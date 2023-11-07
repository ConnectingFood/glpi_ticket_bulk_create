import requests
from requests.auth import HTTPBasicAuth


class BaseGLPIRepository:
    def __init__(
        self, base_glpi_url: str, glpi_app_token: str, glpi_user: str, glpi_pass: str
    ):
        self.BASE_GLPI_URL = base_glpi_url
        self.GLPI_APP_TOKEN = glpi_app_token
        self.GLPI_USER = glpi_user
        self.GLPI_PASS = glpi_pass

        self.session_token = None

    def get_auth_header(self, session=False):
        basic_header = {"App-Token": self.GLPI_APP_TOKEN}
        if session:
            self.get_session_token()
            basic_header["Session-Token"] = self.session_token
        return basic_header

    def __get_basic_auth(self):
        return HTTPBasicAuth(self.GLPI_USER, self.GLPI_PASS)

    def get_session_token(self):
        full_url = f"{self.BASE_GLPI_URL}/initSession"
        result = requests.get(
            full_url, headers=self.get_auth_header(), auth=self.__get_basic_auth()
        )
        self.session_token = result.json().get("session_token")