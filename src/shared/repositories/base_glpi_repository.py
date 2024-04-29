import requests
from requests.auth import HTTPBasicAuth


class BaseGLPIRepository:
    def __init__(
        self, base_glpi_url: str, GLPI_APP_TOKEN_NOVO2: str, GLPI_USER_NOVO2: str, GLPI_PASS_NOVO2: str
    ):
        self.BASE_GLPI_URL = base_glpi_url
        self.GLPI_APP_TOKEN_NOVO2 = GLPI_APP_TOKEN_NOVO2
        self.GLPI_USER_NOVO2 = GLPI_USER_NOVO2
        self.GLPI_PASS_NOVO2 = GLPI_PASS_NOVO2

        self.session_token = None

    def get_auth_header(self, session=False):
        basic_header = {"App-Token": self.GLPI_APP_TOKEN_NOVO2}
        if session:
            self.get_session_token()
            basic_header["Session-Token"] = self.session_token
        return basic_header

    def __get_basic_auth(self):
        return HTTPBasicAuth(self.GLPI_USER_NOVO2, self.GLPI_PASS_NOVO2)

    def get_session_token(self):
        full_url = f"{self.BASE_GLPI_URL}/initSession"
        result = requests.get(
            full_url, headers=self.get_auth_header(), auth=self.__get_basic_auth()
        )
        self.session_token = result.json().get("session_token")