
import os
from tinydb import TinyDB
from variables import Variables


# Pour fonctionner créer un répertoire 'datas'.
def _data_path(table_name):
    path = Variables.PROJECT_PATH
    return os.path.join(path, Variables.DATABASE_PATH, '{0}.json'.format(table_name))


class Table:
    """ Class d'accès à la table de donnée
        @table_name : string
    """
    def __init__(self, table_name):
        self._name = table_name
        self._db = TinyDB(path=_data_path(table_name),
                          sort_keys=True,
                          indent=4,
                          separators=(',', ': '),
                          encoding="utf-8",
                          ensure_ascii=False)
        self._table_length = len(self._db.all())

    """vide la table"""
    def purge(self):
        self._db.purge()

    """ajouter un objet à la table"""
    def insert(self, obj):
        self._db.insert(obj)

    def insert_obj(self, obj):
        self._db.insert(obj.__repr__())

    """ mise à jour d'un objet en base 
    @value : dict{key: value} to update
    @expression : QueryObject comparission
    """
    def update(self, value, expression):
        self._db.update(value, expression)

    """ mise à jour d'un objet en base si l'objet n'existe pas, c'est un insert 
    @value : dict{key: value} to update
    @expression : QueryObject comparission
        """
    def upsert(self, value, expression):
        self._db.upsert(value, expression)
    """ suppression d'une entrée en base"""
    def remove(self, expresion):
        self._db.remove(expresion)

    """ Cherche un/des objets selon le filtre
    @expression : Query Object Expression
    """
    def find(self, expression):
        return self._db.search(expression)

    """ retourne la list des éléments d'un champ
    @datas : data List
    @ fields_name : string : names of the columns to get"""
    def get_fields(self, datas, fields_name):
        if len(fields_name) < 2:
            return [r[fields_name[0]] for r in datas]

        result = list()
        for row in datas:
            filtred_data = tuple()
            for label in fields_name:
                filtred_data += (row[label],)
            result.append(filtred_data)
        return result

    """Renvoie toutes les entrées de la table"""
    def all(self):
        return self._db.all()
