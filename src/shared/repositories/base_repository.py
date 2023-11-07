from typing import Union, Dict, List

from src.config.db import DBConnection


class BaseRepository:
    def __init__(self, connection: DBConnection):
        self.session = connection.get_session()
        self.cursor = connection.get_cursor()

    def _execute_query(self, query: str, commit=False, args=[]) -> None:
        if len(args):
            self.cursor.execute(query, tuple(args))
        else:
            self.cursor.execute(query)
        
        if commit:
            self.session.commit()

    def execute(self, query: str, commit=False, args=[]) -> None:
        self._execute_query(query, commit, args)

    def fetch(self, first=False) -> Union[Dict, List]:
        return self.cursor.fetchone() if first else self.cursor.fetchall()