# Software FJ - Sistema integral de gestion de clientes, servicios y reservas

Proyecto de la **Fase 4** del curso **Programacion (213023)** - UNAD.
Sistema orientado a objetos en Python, **sin base de datos**, con manejo avanzado de excepciones.

## Como ejecutarlo

```bash
python main.py
```

Requiere Python 3.10 o superior. No necesita instalar librerias externas.
Los errores y eventos se registran en `logs/software_fj.log`.

## Estructura

| Archivo | Contenido |
|---|---|
| `main.py` | Simulacion de 21 operaciones (validas e invalidas) |
| `software_fj/entidad.py` | Clase abstracta `EntidadBase` (ID unico + `describir()`) |
| `software_fj/cliente.py` | `Cliente` con datos privados y validaciones estrictas |
| `software_fj/servicios.py` | Clase abstracta `Servicio` + `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` |
| `software_fj/reserva.py` | `Reserva` (confirmar, cancelar, procesar) y `EstadoReserva` |
| `software_fj/sistema.py` | `SistemaFJ`: listas internas y operaciones seguras |
| `software_fj/excepciones.py` | Excepciones personalizadas |
| `software_fj/registro.py` | Configuracion del archivo de logs |

## Conceptos aplicados

- **Abstraccion:** `EntidadBase` y `Servicio` son clases abstractas (`ABC`, `@abstractmethod`).
- **Herencia y polimorfismo:** los tres servicios sobrescriben `validar_parametros`, `calcular_costo` y `describir`.
- **Encapsulacion:** atributos privados con `property` y validacion en los setters.
- **Sobrecarga simulada:** `calcular_costo(horas)`, `calcular_costo(horas, impuesto)`, `calcular_costo(horas, impuesto, descuento)` y `procesar()` con parametros opcionales.
- **Excepciones:** clases personalizadas, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento con `raise ... from ...`.
- **Logs:** cada error y evento relevante queda en `logs/software_fj.log`; el programa nunca se detiene.

## Integrantes

Grupo 213023_74

- Rosa Isela Betancurt Cabrales
- Luis Daniel Vergara Orozco
- Iván Daniel Jiménez Carrillo
