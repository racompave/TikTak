from datetime import datetime

import sirope

from . import Comentario

class Video:
    def __init__(self, url: str, autor: str, descripcion: str, categoria: str):
        self._url = url
        self._autor = autor
        self._visualizaciones = 0
        self._likedBy = []
        self._ncomentarios = 0
        self._descripcion = descripcion
        self._categoria = categoria
        self._time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def url(self):
        return self._url

    @property
    def autor(self):
        return self._autor

    @property
    def visualizaciones(self):
        return self._visualizaciones

    @property
    def likedBy(self):
        return self._likedBy

    @property
    def nlikes(self):
        return len(self._likedBy)

    @property
    def ncomentarios(self):
        return self._ncomentarios

    @ncomentarios.setter
    def ncomentarios(self, valor):
        self._ncomentarios = valor
    @property
    def descripcion(self):
        return self._descripcion

    @property
    def categoria(self):
        return self._categoria

    @property
    def time(self):
        return self._time

    def addVisualizacion(self):
        self._visualizaciones += 1

    def addLike(self, email):
        self._likedBy.append(email)

    def removeLike(self, email):
        self._likedBy.remove(email)

    @staticmethod
    def find(s: sirope.Sirope, url: str) -> "Video":
        return s.find_first(Video, lambda v: v.url == url)

    @staticmethod
    def findVideosAutor(s: sirope.Sirope, autor: str):
        return s.filter(Video, lambda v: v.autor == autor)

    @staticmethod
    def findByLike(s: sirope.Sirope, email: str):
        return s.filter(Video, lambda v: email in v.likedBy)

    @staticmethod
    def findVideos(s: sirope.Sirope, autor: str, visualizaciones: str,
                   likes: str, comentarios: str, fecha: str, categoria: str):
        if autor == "" and fecha == "" and categoria == "":
            return s.filter(Video, lambda v: v.visualizaciones >= int(visualizaciones) and v.nlikes >= int(likes) and v.ncomentarios >= int(comentarios))
        elif autor == "" and fecha == "":
            return s.filter(Video, lambda v: v.visualizaciones >= int(visualizaciones) and v.nlikes >= int(likes) and v.ncomentarios >= int(comentarios) and v.categoria == categoria)
        elif autor == "" and categoria == "":
            return s.filter(Video, lambda v: v.visualizaciones >= int(visualizaciones) and v.nlikes >= int(likes) and v.ncomentarios >= int(comentarios) and v.time >= fecha)
        elif fecha == "" and categoria == "":
            return s.filter(Video, lambda v: v.autor == autor and v.visualizaciones >= int(visualizaciones) and v.nlikes >= int(likes) and v.ncomentarios >= int(comentarios))
        elif autor == "":
            return s.filter(Video, lambda v: v.visualizaciones >= int(visualizaciones) and v.nlikes >= int(likes) and v.ncomentarios >= int(comentarios) and v.time >= fecha and v.categoria == categoria)
        elif fecha == "":
            return s.filter(Video, lambda v: v.autor == autor and v.visualizaciones >= int(visualizaciones) and v.nlikes >= int(likes) and v.ncomentarios >= int(comentarios) and v.categoria == categoria)
        elif categoria == "":
            return s.filter(Video, lambda v: v.autor == autor and v.visualizaciones >= int(visualizaciones) and v.nlikes >= int(likes) and v.ncomentarios >= int(comentarios) and v.time >= fecha)
        else:
            return s.filter(Video, lambda v: v.autor == autor and v.visualizaciones >= int(visualizaciones) and v.nlikes >= int(likes) and v.ncomentarios >= int(comentarios) and v.time >= fecha and v.categoria == categoria)







