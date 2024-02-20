from enum import Enum

class EntityGLPIFields(Enum):
    CODIGO_CF = (76668, 'cdigocffield')
    NOME = (14, 'name')
    TITULO = (76677, 'titulofield')
    CODIGO_POSTAL = (25, 'postcode')
    CIDADE = (11, 'town')
    ESTADO = (12, 'state')
    LATITUDE = (67, 'latitude')
    LONGITUDE = (68, 'longitude')
    CNPJ = (70, 'registration_number')
    SITE = (4, 'website')
    TELEFONE = (5, 'phonenumber')
    EMAIL_RESPONSAVEL = (6, 'email')
    ENDERECO = (3, 'address')
    ESTA_NO_BANCO = (76699, 'entidadejfoicadastradanobancodedoaesfield')
    DATA_DE_CADASTRO = (76671, 'datacadastrofield')
    TIPO_DE_CADASTRO = (76689, 'completename')