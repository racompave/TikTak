import itertools
from datetime import datetime
import sirope
import uuid

class Comentario:

    def __init__(self, url: str, autor: str, texto: str):
         self._id = str(uuid.uuid4())
         self._url = url
         self._autor = autor
         self._texto = texto
         self._fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def id(self):
        return self._id
    @property
    def url(self):
        return self._url
    @property
    def autor(self):
        return self._autor

    @property
    def texto(self):
        return self._texto

    @property
    def fecha(self):
        return self._fecha

    """Convierte un objeto Comentario en diccionario para que pueda ser manipulado
    en JavaScript al ser enviado como respuesta JSON"""
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'autor': self.autor,
            'texto': self.texto,
            'fecha': self.fecha
        }

    @staticmethod
    def find(s: sirope.Sirope, id: str) -> "Comentario":
        return s.find_first(Comentario, lambda c: c.id == id)

    @staticmethod
    def findByUrl(s: sirope.Sirope, url: str):
        return s.filter(Comentario, lambda c: c.url == url)

