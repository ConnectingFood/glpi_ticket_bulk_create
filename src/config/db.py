import pymssql

class DBConnection:
    def __init__(self, server: str, user: str, password: str, database: str) -> None:
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.session = None
        self.cursor = None

    def get_cursor(self):
        if not self.session:
            self.__set_session()
        if not self.cursor:
            self.__set_cursor()
        return self.cursor
    
    def get_session(self):
        if not self.session:
            self.__set_session()
        return self.session
    
    def __set_session(self):
        self.session = pymssql.connect(
            server=self.server,
            user=self.user,
            password=self.password,
            database=self.database,
            as_dict=True
        )

    def __set_cursor(self):
        self.cursor = self.session.cursor()