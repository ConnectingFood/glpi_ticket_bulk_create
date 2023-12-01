import sys

from dependency_injector.wiring import Provide, inject

from src.config import containers
from src.config.containers import Container
from src.domain.tickets.services.tickets_service import TicketService

@inject
def main(service: TicketService = Provide[Container.ticket_service]):

    MODES = ["relatorio", "criar"]

    if len(sys.argv) <= 1:
        print("Necessario informar parametro: relatorio ou criar")
        exit()

    try:
        args = sys.argv[1:]
        mode = args[0]
        client_cnpj = args[1]
        month = args[2]

        if mode not in MODES or month > 12:
            raise Exception
        
    except Exception:
        exit("""Parametros invalidos.
A execucao deve conter os seguintes parametros:
    python application.py <modo> <cnpj cliente com pontuacao> <mes de apuracao>
Modos disponiveis:
    - relatorio: Gera um relatorio com os dados que dos clientes que nao doaram
    - criar: Cria os chamados no glpi para os clientes que nao doaram
        """)

    if mode == "relatorio":
        service.ticket_report(client_cnpj, month=month)
    if mode == "criar":
        service.ticket_create(client_cnpj, month=month)

if __name__ == '__main__':
    container = containers.init_app()
    container.wire(modules=[__name__])
    main()