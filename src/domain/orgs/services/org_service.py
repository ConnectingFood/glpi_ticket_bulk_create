from typing import List
from datetime import datetime
from logging import Logger
import pandas

from src.domain.orgs.repositories.org_repository import OrgRepository
from src.domain.orgs.repositories.org_glpi_db_repository import OrgGLPIDBRepository
from src.domain.orgs.models.org_model import OrgModel
from src.domain.orgs.models.glpi_org_model import GLPIOrgModel
from src.domain.tickets.repositories.ticket_glpi_repository import TicketGLPIRepository


class OrgService:

    def __init__(self, repository: OrgRepository, glpi_repository: TicketGLPIRepository, org_glpi_db_repository: OrgGLPIDBRepository, logger: Logger):
        self.repository = repository
        self.glpi_repository = glpi_repository
        self.org_glpi_db_repository = org_glpi_db_repository
        self.logger = logger
        self.CHUNK_SIZE = 30

    def __divide_chunks(self, list_to_divide: List[any], chunck_size: int):
        for i in range(0, len(list_to_divide), chunck_size):
            yield list_to_divide[i:i + chunck_size]

    def orgs_glpi_report(self) -> None:
        self.logger.debug(f"Iniciando Rotina relatorio sync osc.")

        self.logger.debug(f"Consultando lista de OSCs no GLPI.")
        glpi_org_list = self.glpi_repository.get_entity_list()
        
        self.logger.debug(f"Buscando OSCs no banco de dados.")
        org_model_list = self.repository.get_org_list()

        org_cnpj_list = [org_model.cnpj for org_model in org_model_list]

        org_only_glpi_fitered_list = list(filter(lambda x: x.get("cnpj") and x.get("cnpj") not in org_cnpj_list, glpi_org_list[0]))

        self.logger.debug(f"Gerando relatorio com {len(org_only_glpi_fitered_list)} OSCs.")
        self.__generate_report__(org_only_glpi_fitered_list)

    def __generate_report__(self, glpi_org_dict) -> None:
        df = pandas.DataFrame(glpi_org_dict)
        
        report_name = "OSCs_nao_presentes_no_banco_relatorio.xlsx"
        df.to_excel(report_name)
        self.logger.debug(f"Relatorio gerado com nome de {report_name}.")

    def sync_glpi_with_db(self) -> None:
        self.logger.debug(f"Buscando OSCs no banco de dados.")
        orgs = self.repository.get_org_list()
        
        orgs_with_cnpj = list(filter(lambda x: x.cnpj != '', orgs))
        orgs_cnpj_list = [org.cnpj for org in orgs_with_cnpj]

        chunks_of_list_create_ticket_model = self.__divide_chunks(list_to_divide=orgs_cnpj_list, chunck_size=self.CHUNK_SIZE)
        
        self.logger.debug(f"Consultando lista de OSCs no GLPI.")
        list_of_glpi_entity_cnpj = []
        for chunk in chunks_of_list_create_ticket_model:
            entity_ids = self.glpi_repository.get_entity_id_by_cnpj(chunk)
            list_of_glpi_entity_cnpj += entity_ids[1]

        to_create = []
        for org in orgs_with_cnpj:
            if org.cnpj not in list_of_glpi_entity_cnpj:
                to_create.append(org)

        self.logger.debug(f"Encontrado um total de {len(to_create)} OSC para criar no GLPI.")

        if(len(to_create)):
            self.__create_orgs__(to_create)
            return None
        
    def __create_orgs__(self, org_models: List[OrgModel]):
        
        glpi_org_model_list = []

        for org_model in org_models:
            org_model.titulo = f"{org_model.titulo}|{org_model.cnpj}"
            glpi_org_model_list.append(GLPIOrgModel(
                **org_model.model_dump(),
                address = f" {org_model.endereco  or ''}, {org_model.numero  or ''}, {org_model.complemento  or ''}, {org_model.cep or ''}, {org_model.bairro  or ''}, {org_model.cidade  or ''}, {org_model.estado  or ''}",
                entidadejfoicadastradanobancodedoaesfield = "Sim",
                datacadastrofield = str(datetime.now()),
                completename = "OSC",
            ))
        
        self.logger.debug(f"Criando OSCs no GLPI.")
        glpi_id_list = self.glpi_repository.create_org(glpi_org_model_list)
        glpi_id_list = list(map(lambda x: x.get("id"), glpi_id_list.json()))
        self.org_glpi_db_repository.create_org_plugin_fields(glpi_org_model_list, glpi_id_list)
