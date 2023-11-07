from typing import List

from src.shared.repositories.base_repository import BaseRepository
from src.domain.tickets.models.ticket_model import ClientShopModel


class TicketRepository(BaseRepository):
    
    def get_non_donators_by_client_cnpj(self, client_cnpj: str, month=None, year=None) -> List:
        query = """
            select 
                cl.titulo,
                e.cnpj,
                e.codigo_organizacao_cliente,
                e.razao_social
            from connectingfood02.coletas c 
            left join connectingfood02.coleta_alimentos ca on 
                c.id=ca.coleta_id
            left join connectingfood02.empresas e on
                e.id = c.empresa_id
            left join connectingfood02.parcerias p on
                p.id = c.empresa_id
            left join connectingfood02.clientes cl on
                cl.id = e.cliente_id
            where 
                month(c.data) = %s and 
                year(c.data)= %s and
                cl.cnpj = %s and
                e.razao_social not like '%Teste%'
            group by c.empresa_id, e.codigo_organizacao_cliente, cl.titulo, e.cnpj, e.razao_social
            having(sum(quantidade) is null)
        """

        self.execute(query=query, args=[month, year, client_cnpj])
        results = self.fetch()
        return ClientShopModel.load_list(results)