from typing import Optional
from datetime import datetime
from pydantic import validator, Field, AliasPath
from src.shared.models.base_model import CustomBaseModel


class GLPIOrgModel(CustomBaseModel):
    
    cdigocffield: Optional[int] = Field(validation_alias=AliasPath('id'))
    titulofield: Optional[str] = Field(validation_alias=AliasPath('titulo'))
    name: Optional[str] = None
    postcode: Optional[str] = Field(validation_alias=AliasPath('cep'))
    town: Optional[str] = Field(validation_alias=AliasPath('cidade'))
    state: Optional[str] = Field(validation_alias=AliasPath('estado'))
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    registration_number: Optional[str] = Field(validation_alias=AliasPath('cnpj'))
    website: Optional[str] = None
    phonenumber: Optional[str] = Field(validation_alias=AliasPath('telefone'))
    email: Optional[str] = Field(validation_alias=AliasPath('email_responsavel'))
    address: Optional[str] = None
    entidadejfoicadastradanobancodedoaesfield: Optional[str] = None
    datacadastrofield: Optional[str] = None
    completename: Optional[str] = None

    @validator("name", always=True)
    def name_validator(cls, value, values):
        return values["titulofield"]