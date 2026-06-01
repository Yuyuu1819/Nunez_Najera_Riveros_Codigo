import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
# Configuración del backend de Matplotlib para que sea compatible con el bucle principal de Tkinter
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importación de las rutinas lógicas y de seguridad creadas en el motor matemático externo
from numerical_engine import safe_function, simpson_simple, simpson_one_third

# PALETA DE COLORES ESTILIZADA (Diseño Dark Mode / Paleta Industrial Nord)
BG = "#1B2A4A"          # Color de fondo general de la ventana
PANEL = "#243656"       # Fondo de los contenedores laterales
CARD = "#29436B"        # Fondo de los bloques/tarjetas de resultados
ACCENT = "#D89CA4"      # Tono rosa suave para botones y elementos activos
SKY = "#F7D4D8"         # Tono complementario pastel para títulos secundarios
WHITE = "#FFFFFF"       # Blanco puro para visibilidad de números de cálculo
OFFWHITE = "#F4E6E8"    # Blanco opaco para etiquetas de texto plano
PINK = "#D89CA4"        # Color identificativo del Método de Simpson Simple
AMBER = "#EBCB8B"       # Color identificativo del Método de Simpson Compuesto
RED = "#C75C5C"         # Tono de alerta para errores en la gráfica
PLOT_BG = "#152544"     # Fondo interno personalizado para el lienzo del gráfico

