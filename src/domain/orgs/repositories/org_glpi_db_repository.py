from typing import List

from src.shared.repositories.base_repository import BaseRepository
from src.domain.orgs.models.glpi_org_model import GLPIOrgModel

class OrgGLPIDBRepository(BaseRepository):

    def create_org_plugin_fields(self, glpi_org_model_list: List[GLPIOrgModel], glpi_id_list: List[int]) -> None:

        query = """
        INSERT INTO glpi_cf.glpi_plugin_fields_entitycdigosdecadastros (items_id,
            itemtype,
            plugin_fields_containers_id,
            cdigocffield,
            datacadastrofield,
            plugin_fields_tipodecadastrofielddropdowns_id,
            entidadejfoicadastradanobancodedoaesfield)
        values (%s, %s, %s, %s, %s, %s, %s)
        """

        for glpi_org_model, glpi_id in zip(glpi_org_model_list, glpi_id_list):
            self.execute(query=query, args=[glpi_id, "Entity", 3, glpi_org_model.cdigocffield, glpi_org_model.datacadastrofield, 1, True], commit=True)