"""
SistemaFJ: gestiona las listas internas de clientes, servicios y reservas.

Regla de oro del sistema: NINGUN error puede detener la aplicacion. Por eso
cada operacion publica atrapa las excepciones, las registra en el log y devuelve
None (o False) en lugar de dejar que el programa se caiga.
"""

from .cliente import Cliente
from .excepciones import (
    ClienteInvalidoError,
    ErrorSoftwareFJ,
    ParametroFaltanteError,
    RegistroNoEncontradoError,
    ServicioInvalidoError,
)
from .registro import obtener_logger
from .reserva import Reserva
from .servicios import Servicio

log = obtener_logger()


class SistemaFJ:
    """Controlador principal; guarda todo en listas (sin base de datos)."""

    def __init__(self):
        self._clientes = []                      # Lista de objetos Cliente
        self._servicios = []                     # Lista de objetos Servicio
        self._reservas = []                      # Lista de objetos Reserva
        log.info("Sistema Software FJ iniciado")

    # ---------- Consultas ----------
    @property
    def clientes(self):
        return list(self._clientes)              # Copia: la lista interna queda protegida

    @property
    def servicios(self):
        return list(self._servicios)

    @property
    def reservas(self):
        return list(self._reservas)

    def _buscar(self, lista, id_buscado, nombre):
        """Busca un objeto por ID; si no existe lanza RegistroNoEncontradoError."""
        if id_buscado is None:
            raise ParametroFaltanteError(f"Falta el ID de {nombre}.")
        for elemento in lista:
            if elemento.id == id_buscado:
                return elemento
        raise RegistroNoEncontradoError(f"No existe {nombre} con ID '{id_buscado}'.")

    # ---------- Operaciones seguras ----------
    def registrar_cliente(self, nombre, documento, correo, telefono):
        """Crea y guarda un cliente. Devuelve el Cliente o None si hubo error."""
        try:
            cliente = Cliente(nombre, documento, correo, telefono)
            if any(c.documento == cliente.documento for c in self._clientes):
                raise ClienteInvalidoError(f"Ya existe un cliente con el documento {cliente.documento}.")
        except ErrorSoftwareFJ as error:
            log.error("REGISTRAR CLIENTE fallido | %s", error)
            return None
        else:
            self._clientes.append(cliente)
            log.info("REGISTRAR CLIENTE exitoso | %s", cliente.describir())
            return cliente

    def registrar_servicio(self, clase_servicio, *args, **kwargs):
        """
        Crea un servicio de la clase indicada (ReservaSala, AlquilerEquipo...).
        Los argumentos se pasan tal cual al constructor de esa clase.
        """
        try:
            if not (isinstance(clase_servicio, type) and issubclass(clase_servicio, Servicio)):
                raise ServicioInvalidoError("La clase indicada no es un tipo de servicio valido.")
            servicio = clase_servicio(*args, **kwargs)        # Aqui actua el polimorfismo del constructor
        except ErrorSoftwareFJ as error:
            log.error("REGISTRAR SERVICIO fallido | %s", error)
            return None
        except TypeError as error:                            # Faltan o sobran argumentos del constructor
            log.error("REGISTRAR SERVICIO fallido | argumentos incorrectos: %s", error)
            return None
        else:
            self._servicios.append(servicio)
            log.info("REGISTRAR SERVICIO exitoso | %s", servicio.describir())
            return servicio

    def crear_reserva(self, id_cliente, id_servicio, horas):
        """Crea una reserva pendiente. Devuelve la Reserva o None si hubo error."""
        try:
            cliente = self._buscar(self._clientes, id_cliente, "el cliente")
            servicio = self._buscar(self._servicios, id_servicio, "el servicio")
            reserva = Reserva(cliente, servicio, horas)
        except ErrorSoftwareFJ as error:
            log.error("CREAR RESERVA fallido | %s", error)
            return None
        else:
            self._reservas.append(reserva)
            log.info("CREAR RESERVA exitoso | %s", reserva.describir())
            return reserva

    def ejecutar(self, operacion, *args, **kwargs):
        """
        Ejecuta confirmar / cancelar / procesar sobre una reserva de forma segura.
        Devuelve (True, resultado) si salio bien o (False, mensaje_de_error) si fallo.
        """
        try:
            resultado = operacion(*args, **kwargs)
        except ErrorSoftwareFJ as error:                      # Errores propios: ya fueron registrados
            return False, str(error)
        except Exception as error:                            # Cualquier error inesperado
            log.critical("ERROR INESPERADO en %s | %s: %s", getattr(operacion, "__name__", operacion),
                         type(error).__name__, error)
            return False, f"Error inesperado ({type(error).__name__}): {error}"
        else:
            return True, resultado
