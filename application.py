import sys

from dependency_injector.wiring import Provide, inject

from src.config import containers
from src.config.containers import Container
from src.domain.tickets.services.tickets_service import TicketService
from src.domain.orgs.services.org_service import OrgService


@inject
def main(service: TicketService = Provide[Container.ticket_service], org_service: OrgService = Provide[Container.org_service]):

    MODES = ["relatorio", "criar", "sync_osc", "relatorio_sync", "email_renovacao"]

    if len(sys.argv) <= 1:
        print("Necessario informar parametro: relatorio ou criar")
        exit()

    try:
        args = sys.argv[1:]
        mode = args[0]
        if mode not in MODES:
            raise Exception
        
        if mode in ["relatorio", "criar"]:
            client_cnpj = args[1]
            month = int(args[2])
            year = int(args[3])

            if month > 12:
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
        service.ticket_report(client_cnpj, month=month, year=year)
    if mode == "criar":
        service.ticket_create(client_cnpj, month=month, year=year)
    if mode == "sync_osc":
        org_service.sync_glpi_with_db()
    if mode == "relatorio_sync":
        org_service.orgs_glpi_report()
    if mode == "email_renovacao":
        org_service.send_renovation_email()

if __name__ == '__main__':
    container = containers.init_app()
    container.wire(modules=[__name__])
    main()