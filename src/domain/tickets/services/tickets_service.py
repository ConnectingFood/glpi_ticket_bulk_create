from typing import List, Tuple
from datetime import date, timedelta
import pandas

from src.domain.tickets.repositories.ticket_repository import TicketRepository
from src.domain.tickets.repositories.ticket_glpi_repository import TicketGLPIRepository
from src.domain.tickets.models.ticket_model import CreateTicketModel
from src.domain.tickets.models.ticket_model import ClientShopModel


class TicketService:

    def __init__(self, repository: TicketRepository, glpi_repository: TicketGLPIRepository):
        self.repository = repository
        self.glpi_repository = glpi_repository

    def ticket_create(self, client_cnpj: str, **kwargs):
        client_shops_model = self.get_non_donators_by_client_cnpj(client_cnpj, **kwargs)
        list_of_entity_cnpjs = [client_shop_model.cnpj for client_shop_model in client_shops_model]
        list_of_glpi_entity_ids, list_of_glpi_entity_cnpj = self.get_list_entity_id_by_cnpj(list_of_entity_cnpjs)
        for client_shop_model in client_shops_model:
            if client_shop_model.cnpj in list_of_glpi_entity_cnpj:
                glpi_entity_index = list_of_glpi_entity_cnpj.index(client_shop_model.cnpj)
                client_shop_model.glpi_entities_id = list_of_glpi_entity_ids[glpi_entity_index]
        
        filtered_client_shops_model = [client_shop_model for client_shop_model in client_shops_model if not client_shop_model.glpi_entities_id]

        if (len(filtered_client_shops_model)):
            print("Lojas sem cnpj achadas, planilha com report gerada")
            self.generate_report(filtered_client_shops_model)
            return None

        list_create_ticket_model = self.format_create_ticket_model(client_shops_model, **kwargs)

        self.glpi_repository.create_ticket(list_create_ticket_model)

    def filter_non_donators(self, client_cnpj, generate_report = False, **kwargs):
        client_shops_model = self.get_non_donators_by_client_cnpj(client_cnpj, **kwargs)
        list_of_entity_cnpjs = [client_shop_model.cnpj for client_shop_model in client_shops_model]
        list_of_glpi_entity_ids, list_of_glpi_entity_cnpj = self.get_list_entity_id_by_cnpj(list_of_entity_cnpjs)
        for client_shop_model in client_shops_model:
            if client_shop_model.cnpj in list_of_glpi_entity_cnpj:
                glpi_entity_index = list_of_glpi_entity_cnpj.index(client_shop_model.cnpj)
                client_shop_model.glpi_entities_id = list_of_glpi_entity_ids[glpi_entity_index]
        
        filtered_client_shops_model = [client_shop_model for client_shop_model in client_shops_model if not client_shop_model.glpi_entities_id]

        if generate_report:
            self.generate_report(client_shops_model)
        
        return filtered_client_shops_model

    def get_non_donators_by_client_cnpj(self, client_cnpj: str, month=None, year=None) -> List[ClientShopModel]:
        today = date.today()
        month = (today.replace(day=1) - timedelta(days=1)).strftime("%m") if not month else month
        year = today.strftime("%Y") if not year else year

        non_donators = self.repository.get_non_donators_by_client_cnpj(client_cnpj=client_cnpj, month=month, year=year)
        return non_donators
    
    def get_list_entity_id_by_cnpj(self, list_cnpj: List[str]) -> Tuple[List[int],List[str]]:
        entity_ids = self.glpi_repository.get_entity_id_by_cnpj(list_cnpj=list_cnpj)
        return entity_ids
    
    def generate_report(self, client_shops_model):
        client_shops_dict = ClientShopModel.bulk_model_dump(client_shops_model)
        df = pandas.DataFrame(client_shops_dict)
        df.to_excel("relatorio.xlsx")

    def format_create_ticket_model(self, client_shops_model: List[ClientShopModel], month: int = None, year: int = None) -> List[CreateTicketModel]:
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