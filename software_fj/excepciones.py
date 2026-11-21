"""
Excepciones personalizadas de Software FJ.

Todas heredan de ErrorSoftwareFJ, de modo que el sistema pueda capturar
"cualquier error propio de la aplicacion" con un solo except, o bien
capturar un tipo concreto cuando necesite reaccionar de forma distinta.
"""


class ErrorSoftwareFJ(Exception):
    """Excepcion base de toda la aplicacion."""


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se llamo a una operacion sin entregar un dato obligatorio."""


class RegistroNoEncontradoError(ErrorSoftwareFJ):
    """Se busco un cliente o servicio por su ID y no existe en las listas del sistema."""


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Los datos personales de un cliente no cumplen las validaciones."""


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Los parametros de un servicio (o de su uso) son incorrectos."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """El servicio existe, pero en este momento no se puede reservar."""


class ReservaInvalidaError(ErrorSoftwareFJ):
    """No se pudo construir la reserva con los datos entregados."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """La operacion no es valida para el estado actual de la reserva."""


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """El calculo de un costo dio un resultado imposible o incoherente."""
