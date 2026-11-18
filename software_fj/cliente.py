"""
Clase Cliente: encapsula los datos personales y los valida de forma estricta.
"""

import re  # Libreria de expresiones regulares: sirve para comprobar que un texto tenga cierto formato.

from .entidad import EntidadBase  # Clase abstracta de la que hereda Cliente (aporta el ID unico).
from .excepciones import ClienteInvalidoError, ParametroFaltanteError  # Errores personalizados del sistema.

# Patrones de validacion (se compilan una sola vez para reutilizarlos).
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{3,60}$")  # Solo letras y espacios, de 3 a 60 caracteres.
PATRON_DOCUMENTO = re.compile(r"^\d{6,12}$")  # Solo digitos, de 6 a 12.
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")  # Formato usuario@dominio.ext
PATRON_TELEFONO = re.compile(r"^\d{7,10}$")  # Solo digitos, de 7 a 10.


class Cliente(EntidadBase):
    """Cliente de Software FJ."""

    prefijo = "CLI"  # Los IDs de los clientes seran CLI-001, CLI-002, ...

    def __init__(self, nombre, documento, correo, telefono):
        # Cada asignacion pasa por su setter, que valida el dato antes de guardarlo.
        self.nombre = nombre  # Valida y guarda el nombre.
        self.documento = documento  # Valida y guarda el documento.
        self.correo = correo  # Valida y guarda el correo.
        self.telefono = telefono  # Valida y guarda el telefono.

        # Solo se genera el ID cuando todos los datos fueron validos.
        super().__init__()

    # ---------- Validaciones auxiliares ----------

    @staticmethod
    def _texto_obligatorio(valor, campo):
        """Verifica que el dato exista y sea un texto no vacio."""

        if valor is None:  # El dato no fue entregado.
            raise ParametroFaltanteError(  # Error propio: falta un parametro obligatorio.
                f"Falta el dato obligatorio: {campo}."
            )

        if not isinstance(valor, str):  # El dato no es un texto (por ejemplo, es un numero).
            raise ClienteInvalidoError(  # Error propio: dato de cliente invalido.
                f"{campo} debe ser texto, se recibio {type(valor).__name__}."
            )

        valor = valor.strip()  # Quita los espacios sobrantes al inicio y al final.

        if not valor:  # Quedo vacio despues de limpiar los espacios.
            raise ClienteInvalidoError(
                f"{campo} no puede estar vacio."
            )

        return valor  # Devuelve el texto ya limpio.

    # ---------- Propiedades (getters y setters) ----------

    @property
    def nombre(self):
        # Getter: permite leer cliente.nombre desde fuera de la clase.
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        # Setter: se ejecuta cada vez que se asigna cliente.nombre = ...
        valor = self._texto_obligatorio(valor, "nombre")  # Comprueba que exista y sea texto.

        if not PATRON_NOMBRE.match(valor):  # Debe cumplir el patron de solo letras y espacios.
            raise ClienteInvalidoError(
                f"Nombre invalido: '{valor}' (solo letras, 3 a 60 caracteres)."
            )

        if len(valor.split()) < 2:  # split() separa por espacios: se exigen al menos 2 palabras.
            raise ClienteInvalidoError(
                "Debe ingresar nombre y apellido."
            )

        self._nombre = valor.title()  # Se guarda con formato "Nombre Apellido".

    @property
    def documento(self):
        # Getter del documento de identidad.
        return self._documento

    @documento.setter
    def documento(self, valor):
        valor = self._texto_obligatorio(valor, "documento")  # Comprueba que exista y sea texto.

        if not PATRON_DOCUMENTO.match(valor):  # Debe tener solo numeros (6 a 12 digitos).
            raise ClienteInvalidoError(
                f"Documento invalido: '{valor}' (solo numeros, 6 a 12 digitos)."
            )

        self._documento = valor  # Se guarda el documento validado.

    @property
    def correo(self):
        # Getter del correo electronico.
        return self._correo

    @correo.setter
    def correo(self, valor):
        valor = self._texto_obligatorio(valor, "correo")  # Comprueba que exista y sea texto.

        if not PATRON_CORREO.match(valor):  # Debe tener el formato usuario@dominio.ext
            raise ClienteInvalidoError(
                f"Correo invalido: '{valor}'."
            )

        self._correo = valor.lower()  # Se guarda en minusculas para evitar duplicados por mayusculas.

    @property
    def telefono(self):
        # Getter del telefono.
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        valor = self._texto_obligatorio(valor, "telefono")  # Comprueba que exista y sea texto.

        if not PATRON_TELEFONO.match(valor):  # Debe tener solo numeros (7 a 10 digitos).
            raise ClienteInvalidoError(
                f"Telefono invalido: '{valor}' (7 a 10 digitos)."
            )

        self._telefono = valor  # Se guarda el telefono validado.

    # ---------- Actualizacion de contacto ----------

    def actualizar_contacto(self, correo, telefono):
        """Actualiza el correo y el telefono del cliente."""

        # Primero se validan AMBOS datos, para no dejar el contacto a medio cambiar si uno falla.
        correo = self._texto_obligatorio(correo, "correo")  # El correo existe y es texto.
        telefono = self._texto_obligatorio(telefono, "telefono")  # El telefono existe y es texto.

        if not PATRON_CORREO.match(correo):  # El correo tiene un formato incorrecto.
            raise ClienteInvalidoError(f"Correo invalido: '{correo}'.")

        if not PATRON_TELEFONO.match(telefono):  # El telefono tiene un formato incorrecto.
            raise ClienteInvalidoError(
                f"Telefono invalido: '{telefono}' (7 a 10 digitos)."
            )

        # Con los dos datos validos, se actualizan usando los setters.
        self.correo = correo
        self.telefono = telefono

    # ---------- Metodo abstracto implementado ----------

    def describir(self):
        # Implementa el metodo abstracto de EntidadBase: devuelve el cliente como texto legible.
        return (
            f"[{self.id}] {self.nombre} | Doc: {self.documento} "
            f"| {self.correo} | Tel: {self.telefono}"
        )
