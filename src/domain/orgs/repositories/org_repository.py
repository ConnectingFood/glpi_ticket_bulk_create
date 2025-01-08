from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta

from src.shared.repositories.base_repository import BaseRepository
from src.domain.orgs.models.org_model import (
    OrgModel,
    OrgRenovationEmailModel,
    OrgShopModel
)


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

    def get_current_month(self):
        query = """
            select max(data) data
            from connectingfood02.coletas col left join connectingfood02.empresas emp on col.empresa_id=emp.id
            where emp.cliente_id=1
        """
        self.execute(query=query)
        results = self.fetch()
        return results[0].get("data").replace(day=1)
    
    def update_email_renovation_due_date(self, entidade_id: int, message_id: str, ticket_id: str, due_date: datetime):
        query = """
            insert into dbo.emailrenovacao(vencimento, id_ticket, id_mensagem, entidade_id, data_envio_email)
            values (%s, %s, %s, %s, %s)
        """
        self.execute(
            query=query,
            args=[
                due_date.strftime("%Y-%m-%d"),
                ticket_id,
                message_id,
                entidade_id,
                datetime.now().strftime("%Y-%m-%d")
            ],
            commit=True
        )

    
    def filter_entity_by_send_email(self, entity_id_date_list: List[tuple[int, str]]) -> List[int]:
        
        results = []
        for entity in entity_id_date_list:
            query = f"""
                select 
                    entidade_id
                from 
                    dbo.emailrenovacao
                where
                    entidade_id = %s
                    and vencimento = %s
            """

            self.execute(query=query, args=entity)
            result = self.fetch()
            results += result
        return list(map(lambda x: x.get("entidade_id"), results))
    
    def get_org_to_send_email(self) -> List[OrgRenovationEmailModel]:
        query = """
        select 
            distinct (ent.cnpj),
            ent.id,
            ent.titulo,
            ent.razao_social,
            ent.data_vencimento
        from connectingfood02.coletas col 
            left join connectingfood02.empresas emp on 
                col.empresa_id=emp.id 
            left join connectingfood02.entidades ent on 
                col.entidade_id=ent.id
        where
            month(col.data) = (
                select
                    month(max(distinct(col.data)))
                from connectingfood02.coletas col
                    left join connectingfood02.empresas emp on
                        col.empresa_id=emp.id
                where emp.cliente_id=1
            )
            and year(col.data)=(
                select year(max(distinct(col.data)))
                from connectingfood02.coletas col
                    left join connectingfood02.empresas emp on
                        col.empresa_id=emp.id
                where emp.cliente_id=1
            )
            and emp.cliente_id=1
            and emp.cd_status=1
            and ent.data_vencimento>=GETDATE()
            and ent.data_vencimento<=GETDATE()+45
        order by ent.data_vencimento
        """
        self.execute(query=query)
        results = self.fetch()
        last_valid_date = self.get_current_month()
        results = map(lambda x: {**x, "last_valid_date": last_valid_date}, results)
        return OrgRenovationEmailModel.load_list(results)
    
    def get_osc_relations(self, org_renovation_model_list: List[OrgRenovationEmailModel]) -> List[OrgShopModel]:
        last_valid_date = org_renovation_model_list[0].last_valid_date
        entity_id_list = list(map(lambda x: x.id, org_renovation_model_list))
        query = f"""
        select 
            col.entidade_id as entity_id,
            col.data,
            col.data_entrada,
            col.data_saida,
            emp.codigo_organizacao_cliente,
            emp.razao_social
        from 
            connectingfood02.coletas col 
                left join connectingfood02.empresas emp on 
                    col.empresa_id=emp.id
        where 
            data between %s and %s
        and emp.cd_status=1
        and emp.cliente_id=1
        and entidade_id in ({self.get_arg_string(len(entity_id_list))})
        """
        first_valid_date_string = (last_valid_date - relativedelta(months=3)).strftime("%Y-%m-%d")
        last_valid_date_string = (last_valid_date + relativedelta(months=+1, seconds=-1)).strftime("%Y-%m-%d")
        self.execute(query=query, args=[first_valid_date_string, last_valid_date_string, *entity_id_list])
        results = self.fetch()
        return OrgShopModel.load_list(results)