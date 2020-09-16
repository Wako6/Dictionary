from threading import Thread, RLock
from .storage import Table

lock = RLock()


class UnitexSearch(Thread):

    def __init__(self, table_name: str, expression, collector: list):
        Thread.__init__(self)

        self.table_name = table_name
        self.expression = expression
        self.collector = collector

    def run(self):
        """Code à exécuter pendant l'exécution du thread."""

        bdd = Table(self.table_name)
        result = bdd._db.search(self.expression)

        with lock:
            self.collector += result
