"""
Software FJ - Simulacion de 21 operaciones (validas e invalidas).

Programacion (213023) - UNAD - Fase 4
Ejecutar con:  python main.py
Los errores se registran en logs/software_fj.log y el programa nunca se detiene.
"""

from software_fj.registro import RUTA_LOGS, obtener_logger
from software_fj.servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala
from software_fj.sistema import SistemaFJ

log = obtener_logger()
resumen = {"exitosas": 0, "fallidas": 0}          # Contadores para el resumen final


def mostrar(numero, titulo, exito, detalle=""):
    """Imprime el resultado de cada operacion y actualiza los contadores."""
    marca = "OK   " if exito else "ERROR"
    resumen["exitosas" if exito else "fallidas"] += 1
    print(f"{numero:>2}. [{marca}] {titulo}" + (f"\n        -> {detalle}" if detalle else ""))


def main():
    sistema = SistemaFJ()
    print("=" * 70)
    print(" SOFTWARE FJ - Simulacion del sistema de clientes, servicios y reservas")
    print("=" * 70)

    # ---------------- CLIENTES ----------------
    c1 = sistema.registrar_cliente("ana maria perez", "1065432100", "ana.perez@correo.com", "3001234567")
    mostrar(1, "Registrar cliente valido (Ana Maria Perez)", c1 is not None, c1.describir() if c1 else "")

    c_malo = sistema.registrar_cliente("Luis Gomez", "10654abc", "luis@correo", "3009876543")
    mostrar(2, "Registrar cliente con documento invalido (letras)", c_malo is not None,
            "Rechazado (ver logs/software_fj.log)" if c_malo is None else "")

    c2 = sistema.registrar_cliente("Carlos Andres Ruiz", "1102233445", "carlos.ruiz@empresa.co", "3157894561")
    mostrar(3, "Registrar cliente valido (Carlos Andres Ruiz)", c2 is not None, c2.describir() if c2 else "")

    c_dup = sistema.registrar_cliente("Carlos Andres Ruiz", "1102233445", "otro@correo.com", "3157894561")
    mostrar(4, "Registrar cliente con documento repetido", c_dup is not None,
            "Rechazado (ver logs)" if c_dup is None else "")

    # ---------------- SERVICIOS ----------------
    sala = sistema.registrar_servicio(ReservaSala, "Sala Innovacion", 50000, 10)
    mostrar(5, "Crear servicio ReservaSala valido", sala is not None, sala.describir() if sala else "")

    equipo = sistema.registrar_servicio(AlquilerEquipo, "Portatil Gamer", 8000, 2, deposito=100000)
    mostrar(6, "Crear servicio AlquilerEquipo valido", equipo is not None, equipo.describir() if equipo else "")

    asesoria = sistema.registrar_servicio(AsesoriaEspecializada, "Ciberseguridad", 120000, nivel="senior")
    mostrar(7, "Crear servicio AsesoriaEspecializada valido", asesoria is not None,
            asesoria.describir() if asesoria else "")

    servicio_malo = sistema.registrar_servicio(ReservaSala, "Sala Fantasma", -500, 5)
    mostrar(8, "Crear servicio con tarifa negativa", servicio_malo is not None,
            "Rechazado (ver logs)" if servicio_malo is None else "")

    # ---------------- RESERVAS ----------------
    r1 = sistema.crear_reserva(c1.id, sala.id, 3)
    mostrar(9, "Crear reserva valida (Ana, sala, 3 h)", r1 is not None, r1.describir() if r1 else "")

    r_mala = sistema.crear_reserva(c1.id, sala.id, 20)
    mostrar(10, "Crear reserva con duracion imposible (20 h en una sala)", r_mala is not None,
            "Rechazada (ver logs)" if r_mala is None else "")

    ok, res = sistema.ejecutar(r1.confirmar)
    mostrar(11, "Confirmar la reserva de Ana", ok, f"Estado: {r1.estado.value}" if ok else res)

    # Sobrecarga simulada: procesar con impuesto y descuento
    ok, res = sistema.ejecutar(r1.procesar, 0.19, 0.10)
    mostrar(12, "Procesar reserva con IVA 19 % y descuento 10 %", ok,
            f"Costo final: ${res:,.2f}" if ok else res)

    ok, res = sistema.ejecutar(r1.cancelar, "El cliente cambio de opinion")
    mostrar(13, "Cancelar una reserva ya procesada (operacion no permitida)", ok, "" if ok else res)

    # Servicio no disponible
    equipo.disponible = False
    r2 = sistema.crear_reserva(c2.id, equipo.id, 5)
    mostrar(14, "Reservar un equipo que no esta disponible", r2 is not None,
            "Rechazada (ver logs)" if r2 is None else "")

    # Parametro faltante (horas = None) y cliente inexistente
    r3 = sistema.crear_reserva(c2.id, asesoria.id, None)
    mostrar(15, "Crear reserva sin indicar la duracion (parametro faltante)", r3 is not None,
            "Rechazada (ver logs)" if r3 is None else "")

    r4 = sistema.crear_reserva("CLI-999", asesoria.id, 2)
    mostrar(16, "Crear reserva para un cliente inexistente", r4 is not None,
            "Rechazada (ver logs)" if r4 is None else "")

    # Flujo exitoso con otro servicio: asesoria senior
    r5 = sistema.crear_reserva(c2.id, asesoria.id, 2)
    ok1, _ = sistema.ejecutar(r5.confirmar)
    ok2, costo = sistema.ejecutar(r5.procesar)           # Sin argumentos: usa el IVA por defecto
    mostrar(17, "Reserva de asesoria senior: crear, confirmar y procesar (IVA por defecto)", ok1 and ok2,
            f"Costo final: ${costo:,.2f}" if ok2 else costo)

    # Descuento fuera de rango en una reserva confirmada: el error NO detiene el programa
    r6 = sistema.crear_reserva(c1.id, asesoria.id, 1)
    sistema.ejecutar(r6.confirmar)
    ok, res = sistema.ejecutar(r6.procesar, 0.19, 0.90)
    mostrar(18, "Procesar con descuento inconsistente del 90 %", ok, "" if ok else res)

    # ---------------- VALIDACIONES DE CADA SERVICIO ESPECIALIZADO ----------------
    # Cada servicio valida sus propios parametros al crearse (polimorfismo).
    sala_mala = sistema.registrar_servicio(ReservaSala, "Sala Sin Cupo", 40000, 0)
    mostrar(19, "Crear ReservaSala con capacidad 0 (invalida)", sala_mala is not None,
            "Rechazado (ver logs)" if sala_mala is None else "")

    equipo_malo = sistema.registrar_servicio(AlquilerEquipo, "Proyector", 15000, 0, deposito=-50000)
    mostrar(20, "Crear AlquilerEquipo con cantidad 0 y deposito negativo", equipo_malo is not None,
            "Rechazado (ver logs)" if equipo_malo is None else "")

    asesoria_mala = sistema.registrar_servicio(AsesoriaEspecializada, "Redes", 90000, nivel="experto")
    mostrar(21, "Crear AsesoriaEspecializada con nivel inexistente ('experto')", asesoria_mala is not None,
            "Rechazado (ver logs)" if asesoria_mala is None else "")

    # ---------------- RESUMEN ----------------
    print("-" * 70)
    print(f" Operaciones simuladas : {resumen['exitosas'] + resumen['fallidas']}")
    print(f" Exitosas              : {resumen['exitosas']}")
    print(f" Con error controlado  : {resumen['fallidas']}")
    print(f" Reservas registradas  : {len(sistema.reservas)}")
    print(f" Log de eventos        : {RUTA_LOGS}")
    print("=" * 70)
    print(" El programa termino de forma normal: ningun error lo detuvo.")
    log.info("Simulacion finalizada | exitosas=%d | con error controlado=%d",
             resumen["exitosas"], resumen["fallidas"])


if __name__ == "__main__":
    main()
