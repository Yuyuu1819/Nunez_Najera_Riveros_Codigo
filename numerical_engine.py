import numpy as np
import time

def safe_function(function_text):
  
    #CONVERSIÓN DE TEXTO A FUNCIÓN MATEMÁTICA EVALUABLE
    #Toma un string (ej. 'sin(x) + x**2') y construye  una función ejecutable en Python
    #Permite al usuario escribir libremente fórmulas en la interfaz gráfica.
    
    
    # DICCIONARIO DE NOMBRES PERMITIDOS 
    # Al mapear explícitamente palabras clave a funciones de NumPy
    # para que solo se puedan resolver operaciones matemáticas deseadas.
    allowed_names = {
        "x":     0,          # Declaramos 'x' como variable válida 
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

    # VALIDACIÓN SINTÁCTICA PREVIA
    #  Evita que el programa se rompa si el usuario escribe algo
    # sin sentido o con errores de sintaxis (ej. 'sin(x++').
    # compile() comprueba la gramática del texto antes de que la app intente calcular nada.
    try:
        compile(function_text, "<string>", "eval")
    except SyntaxError as err:
        raise ValueError(f"Sintaxis inválida en la ecuación: {err}")

    def f(x):
        
       # Función interna evaluadora para un punto 'x' específico.
        
        try:
            # MANEJO DE ENTRADAS 
            # 1. {"__builtins__": {}}: Bloquea el acceso a todas las funciones nativas
            #    peligrosas de Python (como 'import', 'open', 'eval', etc.).
            # 2. {**allowed_names, "x": x}: Inyecta el valor numérico actual de 'x' en el cálculo.
            return float(eval(function_text,
                              {"__builtins__": {}},
                              {**allowed_names, "x": x}))
                              
        except ZeroDivisionError:
            # Entrada problemática tipo 1 Divisiones por cero (ej. f(x) = 1/x cuando x=0)
            # Retornamos 'NaN' (Not a Number) para que Matplotlib rompa la línea de forma limpia
            # en la gráfica en lugar de colapsar o congelar toda la interfaz.
            return float("nan")
            
        except (ValueError, TypeError):
            # Entrada problemática tipo 2 Raíces de números negativos o logaritmos negativos.
            # Funciones como np.sqrt(-1) o np.log(-5) devuelven excepciones o advertencias en flotantes.
            # Capturarlas aquí y devolver 'NaN' previene la interrupción abrupta del bucle de integración.
            return float("nan")
            
        except Exception as err:
            # Cualquier otra anomalía  se manda en un mensaje claro
            #  mostrado en los pop-ups de error de Tkinter.
            raise ValueError(f"Error al evaluar f(x) en x={x}: {err}")

    return f


def simpson_simple(f, a, b):
    
    #MÉTODO DE SIMPSON 1/3 SIMPLE
    #Aproxima la integral de una función en el intervalo [a, b] utilizando un único 
    #polinomio de segundo grado (una parábola) que conecta exactamente 3 puntos: 
    #el extremo izquierdo, el punto medio y el extremo derecho.
    
   # Fórmula matemática implementada:
   # Integral ≈ (h / 3) * [ f(x0) + 4*f(x1) + f(x2) ]
    
    # Iniciamos el contador de rendimiento de alta precisión
    t0 = time.perf_counter()

    # Cálculo del paso (h): la distancia entre dos puntos contiguos
    h  = (b - a) / 2.0
    
    # Definición de los 3 nodos obligatorios del método simple
    x0 = a                  # Límite inferior
    x1 = (a + b) / 2.0      # Punto medio
    x2 = b                  # Límite superior
    
    # Aplicación estricta de la regla de Simpson 1/3 básica
    result = (h / 3.0) * (f(x0) + 4.0 * f(x1) + f(x2))

    t1 = time.perf_counter()
    # Retorna el resultado numérico y el tiempo transformado a MICROSEGUNDOS
    return result, (t1 - t0) * 1_000_000


def simpson_one_third(f, a, b, n):
    
    #MÉTODO DE SIMPSON 1/3 COMPUESTO
    #Divide el intervalo completo [a, b] en 'n' subintervalos más pequeños. En cada pareja 
    #de subintervalos adyacentes ajusta una parábola independiente. Al sumar las áreas de 
    #todas estas pequeñas parábolas locales, se obtiene una aproximación precisa.
    
    
    # VALIDACIONES CRÍTICAS DE ENTRADA
    # El método compuesto requiere obligatoriamente que el número de subintervalos (n) 
    # sea PAR, ya que cada parábola necesita exactamente 2 subintervalos (3 puntos) para 
    # poder construirse. Un número impar causaría que el último tramo quede incompleto.
    if n <= 0:
        raise ValueError("El número de subintervalos 'n' debe ser un entero positivo.")
    if n % 2 != 0:
        raise ValueError("El número 'n' debe ser estrictamente PAR para el método de Simpson 1/3.")

    # Iniciamos el cronómetro
    t0 = time.perf_counter()

    # Ancho uniforme de cada uno de los subintervalos
    h     = (b - a) / n
    
    # Inicialización de la sumatoria con los extremos del intervalo global.
    # Los extremos a y b sólo pertenecen a una parábola, por ende su coeficiente es 1.
    total = f(a) + f(b)

    # Bucle para recorrer los nodos internos (desde x1 hasta x_n-1)
    for i in range(1, n):
        xi = a + i * h
        
        # LÓGICA DE COEFICIENTES 
        #  Los nodos IMPARES (i=1, 3, 5...) representan los puntos medios de las parábolas : Coeficiente 4.
        #  Los nodos PARES (i=2, 4, 6...) son las fronteras compartidas donde termina una parábola 
        #   y empieza la siguiente, por lo tanto se suman dos veces : Coeficiente 2.
        if i % 2 == 0:
            total += 2.0 * f(xi)   # Nodo par
        else:
            total += 4.0 * f(xi)   # Nodo impar

    # Multiplicación final por el factor h/3 dictado por el método
    result = (h / 3.0) * total

    t1 = time.perf_counter()
    # Retorna el resultado y el tiempo en microsegundos
    return result, (t1 - t0) * 1_000_000