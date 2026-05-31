import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from numerical_engine import safe_function, simpson_simple, simpson_one_third

# ── Paleta de colores ────────────────────────────────────────────────────────
BG       = "#1B2A4A"   # azul marino (fondo principal)
PANEL    = "#243656"   # panel lateral
CARD     = "#1E3A5F"   # tarjetas de resultado
ACCENT   = "#D89CA4"   # rosita acento
SKY      = "#F7D4D8"   # texto secundario
WHITE    = "#FFFFFF"
OFFWHITE = "#EABEC3"
PINK    = "#D89CA4"
AMBER    = "#FCD34D"
RED      = "#F87171"
PLOT_BG  = "#0F1C30"


class SimpsonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Integración Numérica — Método de Simpson 1/3")
        icon = tk.PhotoImage(file='simpson.png')
        self.iconphoto(True,icon)
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(1000, 680)

        self._build_layout()
        self._center_window(1150, 740)

    # ── Centrar ventana ──────────────────────────────────────────────────────
    def _center_window(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Layout principal ─────────────────────────────────────────────────────
    def _build_layout(self):
        # Título top bar
        top = tk.Frame(self, bg=ACCENT, height=52)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="  Integración Numérica  ·  Método de Simpson 1/3  ",
                 font=("Segoe UI", 14, "bold"),
                 bg=ACCENT, fg=WHITE).pack(side="left", padx=16, pady=10)
        tk.Label(top, text="CETYS Universidad - Manuel Riveros, Yuliette Nuñez y Francisco Najera — Métodos Numéricos",
                 font=("Segoe UI", 10),
                 bg=ACCENT, fg=SKY).pack(side="right", padx=16)

        # Contenedor principal
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # Panel izquierdo (inputs + resultados)
        left = tk.Frame(main, bg=PANEL, width=310)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        self._build_left_panel(left)

        # Panel derecho (gráfica)
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        self._build_graph_panel(right)

    # ── Panel izquierdo ──────────────────────────────────────────────────────
    def _build_left_panel(self, parent):
        # ── Inputs ──────────────────────────────────────────────────────────
        sec = tk.Frame(parent, bg=PANEL)
        sec.pack(fill="x", padx=16, pady=(20, 0))

        tk.Label(sec, text="PARÁMETROS DE ENTRADA",
                 font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=SKY).pack(anchor="w", pady=(0, 10))

        fields = [
            ("Función  f(x)", "sin(x)"),
            ("Límite inferior  a", "0"),
            ("Límite superior  b", "3.14159"),
            ("Subintervalos  n  (par)", "10"),
        ]
        self._entries = {}
        for label, default in fields:
            tk.Label(sec, text=label,
                     font=("Segoe UI", 9), bg=PANEL, fg=OFFWHITE).pack(anchor="w", pady=(6, 1))
            e = tk.Entry(sec,
                         font=("Consolas", 11),
                         bg=CARD, fg=WHITE,
                         insertbackground=WHITE,
                         relief="flat", bd=4)
            e.insert(0, default)
            e.pack(fill="x", ipady=5)
            self._entries[label] = e

        # ── Botón calcular ───────────────────────────────────────────────────
        tk.Frame(parent, bg=PANEL, height=14).pack()
        btn = tk.Button(parent, text="  ▶  CALCULAR",
                        font=("Segoe UI", 11, "bold"),
                        bg=ACCENT, fg=PINK,
                        activebackground=PINK,
                        activeforeground=OFFWHITE,
                        relief="flat", bd=0, cursor="hand2",
                        command=self._calcular)
        btn.pack(fill="x", padx=16, ipady=8)

        # ── Separador ────────────────────────────────────────────────────────
        tk.Frame(parent, bg="#2D4A72", height=1).pack(fill="x", padx=16, pady=16)

        # ── Resultados ───────────────────────────────────────────────────────
        tk.Label(parent, text="RESULTADOS",
                 font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=SKY).pack(anchor="w", padx=16, pady=(0, 8))

        results_frame = tk.Frame(parent, bg=PANEL)
        results_frame.pack(fill="x", padx=16)

        # Tarjeta: Simpson Simple
        self._card_simple = self._make_result_card(
            results_frame, "Simpson 1/3  Simple", "n = 2  (3 puntos)", PINK)

        tk.Frame(results_frame, bg=PANEL, height=8).pack()

        # Tarjeta: Simpson Compuesto
        self._card_compuesto = self._make_result_card(
            results_frame, "Simpson 1/3  Compuesto", "n ingresado", AMBER)

        # ── Comparativa ──────────────────────────────────────────────────────
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
        card = tk.Frame(parent, bg=CARD, bd=0)
        card.pack(fill="x")

        # Barra de color lateral
        tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")

        inner = tk.Frame(card, bg=CARD)
        inner.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        tk.Label(inner, text=titulo,
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=color).pack(anchor="w")
        tk.Label(inner, text=subtitulo,
                 font=("Segoe UI", 8),
                 bg=CARD, fg=SKY).pack(anchor="w")

        lbl_val = tk.Label(inner, text="—",
                           font=("Consolas", 15, "bold"),
                           bg=CARD, fg=WHITE)
        lbl_val.pack(anchor="w", pady=(4, 0))

        lbl_time = tk.Label(inner, text="",
                            font=("Segoe UI", 8),
                            bg=CARD, fg=SKY)
        lbl_time.pack(anchor="w")

        return {"val": lbl_val, "time": lbl_time, "sub": inner.winfo_children()[1]}

    # ── Panel de gráfica ─────────────────────────────────────────────────────
    def _build_graph_panel(self, parent):
        tk.Label(parent, text="Visualización",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG, fg=WHITE).pack(anchor="w", pady=(0, 6))

        self._fig = Figure(figsize=(7, 5.2), dpi=100, facecolor=PLOT_BG)
        self._ax  = self._fig.add_subplot(111)
        self._ax.set_facecolor(PLOT_BG)
        self._ax.tick_params(colors=OFFWHITE)
        for spine in self._ax.spines.values():
            spine.set_color("#2D4A72")
        self._ax.set_xlabel("x", color=OFFWHITE)
        self._ax.set_ylabel("f(x)", color=OFFWHITE)
        self._ax.set_title("Ingresa los parámetros y presiona Calcular",
                           color=PINK, fontsize=10)
        self._fig.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(self._fig, master=parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvas = canvas

    # ── Lógica de cálculo ────────────────────────────────────────────────────
    def _calcular(self):
        # Leer entradas
        try:
            expr = list(self._entries.values())[0].get().strip()
            a    = float(list(self._entries.values())[1].get())
            b    = float(list(self._entries.values())[2].get())
            n    = int(list(self._entries.values())[3].get())
        except ValueError:
            messagebox.showerror("Error de entrada",
                                 "a, b deben ser números y n un entero.")
            return

        if a >= b:
            messagebox.showerror("Error de entrada", "El límite a debe ser menor que b.")
            return
        if n <= 0:
            messagebox.showerror("Error de entrada", "n debe ser un entero positivo.")
            return

        # Construir función
        try:
            f = safe_function(expr)
        except ValueError as e:
            messagebox.showerror("Error en f(x)", str(e))
            return

        # ── Simpson Simple ───────────────────────────────────────────────────
        try:
            res_simple, t_simple = simpson_simple(f, a, b)
        except Exception as e:
            messagebox.showerror("Error (Simple)", str(e))
            return

        # ── Simpson Compuesto ────────────────────────────────────────────────
        try:
            res_comp, t_comp = simpson_one_third(f, a, b, n)
        except ValueError as e:
            messagebox.showerror("Error (Compuesto)", str(e))
            return

        # ── Actualizar tarjetas ──────────────────────────────────────────────
        self._card_simple["val"].config(
            text=f"{res_simple:.8f}")
        self._card_simple["time"].config(
            text=f"⏱  {t_simple:.3f} μs")

        self._card_compuesto["val"].config(
            text=f"{res_comp:.8f}")
        self._card_compuesto["time"].config(
            text=f"⏱  {t_comp:.3f} μs   |   n = {n}")
        self._card_compuesto["sub"].config(
            text=f"n = {n}  ({n+1} puntos)")

        # ── Comparativa ──────────────────────────────────────────────────────
        diff = abs(res_comp - res_simple)
        pct  = (diff / abs(res_comp) * 100) if res_comp != 0 else 0
        self._lbl_diff.config(
            text=f"Diferencia absoluta:\n  {diff:.2e}\n\n"
                 f"Diferencia relativa:\n  {pct:.4f}%\n\n"
                 f"Tiempo simple:    {t_simple:.2f} μs\n"
                 f"Tiempo compuesto: {t_comp:.2f} μs")

        # ── Gráfica ──────────────────────────────────────────────────────────
        self._plot(f, a, b, n, expr, res_simple, res_comp)

    # ── Graficar ─────────────────────────────────────────────────────────────
    def _plot(self, f, a, b, n, expr, res_simple, res_comp):
        ax = self._ax
        ax.clear()
        ax.set_facecolor(PLOT_BG)
        ax.tick_params(colors=OFFWHITE, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#2D4A72")
        ax.set_xlabel("x", color=OFFWHITE, fontsize=9)
        ax.set_ylabel("f(x)", color=OFFWHITE, fontsize=9)

        # Curva continua
        x_cont = np.linspace(a, b, 600)
        try:
            y_cont = np.array([f(xi) for xi in x_cont], dtype=float)
        except Exception:
            ax.set_title("Error al graficar f(x)", color=RED)
            self._canvas.draw()
            return

        ax.plot(x_cont, y_cont, color="#60A5FA", linewidth=2,
                label=f"f(x) = {expr}", zorder=3)
        ax.fill_between(x_cont, y_cont, alpha=0.12, color="#60A5FA")

        # ── Paneles compuesto (parábolas) ────────────────────────────────────
        h = (b - a) / n
        for k in range(0, n, 2):
            x0 = a + k * h
            x1 = a + (k + 1) * h
            x2 = a + (k + 2) * h
            pts = np.linspace(x0, x2, 80)
            y0, y1, y2 = f(x0), f(x1), f(x2)
            L0 = ((pts-x1)*(pts-x2)) / ((x0-x1)*(x0-x2))
            L1 = ((pts-x0)*(pts-x2)) / ((x1-x0)*(x1-x2))
            L2 = ((pts-x0)*(pts-x1)) / ((x2-x0)*(x2-x1))
            y_par = y0*L0 + y1*L1 + y2*L2
            ax.fill_between(pts, y_par, alpha=0.28, color="#FCD34D", zorder=1)
            ax.plot(pts, y_par, color="#FCD34D", linewidth=0.7,
                    alpha=0.6, zorder=2)

        # Nodos compuesto
        x_nodes = np.array([a + i * h for i in range(n + 1)])
        y_nodes = np.array([f(xi) for xi in x_nodes])
        ax.vlines(x_nodes, 0, y_nodes, colors="#94A3B8",
                  linewidth=0.6, linestyle=":", zorder=2)
        ax.scatter(x_nodes, y_nodes, color="#FCD34D",
                   s=28, zorder=5, label=f"Nodos compuesto (n={n})")

        # ── Punto medio (simple) ─────────────────────────────────────────────
        xm = (a + b) / 2.0
        ym = f(xm)
        ax.scatter([a, xm, b], [f(a), ym, f(b)],
                   color=PINK, s=60, zorder=6,
                   marker="D", label="Nodos simple (n=2)")

        # Anotaciones de resultados
        ax.set_title(
            f"Simple = {res_simple:.6f}   |   Compuesto (n={n}) = {res_comp:.6f}",
            color=WHITE, fontsize=9, pad=8)

        ax.axhline(0, color="#2D4A72", linewidth=0.8)
        ax.grid(True, color="#1E3A5F", linewidth=0.5, alpha=0.7)
        ax.legend(fontsize=8, facecolor="#0F1C30",
                  edgecolor="#2D4A72", labelcolor=OFFWHITE,
                  loc="upper right")

        self._fig.tight_layout(pad=1.8)
        self._canvas.draw()