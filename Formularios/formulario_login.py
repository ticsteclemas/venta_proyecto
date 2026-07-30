import tkinter as tk
from tkinter import ttk, messagebox
import Util.generico as utl
from Modulo.Login import Login
from Formularios.Menu_principal import MainMenu

class FormLoginDesigner:

    def __init__(self):
         self.ventana = tk.Tk()
         self._configurar_ventana()
         self._crear_variables()
         self._crear_widgets()
         self._eventos()
         self.ventana.mainloop()

    def _configurar_ventana(self):
        self.ventana.title("Inicio de sesión")
        self.ventana.config(bg="#fcfcfc")
        self.ventana.resizable(False, False)
        utl.centrar_ventana(self.ventana, 500, 700)


    def _crear_variables(self):
        self.usuario_var = tk.StringVar(value="root")
        self.password_var = tk.StringVar()


    def _crear_widgets(self):
        # Frame principal
        frame_principal = tk.Frame(self.ventana, bg="#fcfcfc")
        frame_principal.pack(expand=True, fill="both")

        # Frame logo
        frame_logo = tk.Frame(frame_principal, bg="#3a7ff6", width=250)
        frame_logo.pack(side="left", fill="both")

        logo = utl.leer_imagen("./imagenes/logo.png", (180, 180))
        label_logo = tk.Label(frame_logo, image=logo, bg="#3a7ff6")
        label_logo.image = logo
        label_logo.pack(expand=True)

        # Frame formulario
        frame_form = tk.Frame(frame_principal, bg="#fcfcfc")
        frame_form.pack(side="right", expand=True, fill="both", padx=20)

        tk.Label(frame_form, text="Inicio de sesión", font=("Times", 26),
                 fg="#666a88", bg="#fcfcfc").pack(pady=30)

        tk.Label(frame_form, text="Usuario", bg="#fcfcfc").pack(anchor="w")
        ttk.Entry(frame_form, textvariable=self.usuario_var,
                  font=("Times", 14)).pack(fill="x", pady=10)

        tk.Label(frame_form, text="Contraseña", bg="#fcfcfc").pack(anchor="w")
        ttk.Entry(frame_form, textvariable=self.password_var,
                  show="*", font=("Times", 14)).pack(fill="x", pady=10)

        tk.Button(frame_form, text="Iniciar sesión", bg="#3a7ff6",
                  fg="white", bd=0, font=("Times", 15),
                  command=self.verificar).pack(fill="x", pady=20)

    def _eventos(self):
        self.ventana.bind("<Return>", lambda e: self.verificar())

    def verificar(self):
        usuario = self.usuario_var.get()
        password = self.password_var.get()

        login = Login(usuario, password)
        print(usuario, password)
        datos_usuarios=login.validar()
        if datos_usuarios:
            rol = datos_usuarios["rol"]
            nombres = datos_usuarios["nombres"]
            apellidos = datos_usuarios["apellidos"]
            messagebox.showinfo("Acceso correcto", f"Bienvenido al sistema {nombres} {apellidos}")
            self.ventana.destroy()

            app = MainMenu(nombres=nombres,apellidos=apellidos, rol=rol, icons_dir="assets/icons")
            app.mainloop()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")


