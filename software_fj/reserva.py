"""
Clase Reserva: integra cliente, servicio, duracion y estado.
Implementa confirmar, cancelar y procesar con manejo de excepciones:
  - try / except / else / finally
  - encadenamiento de excepciones (raise ... from ...)
  - registro de cada evento y error en el archivo de logs
"""

from enum import Enum

from .cliente import Cliente
from .entidad import EntidadBase
from .excepciones import (
    ErrorSoftwareFJ,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from .registro import obtener_logger
from .servicios import Servicio

log = obtener_logger()                           # Logger compartido por toda la aplicacion


class EstadoReserva(Enum):
    """Los unicos estados validos de una reserva."""
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    PROCESADA = "Procesada"
    CANCELADA = "Cancelada"


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente."""

    prefijo = "RES"

    def __init__(self, cliente, servicio, horas):
        # 1) Parametros obligatorios
        if cliente is None or servicio is None or horas is None:
            raise ParametroFaltanteError("Una reserva requiere cliente, servicio y duracion (horas).")

        # 2) Tipos correctos
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("El cliente de la reserva no es un objeto Cliente valido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("El servicio de la reserva no es un objeto Servicio valido.")

        # 3) El servicio debe estar disponible
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no esta disponible.")

        # 4) La duracion la valida el propio servicio (polimorfismo). Si falla, se ENCADENA
        #    la excepcion original dentro de una ReservaInvalidaError con 'raise ... from ...'
        try:
            servicio.validar_parametros(horas)
        except ErrorSoftwareFJ as error_original:
            raise ReservaInvalidaError(
                f"No se pudo crear la reserva de '{servicio.nombre}': {error_original}"
            ) from error_original

        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = EstadoReserva.PENDIENTE
        self._costo_final = None                 # Se calcula al procesar
        super().__init__()                       # ID solo si todo fue valido

    # ---------- Propiedades de solo lectura ----------
    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def horas(self):
        return self._horas

    @property
    def estado(self):
        return self._estado

    @property
    def costo_final(self):
        return self._costo_final

    # ---------- Operaciones ----------
    def confirmar(self):
        """Pendiente -> Confirmada. Demuestra try / except / else / finally."""
        try:
            if self._estado is not EstadoReserva.PENDIENTE:          # Solo se confirma lo pendiente
                raise OperacionNoPermitidaError(
                    f"{self.id}: no se puede confirmar una reserva en estado {self._estado.value}."
                )
            if not self._servicio.disponible:                        # El servicio pudo cambiar de estado
                raise ServicioNoDisponibleError(f"El servicio '{self._servicio.nombre}' ya no esta disponible.")
        except ErrorSoftwareFJ as error:
            log.error("CONFIRMAR fallido | %s", error)               # Se registra el error...
            raise                                                    # ...y se vuelve a lanzar al llamador
        else:
            self._estado = EstadoReserva.CONFIRMADA                  # Solo se ejecuta si NO hubo error
            log.info("CONFIRMAR exitoso | %s", self.id)
        finally:
            log.debug("CONFIRMAR intento finalizado | %s", self.id)  # Se ejecuta SIEMPRE

    def cancelar(self, motivo="Sin motivo indicado"):
        """Cancela la reserva si aun no fue procesada ni cancelada."""
        try:
            if self._estado in (EstadoReserva.PROCESADA, EstadoReserva.CANCELADA):
                raise OperacionNoPermitidaError(
                    f"{self.id}: no se puede cancelar una reserva {self._estado.value.lower()}."
                )
        except OperacionNoPermitidaError as error:
            log.error("CANCELAR fallido | %s", error)
            raise
        else:
            self._estado = EstadoReserva.CANCELADA
            log.info("CANCELAR exitoso | %s | motivo: %s", self.id, motivo)
        finally:
            log.debug("CANCELAR intento finalizado | %s", self.id)

    def procesar(self, impuesto=None, descuento=0.0):
        """
        Confirmada -> Procesada: calcula el costo definitivo.
        Sobrecarga simulada:
            procesar()                      -> solo con el IVA por defecto
            procesar(impuesto)              -> con un impuesto especifico
            procesar(impuesto, descuento)   -> con impuesto y descuento
        """
        if impuesto is None:                                         # Si no se indica, se usa el IVA estandar
            impuesto = Servicio.IVA_POR_DEFECTO
        try:
            if self._estado is not EstadoReserva.CONFIRMADA:         # Solo se procesa lo confirmado
                raise OperacionNoPermitidaError(
                    f"{self.id}: solo se procesan reservas confirmadas (estado actual: {self._estado.value})."
                )
            costo = self._servicio.calcular_costo(self._horas, impuesto, descuento)
        except ErrorSoftwareFJ as error_original:
            log.error("PROCESAR fallido | %s | %s", self.id, error_original)
            # Excepcion encadenada: el error de calculo queda como 'causa' del error de operacion
            raise OperacionNoPermitidaError(
                f"{self.id}: no fue posible procesar la reserva ({error_original})."
            ) from error_original
        else:
            self._costo_final = costo
            self._estado = EstadoReserva.PROCESADA
            log.info("PROCESAR exitoso | %s | costo final: $%s", self.id, f"{costo:,.2f}")
            return costo
        finally:
            log.debug("PROCESAR intento finalizado | %s", self.id)

    def resumen(self):
        """Devuelve un texto de varias lineas con todos los datos de la reserva."""
        costo = f"${self._costo_final:,.2f}" if self._costo_final is not None else "pendiente de calcular"
        return (
            f"Reserva {self.id}\n"
            f"  Cliente  : {self._cliente.nombre} ({self._cliente.id})\n"
            f"  Servicio : {self._servicio.nombre} ({self._servicio.id})\n"
            f"  Duracion : {self._horas} horas\n"
            f"  Estado   : {self._estado.value}\n"
            f"  Costo    : {costo}"
        )

    def describir(self):
        costo = f" | costo final ${self._costo_final:,.2f}" if self._costo_final is not None else ""
        return (f"[{self.id}] {self._cliente.nombre} -> {self._servicio.nombre} | "
                f"{self._horas} h | {self._estado.value}{costo}")
