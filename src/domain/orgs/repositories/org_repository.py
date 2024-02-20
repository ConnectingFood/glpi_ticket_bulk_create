from typing import List

from src.shared.repositories.base_repository import BaseRepository
from src.domain.orgs.models.org_model import OrgModel
from src.domain.orgs.models.glpi_org_model import GLPIOrgModel

class OrgRepository(BaseRepository):

    def get_org_list(self,cnpj: str = None) -> List:

        query = """
        SELECT
            e.id,
            e.titulo,
            e.cep,
            e.endereco,
            e.numero,
            e.complemento,
            e.bairro,
            e.cidade,
            e.estado,
            e.latitude,
            e.longitude,
            e.cnpj,
            e.website,
            e.telefone,
            e.email_responsavel
        FROM
            connectingfood02.connectingfood02.entidades e
        """
        self.execute(query=query)
        results = self.fetch()
        return OrgModel.load_list(results)
    
    