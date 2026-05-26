import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

from numerical_engine import (
    safe_function,
    simpson_one_third
)

# General Config
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
# Clase la buena buena
class SimpsonApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window config
        self.title("Proyecto Final - Simpson 1/3")
        self.geometry("900x650")
        
        icon = tk.PhotoImage(file='simpson.png')
        self.iconphoto(True,icon)

        # Title config
        title = ctk.CTkLabel(
            self,
            text="Método de Simpson 1/3",
            font=("Baskerville", 30, "bold")
        )
        title.pack(pady=20)

        subtitle = ctk.CTkLabel(
            self,
            text="Aproximación Numérica de Integrales Definidas",
            font=("Baskerville", 16)
        )
        subtitle.pack(pady=5)

        # Frame cnfig
        frame = ctk.CTkFrame(
            self,
            fg_color="#3A3A3A",
            corner_radius=20
        )
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Input config for parameters
        function_label = ctk.CTkLabel(
            frame,
            text="Función f(x):"
        )
        function_label.grid(row=0, column=0, padx=10, pady=10)

        self.function_entry = ctk.CTkEntry(
            frame,
            width=300,
            placeholder_text="Ejemplo: sin(x) + x**2"
        )
        self.function_entry.grid(row=0, column=1, padx=10, pady=10)

        label_a = ctk.CTkLabel(frame, text="Límite inferior a:")
        label_a.grid(row=1, column=0, padx=10, pady=10)

        self.entry_a = ctk.CTkEntry(frame)
        self.entry_a.grid(row=1, column=1, padx=10, pady=10)

        label_b = ctk.CTkLabel(frame, text="Límite superior b:")
        label_b.grid(row=2, column=0, padx=10, pady=10)

        self.entry_b = ctk.CTkEntry(frame)
        self.entry_b.grid(row=2, column=1, padx=10, pady=10)

        label_n = ctk.CTkLabel(frame, text="Número de segmentos n:")
        label_n.grid(row=3, column=0, padx=10, pady=10)

        self.entry_n = ctk.CTkEntry(frame)
        self.entry_n.grid(row=3, column=1, padx=10, pady=10)

        # Botonsito
        calculate_button = ctk.CTkButton(
        frame,
        text="Calcular Integral",
        command=self.calculate_integral,

        fg_color="#EABEC3",
        hover_color="#D89CA4",
        text_color="black",

        corner_radius=15,
        height=40,
        font=("Baskerville", 15, "bold")
        )

        calculate_button.grid(row=4, column=0, columnspan=2, pady=20)

        # Results
        self.result_label = ctk.CTkLabel(
            frame,
            text="Resultado aparecerá aquí.",
            font=("Arial", 15)
        )

        self.result_label.grid(
            row=5,
            column=0,
            columnspan=2,
            pady=20
        )

    # Main function
    def calculate_integral(self):

        try:
            # Get data
            function_text = self.function_entry.get()

            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            n = int(self.entry_n.get())

            # Validations iykyk
            if n <= 0:
                raise ValueError("n debe ser positivo.")

            # Google translator moment
            f = safe_function(function_text)

            # Call Simpson
            result, execution_time = simpson_one_third(
                f,
                a,
                b,
                n
            )

            # Show, don't tell (results)
            self.result_label.configure(
                text=
                f"Integral ≈ {result:.6f}\n"
                f"Tiempo: {execution_time:.2f} microsegundos"
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )