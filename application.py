import sys

from dependency_injector.wiring import Provide, inject

from src.config import containers
from src.config.containers import Container
from src.domain.tickets.services.tickets_service import TicketService

@inject
def main(service: TicketService = Provide[Container.ticket_service]):

    if len(sys.argv) <= 1:
        print("Necessario informar parametro: relatorio ou criar")
        exit()

    args = sys.argv[1]

    if args == "relatorio":
        service.filter_non_donators("06.057.223/0001-71", month=9, generate_report=True)
    if args == "criar":
        service.ticket_create("06.057.223/0001-71", month=9)

if __name__ == '__main__':
    container = containers.init_app()
    container.wire(modules=[__name__])

    main()