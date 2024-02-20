from typing import Optional

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