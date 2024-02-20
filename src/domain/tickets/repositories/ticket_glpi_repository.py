from typing import List, Dict, Tuple

import requests

from src.shared.repositories.base_glpi_repository import BaseGLPIRepository
from src.domain.tickets.models.ticket_model import CreateTicketModel
from src.domain.orgs.models.glpi_org_model import GLPIOrgModel


class TicketGLPIRepository(BaseGLPIRepository):

    def get_ticket(self, ticketID: str) -> Dict:
        full_url = f"{self.BASE_GLPI_URL}/Ticket/{ticketID}/?expand_dropdowns=true"
        result = requests.get(full_url, headers=self.get_auth_header(session=True))
        return result.json()
    
    def get_entity_id_by_cnpj(self, list_cnpj: List[str]) -> Tuple[List[int],List[str]]:

        filters = {}
        for index, cnpj in enumerate(list_cnpj):
            filters[f"criteria[{index}][field]"] = "70"
            filters[f"criteria[{index}][searchtype]"] =  "equals"
            filters[f"criteria[{index}][value]"] = cnpj

            if index > 0:
                filters[f"criteria[{index}][link]"] = "OR"

        filters["range"]="0-99999"

        full_url = f"{self.BASE_GLPI_URL}/search/entity/"
        result = requests.get(full_url, headers=self.get_auth_header(session=True),params=filters)
        json_result = result.json()

        if json_result['totalcount'] > 0:
            return (list(map(lambda x: x["2"], json_result["data"])), list(map(lambda x: x["70"], json_result["data"])))
        return []
    
    def get_entity_list(self) -> Tuple[List[int], List[str], List[str]]:

        filters = {
            "range": "0-99999",
        }

        full_url = f"{self.BASE_GLPI_URL}/search/entity/"
        result = requests.get(full_url, headers=self.get_auth_header(session=True),params=filters)
        json_result = result.json()

        glpi_result = []
        if json_result['totalcount'] > 0:
            glpi_result.append(
                list(map(lambda x:{
                "id": x["2"],
                "cnpj": x["70"],
                "title": x["76677"],
            }, json_result["data"])))

        return glpi_result
    
    def create_ticket(self, ticket_create_model: List[CreateTicketModel]):
        payload = CreateTicketModel.bulk_model_dump(ticket_create_model)
        full_url = f"{self.BASE_GLPI_URL}/Ticket/"
        result = requests.post(full_url, headers=self.get_auth_header(session=True), json={"input": payload})
        return result
    
    def create_org(self, ticket_create_model: List[GLPIOrgModel]):
        payload = GLPIOrgModel.bulk_model_dump(ticket_create_model)
        full_url = f"{self.BASE_GLPI_URL}/entity/"
        result = requests.post(full_url, headers=self.get_auth_header(session=True), json={"input": payload})
        return result
    