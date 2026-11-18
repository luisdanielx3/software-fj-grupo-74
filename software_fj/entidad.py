"""
Clase abstracta que representa cualquier entidad general del sistema
(clientes, servicios y reservas). Aporta el identificador unico y obliga
a las clases hijas a implementar describir().
"""

import itertools                    # count(): contador que genera 1, 2, 3, ...
from abc import ABC, abstractmethod  # Herramientas para crear clases abstractas


class EntidadBase(ABC):
    """Clase abstracta: no se puede instanciar directamente."""

    prefijo = "ENT"                  # Prefijo del ID; cada familia de clases define el suyo
    _contador = itertools.count(1)   # Contador propio de la clase base

    def __init_subclass__(cls, **kwargs):
        """Se ejecuta al definir cada subclase: da contador propio a quien declare 'prefijo'."""
        super().__init_subclass__(**kwargs)
        if "prefijo" in cls.__dict__:                # Solo si la clase define su propio prefijo
            cls._contador = itertools.count(1)       # IDs independientes: CLI-001, SRV-001, RES-001

    def __init__(self):
        # Se llama al FINAL del __init__ de cada hija, es decir, solo cuando los datos
        # ya fueron validados; asi un registro fallido no "gasta" un numero de ID.
        self._id = f"{self.prefijo}-{next(self._contador):03d}"

    @property
    def id(self):
        """El ID es de solo lectura (encapsulacion): no tiene setter."""
        return self._id

    @abstractmethod
    def describir(self):
        """Cada entidad debe poder describirse en un texto legible."""

    def __str__(self):
        return self.describir()      # print(objeto) muestra su descripcion

    def __repr__(self):
        # Representacion tecnica: la que se ve al depurar o al imprimir una lista de objetos.
        # Ejemplo: Cliente('CLI-001')
        return f"{self.__class__.__name__}('{self.id}')"
