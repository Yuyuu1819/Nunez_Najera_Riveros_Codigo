import numpy as np
import time

# Convert text function to math function (safe to work with yk)
def safe_function(function_text):
    """
    Convertimos textito como:
    sin(x) + x**2

    en una función matemática segura usando numpy.
    """

    # Funciones permitidas
    allowed_names = {
        "x": 0,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "sqrt": np.sqrt,
        "log": np.log,
        "pi": np.pi,
        "e": np.e
    }

    # Regresa una función evaluable
    return lambda x: eval(function_text, {"__builtins__": {}}, {**allowed_names, "x": x})

# SIMPSON 1/3 METHOD
def simpson_one_third(f, a, b, n):
    """
    Calculamos la integral usando Simpson 1/3 compuesto.
    """

    # Simpson requiere n PAR
    if n % 2 != 0:
        raise ValueError("n debe ser un número PAR.")

    start_time = time.perf_counter()

    h = (b - a) / n

    # Sumatoria
    total = f(a) + f(b)

    # Términos impares
    for i in range(1, n):
        x = a + i * h

        if i % 2 == 0:
            total += 2 * f(x)
        else:
            total += 4 * f(x)

    result = (h / 3) * total

    end_time = time.perf_counter()

    execution_time = (end_time - start_time) * 1_000_000

    return result, execution_time