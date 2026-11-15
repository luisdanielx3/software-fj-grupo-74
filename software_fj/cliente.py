
"""
Clase Cliente: encapsula los datos personales y los valida de forma estricta.
"""

import re  # Expresiones regulares para validar formatos.

from .entidad import EntidadBase
from .excepciones import ClienteInvalidoError, ParametroFaltanteError

# Patrones de validacion.
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{3,60}$")
PATRON_DOCUMENTO = re.compile(r"^\d{6,12}$")
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
PATRON_TELEFONO = re.compile(r"^\d{7,10}$")


class Cliente(EntidadBase):
    """Cliente de Software FJ."""

    prefijo = "CLI"

    def __init__(self, nombre, documento, correo, telefono):
        # Validar y guardar los datos del cliente.
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono

        # Generar el identificador cuando los datos sean validos.
        super().__init__()

    # ---------- Validaciones auxiliares ----------

    @staticmethod
    def _texto_obligatorio(valor, campo):
        """Verifica que el dato exista y sea un texto no vacio."""

        if valor is None:
            raise ParametroFaltanteError(
                f"Falta el dato obligatorio: {campo}."
            )

        if not isinstance(valor, str):
            raise ClienteInvalidoError(
                f"{campo} debe ser texto, se recibio {type(valor).__name__}."
            )

        valor = valor.strip()

        if not valor:
            raise ClienteInvalidoError(
                f"{campo} no puede estar vacio."
            )

        return valor

    # ---------- Propiedades (getters y setters) ----------

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        valor = self._texto_obligatorio(valor, "nombre")

        if not PATRON_NOMBRE.match(valor):
            raise ClienteInvalidoError(
                f"Nombre invalido: '{valor}' (solo letras, 3 a 60 caracteres)."
            )

        if len(valor.split()) < 2:
            raise ClienteInvalidoError(
                "Debe ingresar nombre y apellido."
            )

        self._nombre = valor.title()

    @property
    def documento(self):
        return self._documento

    @documento.setter
    def documento(self, valor):
        valor = self._texto_obligatorio(valor, "documento")

        if not PATRON_DOCUMENTO.match(valor):
            raise ClienteInvalidoError(
                f"Documento invalido: '{valor}' (solo numeros, 6 a 12 digitos)."
            )

        self._documento = valor

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        valor = self._texto_obligatorio(valor, "correo")

        if not PATRON_CORREO.match(valor):
            raise ClienteInvalidoError(
                f"Correo invalido: '{valor}'."
            )

        self._correo = valor.lower()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        valor = self._texto_obligatorio(valor, "telefono")

        if not PATRON_TELEFONO.match(valor):
            raise ClienteInvalidoError(
                f"Telefono invalido: '{valor}' (7 a 10 digitos)."
            )

        self._telefono = valor

    # ---------- Actualizacion de contacto ----------

    def actualizar_contacto(self, correo, telefono):
        """Actualiza el correo y el telefono del cliente."""

        # Validar ambos datos antes de modificar el contacto.
        correo = self._texto_obligatorio(correo, "correo")
        telefono = self._texto_obligatorio(telefono, "telefono")

        if not PATRON_CORREO.match(correo):
            raise ClienteInvalidoError(f"Correo invalido: '{correo}'.")

        if not PATRON_TELEFONO.match(telefono):
            raise ClienteInvalidoError(
                f"Telefono invalido: '{telefono}' (7 a 10 digitos)."
            )

        # Actualizar utilizando los setters correspondientes.
        self.correo = correo
        self.telefono = telefono

    # ---------- Metodo abstracto implementado ----------

    def describir(self):
        return (
            f"[{self.id}] {self.nombre} | Doc: {self.documento} "
            f"| {self.correo} | Tel: {self.telefono}"
        )
