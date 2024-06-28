from typing import List, Tuple, Union
from datetime import datetime
from http.client import HTTPMessage
from logging import Logger
import pandas
from jinja2 import Environment, PackageLoader, select_autoescape, Template

from src.domain.orgs.repositories.org_repository import OrgRepository
from src.domain.orgs.repositories.org_glpi_db_repository import OrgGLPIDBRepository
from src.domain.orgs.models.org_model import (
    OrgModel,
    OrgRenovationEmailModel,
    OrgShopModel
)
from src.domain.orgs.models.glpi_org_model import GLPIOrgModel
from src.domain.tickets.repositories.ticket_glpi_repository import TicketGLPIRepository
from src.shared.services.sendgrid_service import SendgridService
from src.shared.models.sendgrid_attachment_model import AttachmentModel
from src.domain.tickets.models.ticket_model import CreateTicketModel


class OrgService:

    def __init__(self, repository: OrgRepository, glpi_repository: TicketGLPIRepository, org_glpi_db_repository: OrgGLPIDBRepository, sendgrid_service: SendgridService, logger: Logger):
        self.repository = repository
        self.glpi_repository = glpi_repository
        self.sendgrid_service = sendgrid_service
        self.org_glpi_db_repository = org_glpi_db_repository
        self.logger = logger
        self.CHUNK_SIZE = 30
        self.jinja_env = Environment(
            loader=PackageLoader("src.shared"),
            autoescape=select_autoescape()
        )

    def __divide_chunks(self, list_to_divide: List[any], chunck_size: int):
        for i in range(0, len(list_to_divide), chunck_size):
            yield list_to_divide[i:i + chunck_size]

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

    def __generate_report__(self, glpi_org_dict) -> None:
        df = pandas.DataFrame(glpi_org_dict)
        
        report_name = "OSCs_nao_presentes_no_banco_relatorio.xlsx"
        df.to_excel(report_name)
        self.logger.debug(f"Relatorio gerado com nome de {report_name}.")

    def __sanitaze_glpi_emails__(self, list_dirty_emails: List[Tuple[int, str]]) -> List[Tuple[int, Union[list, str]]]:

        list_clean_email = []
        for glpi_id, dirty_email in list_dirty_emails:

            if ";" in dirty_email:
                dirty_email = [email.replace(" ", "") for email in dirty_email.split(";")]
            
            list_clean_email.append((glpi_id, dirty_email))
        return list_clean_email
    
    def format_email_renovation_model(self, target_entities: List[OrgRenovationEmailModel], glpi_org_list: Tuple[List[int], List[str]], clean_emails: List[Union[str, list]]) -> List[OrgRenovationEmailModel]:
        glpi_org_id_list, glpi_org_cnpj_list = glpi_org_list
        for glpi_org_id, glpi_org_cnpj in zip(glpi_org_id_list, glpi_org_cnpj_list):
            entity_model = list(filter(lambda x: x.cnpj == glpi_org_cnpj, target_entities))[0]
            glpi_emails = list(filter(lambda x: x[0] == glpi_org_id, clean_emails))[0]
            entity_model.glpi_id = glpi_org_id
            entity_model.glpi_email = glpi_emails[1]
        return target_entities
    
    def send_renovation_email(self):
        template = self.jinja_env.get_template("email_renovacao_gpa.html")
        attachments = [
            AttachmentModel(file_name="Meu_Portal.pdf", file_path="src/shared/attachments/Meu_Portal.pdf", file_type="application/pdf"), 
            AttachmentModel(file_name="Formulario_de_Cadastro_GPA.docx", file_path="src/shared/attachments/Formulario_de_Cadastro_GPA.docx", file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        ]

        list_org_renovation_email_model = self.get_entity_emails()
        for org_renovation_email_model in list_org_renovation_email_model:
            _, _, sendgrid_headers = self.send_email(org_renovation_email_model, template, attachments)
            self.create_email_renovation_ticket(org_renovation_email_model)
            self.repository.update_email_renovation_due_date(org_renovation_email_model.id, sendgrid_headers.get("X-MESSAGE-ID"), org_renovation_email_model.glpi_ticket_id, org_renovation_email_model.data_vencimento)

    def create_email_renovation_ticket(self, org_renovation_model: OrgRenovationEmailModel) -> None:
        email_renovation_create_ticket_model = self.format_email_renovation_ticket_model(org_renovation_model)
        glpi_ticket_response = self.glpi_repository.create_ticket(email_renovation_create_ticket_model)
        if glpi_ticket_response.status_code != 201:
            print(f"Erro ao criar chamano do glpi -> resposta glpi: {glpi_ticket_response.json()} | create_ticket_model: {email_renovation_create_ticket_model.model_dump()}")
            return None
        org_renovation_model.glpi_ticket_id = glpi_ticket_response.json().get("id")
        return None

    def format_email_renovation_ticket_model(self, org_renovation_model: OrgRenovationEmailModel) -> CreateTicketModel:
        formatted_dict = {
            "name": f"TESTE - Renovação - GPA - [{org_renovation_model.razao_social} - {org_renovation_model.cnpj}] - Vencimento {org_renovation_model.data_vencimento}",
            "content": f"",
            "itilcategories_id": 15,
            "type": 2,
            "priority": 4,
            "entities_id": org_renovation_model.glpi_id
        }
        return CreateTicketModel(**formatted_dict)

    def send_email(self, org_renovation_email_model: OrgRenovationEmailModel, template: Template, attachments: List[AttachmentModel]) -> Tuple[int, str, HTTPMessage]:
        dict_org_renovation_email = org_renovation_email_model.model_dump()
        return self.sendgrid_service.send_email(
            org_renovation_email_model.glpi_email,
            f"terceiro email teste {org_renovation_email_model.id}",
            template.render({"shops" : dict_org_renovation_email.get("shops")}), attachments
        )

    def get_entity_emails(self) -> List[OrgRenovationEmailModel]:
        target_entities = self.repository.get_org_to_send_email()
        target_entities_to_remove = self.repository.filter_entity_by_send_email(list(map(lambda x: [x.id, x.data_vencimento.strftime("%Y-%m-%d")], target_entities)))
        target_entities = list(filter(lambda x: x.id not in target_entities_to_remove, target_entities))
        if len(target_entities) == 0:
            print("sem emails para enviar, saindo")
            exit()
        target_entities = self.load_entity_shops(target_entities)
        target_entities_cnpj = list(map(lambda x: x.cnpj, target_entities))
        glpi_org_id_list, glpi_org_cnpj_list = self.glpi_repository.get_entity_id_by_cnpj(target_entities_cnpj)
        glpi_org_emails = self.glpi_repository.get_entity_email_by_id(glpi_org_id_list)
        clean_emails = self.__sanitaze_glpi_emails__(glpi_org_emails)

        target_entities = self.format_email_renovation_model(target_entities, (glpi_org_id_list, glpi_org_cnpj_list), clean_emails)
        return target_entities

    def load_entity_shops(self, target_entities: List[OrgRenovationEmailModel]) -> List[OrgRenovationEmailModel]:
        target_entities_shop_list = self.repository.get_osc_relations(target_entities)
        for target_entity in target_entities:
            target_entity_shop_list = list(filter(lambda x: x.entity_id == target_entity.id, target_entities_shop_list))
            has_valid_donation = any([x.data_entrada != None and x.data_saida != None for x in target_entity_shop_list])
            if has_valid_donation:
                target_entity_shop_list = list(filter(lambda x: x.data_entrada != None and x.data_saida != None, target_entity_shop_list))
            else:
                target_entity_shop_list = list(filter(lambda x: x.data >= target_entity.last_valid_date, target_entity_shop_list))
            
            unique_shops = set(map(lambda x: x.codigo_organizacao_cliente, target_entity_shop_list))
            filtered_target_entity_shop_list = self.filter_unique_shops(target_entity_shop_list, unique_shops)
            target_entity.shops = filtered_target_entity_shop_list
        
        return target_entities

    def filter_unique_shops(self, entity_shop_list: List[OrgShopModel], unique_shops: List[int]) -> List[OrgShopModel]:
        filtered_unique = []
        already_found = []
        for entity_shop in entity_shop_list:
            if entity_shop.codigo_organizacao_cliente not in already_found and entity_shop.codigo_organizacao_cliente in unique_shops:
                filtered_unique.append(entity_shop)
                already_found.append(entity_shop.codigo_organizacao_cliente)

        return filtered_unique
    
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
            list_of_glpi_entity_cnpj += entity_ids[1] if len(entity_ids) else entity_ids

        to_create = []
        for org in orgs_with_cnpj:
            if org.cnpj not in list_of_glpi_entity_cnpj:
                to_create.append(org)

        self.logger.debug(f"Encontrado um total de {len(to_create)} OSC para criar no GLPI.")

        if(len(to_create)):
            self.__create_orgs__(to_create)
            return None
