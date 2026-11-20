"""
Clase abstracta Servicio y tres servicios especializados:
  - ReservaSala
  - AlquilerEquipo
  - AsesoriaEspecializada

Cada servicio sobrescribe (polimorfismo): validar_parametros, calcular_costo y describir.
calcular_costo esta "sobrecargado" mediante parametros opcionales: se puede llamar
con (horas), con (horas, impuesto) o con (horas, impuesto, descuento).
"""

from abc import ABC, abstractmethod

from .entidad import EntidadBase
from .excepciones import (
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
)


def _es_numero(valor):
    """True si es int o float (se excluye bool, porque True/False no son cantidades)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


class Servicio(EntidadBase, ABC):
    """Clase abstracta: define lo que TODO servicio debe saber hacer."""

    prefijo = "SRV"
    IVA_POR_DEFECTO = 0.19            # 19 % de IVA, usado cuando no se indica otro impuesto

    def __init__(self, nombre, tarifa_hora, disponible=True):
        if nombre is None or tarifa_hora is None:                    # Faltan datos obligatorios
            raise ParametroFaltanteError("El servicio requiere nombre y tarifa por hora.")
        if not isinstance(nombre, str) or not nombre.strip():        # Nombre invalido
            raise ServicioInvalidoError("El nombre del servicio debe ser un texto no vacio.")
        if not _es_numero(tarifa_hora) or tarifa_hora <= 0:          # Tarifa invalida
            raise ServicioInvalidoError(f"La tarifa por hora debe ser un numero positivo (recibido: {tarifa_hora!r}).")
        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)
        super().__init__()                                           # ID solo si todo fue valido

    # ---------- Propiedades ----------
    @property
    def nombre(self):
        # Solo lectura: el nombre no se puede cambiar una vez creado el servicio.
        return self._nombre

    @property
    def tarifa_hora(self):
        # Solo lectura: devuelve el valor de una hora de servicio.
        return self._tarifa_hora

    @property
    def disponible(self):
        # Indica si el servicio se puede reservar en este momento.
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        # Permite activar o desactivar el servicio; bool() lo convierte a True/False.
        self._disponible = bool(valor)

    # ---------- Metodos abstractos: cada servicio hijo DEBE sobrescribirlos ----------
    @abstractmethod
    def validar_parametros(self, horas):
        """Lanza ServicioInvalidoError si la duracion no es valida para este servicio."""

    @abstractmethod
    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        """Calcula el costo total. Sobrecarga simulada con impuesto y descuento opcionales."""

    # ---------- Utilidad compartida por los hijos ----------
    def _validar_horas_basico(self, horas, minimo, maximo):
        """Validacion comun de la duracion; cada hijo fija sus propios limites."""
        if horas is None:
            raise ParametroFaltanteError("Falta indicar la duracion (horas).")
        if not _es_numero(horas):
            raise ServicioInvalidoError(f"La duracion debe ser numerica (recibido: {horas!r}).")
        if not (minimo <= horas <= maximo):
            raise ServicioInvalidoError(
                f"{self.nombre}: la duracion debe estar entre {minimo} y {maximo} horas (recibido: {horas})."
            )

    def _aplicar_ajustes(self, subtotal, impuesto, descuento):
        """Aplica descuento e impuesto al subtotal y verifica que el resultado sea coherente."""
        if not _es_numero(impuesto) or not (0 <= impuesto <= 0.30):
            raise CalculoInconsistenteError(f"Impuesto fuera de rango (0 a 0.30): {impuesto!r}.")
        if not _es_numero(descuento) or not (0 <= descuento <= 0.50):
            raise CalculoInconsistenteError(f"Descuento fuera de rango (0 a 0.50): {descuento!r}.")
        total = subtotal * (1 - descuento) * (1 + impuesto)          # Primero descuento, luego impuesto
        if total <= 0:                                               # Un costo nunca puede ser cero o negativo
            raise CalculoInconsistenteError(f"El calculo produjo un costo invalido: {total}.")
        return round(total, 2)


class ReservaSala(Servicio):
    """Reserva de una sala de reuniones por horas."""

    def __init__(self, nombre_sala, tarifa_hora, capacidad, disponible=True):
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad < 1:
            raise ServicioInvalidoError(f"La capacidad debe ser un entero positivo (recibido: {capacidad!r}).")
        self._capacidad = capacidad                                  # Personas que caben en la sala
        super().__init__(nombre_sala, tarifa_hora, disponible)       # Valida nombre y tarifa

    @property
    def capacidad(self):
        # Solo lectura: cantidad maxima de personas que caben en la sala.
        return self._capacidad

    def validar_parametros(self, horas):
        self._validar_horas_basico(horas, 1, 8)                      # Una sala se reserva de 1 a 8 horas

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        self.validar_parametros(horas)
        subtotal = self.tarifa_hora * horas                          # Tarifa x horas
        return self._aplicar_ajustes(subtotal, impuesto, descuento)

    def describir(self):
        estado = "disponible" if self.disponible else "NO disponible"
        return (f"[{self.id}] Sala '{self.nombre}' | capacidad {self.capacidad} personas | "
                f"${self.tarifa_hora:,.0f}/hora | {estado}")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos (portatiles, proyectores...) con deposito fijo."""

    def __init__(self, nombre_equipo, tarifa_hora, cantidad, deposito=0.0, disponible=True):
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 1:
            raise ServicioInvalidoError(f"La cantidad de equipos debe ser un entero positivo (recibido: {cantidad!r}).")
        if not _es_numero(deposito) or deposito < 0:
            raise ServicioInvalidoError(f"El deposito no puede ser negativo (recibido: {deposito!r}).")
        self._cantidad = cantidad
        self._deposito = float(deposito)
        super().__init__(nombre_equipo, tarifa_hora, disponible)

    @property
    def cantidad(self):
        # Solo lectura: cuantas unidades del equipo se alquilan.
        return self._cantidad

    def validar_parametros(self, horas):
        self._validar_horas_basico(horas, 1, 72)                     # Un equipo se alquila hasta 72 horas

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        self.validar_parametros(horas)
        subtotal = self.tarifa_hora * horas * self.cantidad + self._deposito
        return self._aplicar_ajustes(subtotal, impuesto, descuento)

    def describir(self):
        estado = "disponible" if self.disponible else "NO disponible"
        return (f"[{self.id}] Equipo '{self.nombre}' x{self.cantidad} | "
                f"${self.tarifa_hora:,.0f}/hora c/u | deposito ${self._deposito:,.0f} | {estado}")


class AsesoriaEspecializada(Servicio):
    """Asesoria con un experto; el nivel senior cuesta 50 % mas."""

    NIVELES = {"junior": 1.0, "senior": 1.5}                         # Multiplicador por nivel

    def __init__(self, especialidad, tarifa_hora, nivel="junior", disponible=True):
        if not isinstance(nivel, str) or nivel.lower() not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel invalido: {nivel!r}. Opciones: {', '.join(self.NIVELES)}.")
        self._nivel = nivel.lower()
        super().__init__(especialidad, tarifa_hora, disponible)

    @property
    def nivel(self):
        # Solo lectura: "junior" o "senior".
        return self._nivel

    def validar_parametros(self, horas):
        self._validar_horas_basico(horas, 1, 4)                      # Una asesoria dura de 1 a 4 horas

    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        self.validar_parametros(horas)
        subtotal = self.tarifa_hora * horas * self.NIVELES[self._nivel]
        return self._aplicar_ajustes(subtotal, impuesto, descuento)

    def describir(self):
        estado = "disponible" if self.disponible else "NO disponible"
        return (f"[{self.id}] Asesoria en '{self.nombre}' (nivel {self.nivel}) | "
                f"${self.tarifa_hora:,.0f}/hora | {estado}")
