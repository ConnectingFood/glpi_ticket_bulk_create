from typing import Optional
from src.shared.models.base_model import CustomBaseModel

class CreateTicketModel(CustomBaseModel):
    name: str
    content: str
    itilcategories_id: int # 18
    type: int # 2
    priority: int # 6
    entities_id: int

class CreateTicketFollowUpModel(CustomBaseModel):
    items_id: int
    content: str
    requesttypes_id: int
    status: int
    itemtype: Optional[str] = "Ticket"

class ClientShopModel(CustomBaseModel):
    glpi_entities_id: Optional[int] = None
    titulo: str
    cnpj: str
    codigo_organizacao_cliente: str
    razao_social: str