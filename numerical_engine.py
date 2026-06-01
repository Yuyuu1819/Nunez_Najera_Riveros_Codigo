import numpy as np
import time


def safe_function(function_text):
    """
    Convierte texto como 'sin(x) + x**2' en una función matemática
    segura usando numpy. Solo permite operaciones matemáticas básicas.
    Lanza ValueError si la expresión es inválida o usa nombres no permitidos.
    """
    allowed_names = {
        "x":    0,
        "sin":  np.sin,
        "cos":  np.cos,
        "tan":  np.tan,
        "exp":  np.exp,
        "sqrt": np.sqrt,
        "log":  np.log,
        "log2": np.log2,
        "log10":np.log10,
        "abs":  np.abs,
        "pi":   np.pi,
        "e":    np.e,
    }

    # Validar que compile antes de devolver el lambda
    try:
        compile(function_text, "<string>", "eval")
    except SyntaxError as err:
        raise ValueError(f"Sintaxis inválida: {err}")

    def f(x):
        try:
            return float(eval(function_text,
                              {"__builtins__": {}},
                              {**allowed_names, "x": x}))
        except ZeroDivisionError:
            return float("nan")
        except Exception as err:
            raise ValueError(f"Error al evaluar f(x): {err}")

    return f


# Simpson 1/3 Simple (un solo par de subintervalos, n=2) 
def simpson_simple(f, a, b):
    """
    Aplica Simpson 1/3 básico sobre [a, b] usando solo 3 puntos:
    x0=a, x1=(a+b)/2, x2=b.

    Resultado = (b-a)/6 * [f(a) + 4*f((a+b)/2) + f(b)]

    Retorna (resultado, tiempo_us).
    """
    t0 = time.perf_counter()

    h  = (b - a) / 2.0
    x0, x1, x2 = a, (a + b) / 2.0, b
    result = (h / 3.0) * (f(x0) + 4.0 * f(x1) + f(x2))

    t1 = time.perf_counter()
    return result, (t1 - t0) * 1_000_000


#  Simpson 1/3 Compuesto (n subintervalos, n par) 
def simpson_one_third(f, a, b, n):
    """
    Aplica Simpson 1/3 Compuesto sobre [a, b] con n subintervalos (n PAR).

    Patrón de coeficientes: 1 - 4 - 2 - 4 - 2 - ... - 4 - 1
    Error global: O(h^4)

    Retorna (resultado, tiempo_us).
    Lanza ValueError si n es impar o <= 0.
    """
    if n <= 0:
        raise ValueError("n debe ser un entero positivo.")
    if n % 2 != 0:
        raise ValueError("n debe ser un número PAR para Simpson 1/3.")

    t0 = time.perf_counter()

    h     = (b - a) / n
    total = f(a) + f(b)                    # extremos: coeficiente 1

    for i in range(1, n):
        xi = a + i * h
        if i % 2 == 0:
            total += 2.0 * f(xi)           # nodos pares: coeficiente 2
        else:
            total += 4.0 * f(xi)           # nodos impares: coeficiente 4

    result = (h / 3.0) * total

    t1 = time.perf_counter()
    return result, (t1 - t0) * 1_000_000