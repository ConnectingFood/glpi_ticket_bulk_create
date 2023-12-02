from typing import List, Tuple
from datetime import date, timedelta
from logging import Logger
import pandas

from src.domain.tickets.repositories.ticket_repository import TicketRepository
from src.domain.tickets.repositories.ticket_glpi_repository import TicketGLPIRepository
from src.domain.tickets.models.ticket_model import CreateTicketModel
from src.domain.tickets.models.ticket_model import ClientShopModel


class TicketService:

    def __init__(self, repository: TicketRepository, glpi_repository: TicketGLPIRepository, logger: Logger):
        self.repository = repository
        self.glpi_repository = glpi_repository
        self.logger = logger
        self.CHUNK_SIZE = 30

    def ticket_create(self, client_cnpj: str, **kwargs) -> None:
        self.logger.debug(f"Iniciando rotina 'criar' para {client_cnpj=}.")
        
        client_shops_model = self.__filter_non_donators(client_cnpj, **kwargs)
        filtered_client_shops_model = [client_shop_model for client_shop_model in client_shops_model if not client_shop_model.glpi_entities_id]

        if (len(filtered_client_shops_model)):
            self.logger.debug(f"Lojas sem cnpj achadas, planilha sera report gerada.")
            self.__generate_report(filtered_client_shops_model)
            return None

        list_create_ticket_model = self.__format_create_ticket_model(client_shops_model, **kwargs)
        
        self.logger.debug(f"Iniciando criacao de {len(list_create_ticket_model)} chamados no glpi.")
        self.glpi_repository.create_ticket(list_create_ticket_model)
        self.logger.debug(f"Chamados Criados.")
        return None

    def ticket_report(self, client_cnpj: str, **kwargs) -> None:
        self.logger.debug(f"Iniciando rotina 'relatorio' para {client_cnpj=}.")

        client_shops_model = self.__filter_non_donators(client_cnpj, **kwargs)
        self.logger.debug("Iniciando geracao do relatorio.")
        return self.__generate_report(client_shops_model)

    def __filter_non_donators(self, client_cnpj: str, **kwargs) -> List[ClientShopModel]:
        client_shops_model = self.__get_non_donators_by_client_cnpj(client_cnpj, **kwargs)
        list_of_entity_cnpjs = [client_shop_model.cnpj for client_shop_model in client_shops_model]
        list_of_glpi_entity_ids, list_of_glpi_entity_cnpj = self.__get_list_entity_id_by_cnpj(list_of_entity_cnpjs)
        
        self.logger.debug("Formatando dados encontrados.")

        for client_shop_model in client_shops_model:
            if client_shop_model.cnpj in list_of_glpi_entity_cnpj:
                glpi_entity_index = list_of_glpi_entity_cnpj.index(client_shop_model.cnpj)
                client_shop_model.glpi_entities_id = list_of_glpi_entity_ids[glpi_entity_index]

        return client_shops_model

    def __divide_chunks(self, list_to_divide: List[any], chunck_size: int):
        for i in range(0, len(list_to_divide), chunck_size):
            yield list_to_divide[i:i + chunck_size]

    def __get_non_donators_by_client_cnpj(self, client_cnpj: str, month=None, year=None) -> List[ClientShopModel]:
        self.logger.debug(f"Buscando clientes no banco CF para o {client_cnpj=}.")
        
        today = date.today()
        month = (today.replace(day=1) - timedelta(days=1)).strftime("%m") if not month else month
        year = today.strftime("%Y") if not year else year

        non_donators = self.repository.get_non_donators_by_client_cnpj(client_cnpj=client_cnpj, month=month, year=year)
        self.logger.debug(f"{len(non_donators)} achados.")
        return non_donators
    
    def __get_list_entity_id_by_cnpj(self, list_cnpj: List[str]) -> Tuple[List[int], List[str]]:
        self.logger.debug("Consultando lista de CNPJs no glpi.")
        chunks_of_list_create_ticket_model = self.__divide_chunks(list_to_divide=list_cnpj, chunck_size=self.CHUNK_SIZE)
        list_of_glpi_entity_ids = [] 
        list_of_glpi_entity_cnpj = []
        for chunk in chunks_of_list_create_ticket_model:
            entity_ids = self.glpi_repository.get_entity_id_by_cnpj(list_cnpj=chunk)
            list_of_glpi_entity_ids += entity_ids[0]
            list_of_glpi_entity_cnpj += entity_ids[1]
        return (list_of_glpi_entity_ids, list_of_glpi_entity_cnpj)
    
    def __generate_report(self, client_shops_model) -> None:
        client_shops_dict = ClientShopModel.bulk_model_dump(client_shops_model)
        df = pandas.DataFrame(client_shops_dict)
        
        report_name = "relatorio.xlsx"
        df.to_excel(report_name)
        self.logger.debug(f"Relatorio gerado com nome de {report_name}.")


    def __format_create_ticket_model(self, client_shops_model: List[ClientShopModel], month: int = None, year: int = None) -> List[CreateTicketModel]:
        formatted_list = []
        today = date.today()
        month = (today.replace(day=1) - timedelta(days=1)).strftime("%m") if not month else month
        year = today.strftime("%Y") if not year else year

        for client_shop_model in client_shops_model:
            formatted_dict = {
                "name": f"Não doou - {client_shop_model.titulo} | {client_shop_model.codigo_organizacao_cliente} - {client_shop_model.razao_social}",
                "content": f"Monitoramento de loja que não realizou doação em {month} {year}",
                "itilcategories_id": 18,
                "type": 2,
                "priority": 5,
                "entities_id": client_shop_model.glpi_entities_id
            }
            formatted_list.append(formatted_dict)
        return CreateTicketModel.load_list(formatted_list)