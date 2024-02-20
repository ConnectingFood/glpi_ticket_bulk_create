from typing import List
import requests

from src.shared.repositories.base_glpi_repository import BaseGLPIRepository
from src.domain.orgs.models.glpi_org_model import GLPIOrgModel

class OrgGLPIRepository(BaseGLPIRepository):

    def create_ticket(self, ticket_create_model: List[GLPIOrgModel]):
        payload = GLPIOrgModel.bulk_model_dump(ticket_create_model)
        full_url = f"{self.BASE_GLPI_URL}/entity/"
        result = requests.post(full_url, headers=self.get_auth_header(session=True), json={"input": payload})
        return result