class SimpsonApp(tk.Tk):
    """
    CLASE CONTROLADORA DE LA INTERFAZ GRÁFICA (GUI)
    ¿Qué hace? Gestiona la ventana de la aplicación, dibuja los controles visuales,
    recibe los datos del usuario, llama a las funciones matemáticas y refresca la gráfica.
    """
    def __init__(self):
        super().__init__()
        self.title("Integración Numérica — Método de Simpson 1/3")
        
        # VALIDACIÓN DEL ÍCONO
        # ¿Por qué se valida? Si el archivo 'simpson.png' no existe en la carpeta, Tkinter detendría 
        # la ejecución del programa de golpe lanzando un error fatal. El try/except previene esto,
        # haciendo que si no se encuentra la imagen, la app abra de todos modos con el icono genérico.
        try:
            icon = tk.PhotoImage(file='simpson.png')
            self.iconphoto(True, icon)
        except Exception:
            pass
            
        self.configure(bg=BG)
        self.resizable(True, True)   # Permite maximizar y estirar la ventana libremente
        self.minsize(1000, 680)      # Establece un tamaño mínimo para que los textos no se encimen

        # Construcción y organización de las áreas visuales
        self._build_layout()
        # Posiciona la app en el centro exacto de la pantalla con dimensiones 1150x740
        self._center_window(1150, 740)

    def _center_window(self, w, h):
        """
        CÁLCULO GEOMÉTRICO DE POSICIONAMIENTO
        Mide el tamaño del monitor del usuario y calcula las coordenadas (x, y) 
        para que la ventana aparezca perfectamente centrada al abrirse.
        """
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_layout(self):
        """
        ARQUITECTURA DE CONTENEDORES (Marcos de Trabajo)
        Divide la interfaz en tres bloques base: Barra Superior, Panel de Entrada y Área de Gráfica.
        """
        # 1. Barra de Título Superior 
        top = tk.Frame(self, bg=ACCENT, height=52)
        top.pack(fill="x")
        top.pack_propagate(False) # Evita que el contenedor se encoja al tamaño del texto interno
        tk.Label(
            top,
            text="Método de Simpson 1/3 - Manuel Riveros, Yuliette Nuñez y Francisco Najera — Métodos Numéricos",
            font=("Arial", 16, "bold"),
            bg=ACCENT,
            fg="black"
        ).pack(pady=12)

        # 2. Contenedor Maestro Inferior (Main Workspace)
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # 3. Sub-panel Izquierdo para Captura de Datos y Respuestas
        left = tk.Frame(main, bg=PANEL, width=310)
        left.pack(side="left", fill="y")
        left.pack_propagate(False) # Forzar el ancho exacto a 310 píxeles
        self._build_left_panel(left)

        # 4. Sub-panel Derecho exclusivo para el gráfico dinámico
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        self._build_graph_panel(right)

    def _build_left_panel(self, parent):
        """
        CONSTRUCCIÓN DE ELEMENTOS DE CONTROL E INFORMACIÓN
        Genera los inputs interactivos, el botón principal y las tarjetas informativas.
        """
        sec = tk.Frame(parent, bg=PANEL)
        sec.pack(fill="x", padx=16, pady=(20, 0))

        tk.Label(sec, text="PARÁMETROS DE ENTRADA",
                 font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=SKY).pack(anchor="w", pady=(0, 10))

        # Lista de duplas que define el nombre de la variable y su valor inicial por defecto
        fields = [
            ("Función  f(x)", "sin(x)"),
            ("Límite inferior  a", "0"),
            ("Límite superior  b", "3.14159"),
            ("Subintervalos  n  (par)", "10"),
        ]
        
        # Diccionario para almacenar las referencias de las cajas de texto (Entry) y poder leerlas después
        self._entries = {}
        for label, default in fields:
            tk.Label(sec, text=label,
                     font=("Segoe UI", 9), bg=PANEL, fg=OFFWHITE).pack(anchor="w", pady=(6, 1))
            e = tk.Entry(sec,
                         font=("Consolas", 11),
                         bg=CARD, fg=WHITE,
                         insertbackground=WHITE, # Color del cursor parpadeante
                         relief="flat", bd=4)
            e.insert(0, default) # Escribe el valor predeterminado
            e.pack(fill="x", ipady=5)
            self._entries[label] = e # Guarda la caja de texto indexada por su etiqueta

        # Espaciador vertical decorativo
        tk.Frame(parent, bg=PANEL, height=14).pack()

        # Botón que acciona el cálculo general de la aplicación
        btn = tk.Button(
            parent,
            text="Calcular",
            font=("Arial", 11, "bold"),
            bg=ACCENT,
            fg="black",
            activebackground="#C98A93", # Color cuando el usuario hace clic sobre él
            activeforeground="black",
            relief="raised",
            bd=2,
            cursor="hand2",            # Cambia el puntero del mouse a una mano interactiva
            command=self._calcular     # Ejecuta la función _calcular() al ser presionado
        )
        btn.pack(fill="x", padx=16, ipady=8)

        # Línea divisoria horizontal estilizada
        tk.Frame(parent, bg="#2D4A72", height=1).pack(fill="x", padx=16, pady=16)

        # Sección informativa de visualización de datos numéricos calculados
        tk.Label(parent, text="RESULTADOS",
                 font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=SKY).pack(anchor="w", padx=16, pady=(0, 8))

        results_frame = tk.Frame(parent, bg=PANEL)
        results_frame.pack(fill="x", padx=16)

        # Generación de tarjetas de resultados llamando a la fábrica componencial
        self._card_simple = self._make_result_card(
            results_frame, "Simpson 1/3  Simple", "n = 2  (3 puntos)", PINK)

        tk.Frame(results_frame, bg=PANEL, height=8).pack()

        self._card_compuesto = self._make_result_card(
            results_frame, "Simpson 1/3  Compuesto", "n ingresado", AMBER)

        # Sección para mostrar el error absoluto residual entre los dos modelos
        tk.Frame(parent, bg="#2D4A72", height=1).pack(fill="x", padx=16, pady=14)
        tk.Label(parent, text="COMPARATIVA",
                 font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=SKY).pack(anchor="w", padx=16, pady=(0, 6))

        self._lbl_diff = tk.Label(parent,
                                  text="—",
                                  font=("Consolas", 10),
                                  bg=PANEL, fg=OFFWHITE,
                                  wraplength=270, justify="left")
        self._lbl_diff.pack(anchor="w", padx=16)

    def _make_result_card(self, parent, titulo, subtitulo, color):
        """
        FÁBRICA DE TARJETAS ESTÉTICAS (Cards UI)
        Ensambla un pequeño bloque visual con bordes de color personalizados para 
        mostrar el valor de la integral y el tiempo que tardó la computadora en calcularlo.
        """
        card = tk.Frame(parent, bg=CARD, bd=0)
        card.pack(fill="x")

        # Línea de color vertical izquierda decorativa
        tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")

        inner = tk.Frame(card, bg=CARD)
        inner.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        tk.Label(inner, text=titulo, font=("Segoe UI", 9, "bold"), bg=CARD, fg=color).pack(anchor="w")
        tk.Label(inner, text=subtitulo, font=("Segoe UI", 8), bg=CARD, fg=SKY).pack(anchor="w")

        # Etiqueta para imprimir el valor de la integral aproximada
        lbl_val = tk.Label(inner, text="—", font=("Consolas", 15, "bold"), bg=CARD, fg=WHITE)
        lbl_val.pack(anchor="w", pady=(4, 0))

        # Etiqueta para imprimir la velocidad de cómputo
        lbl_time = tk.Label(inner, text="", font=("Segoe UI", 8), bg=CARD, fg=SKY)
        lbl_time.pack(anchor="w")

        # Retorna las referencias clave para poder actualizarlas dinámicamente con la lógica del programa
        return {"val": lbl_val, "time": lbl_time, "sub": inner.winfo_children()[1]}

    def _build_graph_panel(self, parent):
        """
        INCRUSTACIÓN NATIVA DE MATPLOTLIB
        Prepara el contenedor y los ejes cartesianos de Matplotlib y los adapta
        dentro de la arquitectura de ventanas de Tkinter.
        """
        tk.Label(parent, text="Visualización",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG, fg=WHITE).pack(anchor="w", pady=(0, 6))

        # Inicialización de la figura y del set de ejes coordenados (subplot)
        self._fig = Figure(figsize=(7, 5.2), dpi=100, facecolor=PLOT_BG)
        self._ax  = self._fig.add_subplot(111)
        self._ax.set_facecolor(PLOT_BG)
        self._ax.tick_params(colors=OFFWHITE)
        
        # Coloreado personalizado de los bordes (espinas) del gráfico
        for spine in self._ax.spines.values():
            spine.set_color("#2D4A72")
        self._ax.set_xlabel("x", color=OFFWHITE)
        self._ax.set_ylabel("f(x)", color=OFFWHITE)
        self._ax.set_title("Ingresa los parámetros y presiona Calcular", color=PINK, fontsize=10)
        self._fig.tight_layout(pad=2)

        # Widget especial que acopla la figura interactiva de Matplotlib dentro de Tkinter
        canvas = FigureCanvasTkAgg(self._fig, master=parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvas = canvas

    def _calcular(self):
        """
        MÓDULO DE VALIDACIÓN Y CONTROLADOR DE CÁLCULO
        Extrae la información ingresada por el usuario en la interfaz gráfica, 
        la valida exhaustivamente y gatilla las operaciones matemáticas.
        """
        # 1. VALIDACIÓN GENERAL DE CONVERSIÓN DE TIPOS
        # Extrae las cadenas de texto del diccionario y las intenta transformar a variables numéricas.
        # ¿Por qué se valida? Evita caídas de ejecución si el usuario deja campos vacíos o introduce letras.
        try:
            expr = list(self._entries.values())[0].get().strip()
            a    = float(list(self._entries.values())[1].get())
            b    = float(list(self._entries.values())[2].get())
            n    = int(list(self._entries.values())[3].get())
        except ValueError:
            messagebox.showerror("Error de entrada", "Los límites (a, b) deben ser números y n un número entero.")
            return

        # 2. VALIDACIONES DE COHERENCIA MATEMÁTICA EN ENTRADAS
        # - a >= b: El límite inferior de integración no puede ser mayor ni igual al superior.
        # - n <= 0: No existen áreas divididas en tramos negativos o nulos.
        # - n % 2 != 0: El método de Simpson 1/3 compuesto une puntos de tres en tres, 
        #   lo que obliga a tener una cantidad par de subintervalos.
        if a >= b:
            messagebox.showerror("Error de entrada", "El límite inferior (a) debe ser estrictamente menor que el superior (b).")
            return
        if n <= 0:
            messagebox.showerror("Error de entrada", "La cantidad de subintervalos (n) debe ser un entero positivo.")
            return
        if n % 2 != 0:
            messagebox.showerror("Error de entrada", "Para el método de Simpson 1/3 Compuesto, 'n' debe ser un número par.")
            return

        # 3. COMPILACIÓN DE LA FUNCIÓN
        try:
            f = safe_function(expr)
        except ValueError as e:
            messagebox.showerror("Error en f(x)", str(e))
            return

        # 4. INTENTO DE CÁLCULO DE INTEGRACIÓN (MÉTODO SIMPLE)
        try:
            res_simple, t_simple = simpson_simple(f, a, b)
        except Exception as e:
            messagebox.showerror("Error (Simple)", str(e))
            return

        # 5. INTENTO DE CÁLCULO DE INTEGRACIÓN (MÉTODO COMPUESTO)
        try:
            res_comp, t_comp = simpson_one_third(f, a, b, n)
        except ValueError as e:
            messagebox.showerror("Error (Compuesto)", str(e))
            return

        # 6. TRANSFORMACIÓN DE UNIDADES DE TIEMPO (Microsegundos a Segundos)
        # El motor matemático calcula los tiempos en microsegundos (μs). Para cambiar la escala
        # a segundos (s), dividimos entre 1,000,000.0. Usamos el formateador decimal científico ':.3e' 
        # (ej. 4.120e-06 s) porque las operaciones matemáticas en Python se ejecutan tan rápido 
        # que una notación estándar fija arrojaría siempre '0.000 s'.
        t_simple_seg = t_simple / 1000000.0
        t_comp_seg = t_comp / 1000000.0

        # 7. REFRESCO DINÁMICO DE LOS VALORES EN LAS TARJETAS DE LA INTERFAZ
        self._card_simple["val"].config(text=f"{res_simple:.8f}")
        self._card_simple["time"].config(text=f"  {t_simple_seg:.3e} s")

        self._card_compuesto["val"].config(text=f"{res_comp:.8f}")
        self._card_compuesto["time"].config(text=f"  {t_comp_seg:.3e} s      n = {n}")
        self._card_compuesto["sub"].config(text=f"n = {n}  {n+1} puntos")

        # Cálculo y despliegue del error residual absoluto entre ambas modalidades
        diff = abs(res_comp - res_simple)
        self._lbl_diff.config(text=f"Diferencia entre métodos:\n{diff:.8f}")

        # 8. LLAMADO AL RENDERIZADOR DE LA GRÁFICA
        self._plot(f, a, b, n, expr, res_simple, res_comp)

    def _plot(self, f, a, b, n, expr, res_simple, res_comp):
        """
        DIBUJO DINÁMICO DE CURVAS, PARÁBOLAS Y ÁREAS DE INTEGRACIÓN
        Limpia los trazos anteriores y gráfica en tiempo real el comportamiento del método numérico.
        """
        ax = self._ax
        ax.clear()                  # Borrado total y absoluto de trazos o líneas previas en el eje
        ax.set_facecolor(PLOT_BG)   # Re-establece el color de fondo nocturno
        ax.tick_params(colors=OFFWHITE, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#2D4A72")
        ax.set_xlabel("x", color=OFFWHITE, fontsize=9)
        ax.set_ylabel("f(x)", color=OFFWHITE, fontsize=9)

        # Generación de la muestra matemática para simular continuidad de la función real (600 puntos)
        x_cont = np.linspace(a, b, 600)
        try:
            y_cont = np.array([f(xi) for xi in x_cont], dtype=float)
        except Exception:
            ax.set_title("Error al graficar f(x)", color=RED)
            self._canvas.draw()
            return

        # Traza la línea continua azul que representa el trazo real de f(x)
        ax.plot(x_cont, y_cont, color="#60A5FA", linewidth=2,
                label=f"f(x) = {expr}", zorder=3)

        # CONSTRUCCIÓN GEOMÉTRICA DE PARÁBOLAS DE SIMPSON COMPUESTO
        h = (b - a) / n
        # El ciclo avanza saltando de 2 en 2 subintervalos porque cada parábola requiere 3 nodos consecutivos
        for k in range(0, n, 2):
            x0 = a + k * h        # Extremo izquierdo de la parábola actual
            x1 = a + (k + 1) * h  # Punto central de la parábola actual
            x2 = a + (k + 2) * h  # Extremo derecho de la parábola actual
            
            pts = np.linspace(x0, x2, 80) # 80 puntos locales internos para suavizar la curva de la parábola
            y0, y1, y2 = f(x0), f(x1), f(x2)
            
            # Polinomio interpolador de Lagrange: construye matemáticamente la parábola única que cruza por esos 3 puntos
            L0 = ((pts - x1) * (pts - x2)) / ((x0 - x1) * (x0 - x2))
            L1 = ((pts - x0) * (pts - x2)) / ((x1 - x0) * (x1 - x2))
            L2 = ((pts - x0) * (pts - x1)) / ((x2 - x0) * (x2 - x1))
            y_par = y0 * L0 + y1 * L1 + y2 * L2
            
            # Dibuja físicamente el contorno curvo amarillo de la parábola aproximada (Dentro del ciclo iterador)
            ax.plot(pts, y_par, color="#FCD34D", linewidth=1, zorder=2)
            
            # Sombrea el área rellena debajo de esta parábola para simular visualmente la sumatoria de áreas integradas
            ax.fill_between(pts, y_par, alpha=0.20, color="#FCD34D", zorder=1)

        # Graficación de Nodos Compuestos (Trazado de columnas punteadas verticales)
        x_nodes = np.array([a + i * h for i in range(n + 1)])
        y_nodes = np.array([f(xi) for xi in x_nodes])
        ax.vlines(x_nodes, 0, y_nodes, colors="#94A3B8", linewidth=0.6, linestyle=":", zorder=2)
        ax.scatter(x_nodes, y_nodes, color="#FCD34D", s=28, zorder=5, label=f"Nodos compuesto (n={n})")

        # Graficación de Nodos Simples (Marcadores grandes con forma de diamantes rosados "D")
        xm = (a + b) / 2.0
        ym = f(xm)
        ax.scatter([a, xm, b], [f(a), ym, f(b)],
                   color=PINK, s=60, zorder=6,
                   marker="D", label="Nodos simple (n=2)")

        # Inserción de títulos y métricas en el encabezado interno del marco del gráfico
        ax.set_title(
            f"Simple = {res_simple:.6f}   |   Compuesto (n={n}) = {res_comp:.6f}",
            color=WHITE, fontsize=9, pad=8)

        # Ajustes de rejilla y posicionamiento de cuadro de leyendas explicativas
        ax.axhline(0, color="#2D4A72", linewidth=0.8)
        ax.grid(True, color="#1E3A5F", linewidth=0.5, alpha=0.7)
        ax.legend(fontsize=8, facecolor="#0F1C30",
                  edgecolor="#2D4A72", labelcolor=OFFWHITE,
                  loc="upper right")

        self._fig.tight_layout(pad=1.8)
        
        # OPERACIÓN DE REDIBUJADO DE LIENZO (Fuerza a Matplotlib a plasmar los nuevos vectores en la GUI)
        self._canvas.draw()

