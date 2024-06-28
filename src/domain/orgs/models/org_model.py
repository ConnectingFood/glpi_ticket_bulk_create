from typing import Optional, Union, List
from datetime import datetime
from src.shared.models.base_model import CustomBaseModel


class OrgModel(CustomBaseModel):

    id: int
    cnpj: str
    titulo: Optional[str] = None
    cep: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    website: Optional[str] = None
    telefone: Optional[str] = None
    email_responsavel: Optional[str] = None

class OrgShopModel(CustomBaseModel):
    
    entity_id: int
    razao_social: str
    codigo_organizacao_cliente: str
    data: Optional[datetime] = None
    data_entrada: Optional[datetime] = None
    data_saida: Optional[datetime] = None

class OrgRenovationEmailModel(CustomBaseModel):
    
    glpi_id: Optional[int] = None
    glpi_ticket_id: Optional[int] = None
    glpi_email: Optional[Union[str, list]] = None
    last_valid_date: Optional[datetime] = None
    shops: Optional[List[OrgShopModel]] = []
    id: int
    cnpj: str
    titulo: str
    razao_social: str
    data_vencimento: datetime