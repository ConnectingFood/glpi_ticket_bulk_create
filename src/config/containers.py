from dependency_injector import containers, providers
import os
from dotenv import dotenv_values

from src.domain.tickets.repositories.ticket_repository import TicketRepository
from src.domain.tickets.repositories.ticket_glpi_repository import TicketGLPIRepository
from src.domain.tickets.services.tickets_service import TicketService
from src.domain.orgs.repositories.org_repository import OrgRepository
from src.domain.orgs.repositories.org_glpi_db_repository import OrgGLPIDBRepository
from src.domain.orgs.services.org_service import OrgService
from src.shared.services.base_logger import BaseLogger
from src.config.db import DBConnection
from src.config.glpi_db import GLPIDBConnection


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    logger = providers.Singleton(
        BaseLogger.get_logger
    )

    db = providers.Singleton(
        DBConnection,
        server=config.SERVER,
        user=config.DB_USER,
        password=config.DB_PASS,
        database=config.DB_NAME
    )
    glpi_db = providers.Singleton(
        GLPIDBConnection,
        server=config.GLPI_DB_SERVER,
        user=config.GLPI_DB_USER,
        password=config.GLPI_DB_PASS,
        database=config.GLPI_DB_NAME
    )

    ticket_glpi_repository = providers.Factory(
        TicketGLPIRepository,
        base_glpi_url=config.BASE_GLPI_URL,
        glpi_app_token=config.GLPI_APP_TOKEN,
        glpi_user=config.GLPI_USER,
        glpi_pass=config.GLPI_PASS,
    )

    ticket_repository = providers.Factory(
        TicketRepository,
        connection=db
    )
    
    ticket_service = providers.Factory(
        TicketService,
        repository=ticket_repository,
        glpi_repository=ticket_glpi_repository,
        logger=logger
    )

    org_repository = providers.Factory(
        OrgRepository,
        connection=db
    )
    
    org_glpi_db_repository = providers.Factory(
        OrgGLPIDBRepository,
        connection=glpi_db
    )
    
    org_service = providers.Factory(
        OrgService,
        repository=org_repository,
        glpi_repository=ticket_glpi_repository,
        org_glpi_db_repository=org_glpi_db_repository,
        logger=logger
    )

def init_app() -> Container:
    container = Container()
    config = {**dotenv_values(), **os.environ}
    for key in config.keys():
        config_attr = getattr(container.config,key)
        config_attr.from_env(key)
    
    return container