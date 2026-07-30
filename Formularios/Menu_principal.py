import tkinter as tk
from tkinter import ttk, messagebox
import os
import Util.generico as utl
import importlib
# Iconos PNG opcionales (recomendado)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class MainMenu(tk.Tk):

    def __init__(self, nombres, apellidos, rol, icons_dir="assets/icons"):
        super().__init__()

        # ✅ Tamaño del menú principal (ancho x alto)
        self.ANCHO = 1100
        self.ALTO = 650

        self.title("Sistema de Ventas - Menú Principal")



        # Paleta (sobria y combinable)
        self.COL_BG = "#0f172a"      # fondo general (azul muy oscuro)
        self.COL_PANEL = "#111c3a"   # paneles
        self.COL_SIDEBAR = "#0b1229" # sidebar
        self.COL_CARD = "#0b1a3a"    # tarjetas / contenedores
        self.COL_TEXT = "#e5e7eb"    # texto
        self.COL_MUTED = "#94a3b8"   # texto secundario
        self.COL_ACCENT = "#38bdf8"  # acento (celeste)
        self.COL_BTN = "#162957"     # botones sidebar
        self.COL_BTN_HOVER = "#1c3773"

        self.configure(bg=self.COL_BG)

        self.usuario = f"{nombres} {apellidos}".strip()
        self.rol = rol
        self.icons_dir = icons_dir
        self.icons = {}  # cache de imágenes Tk

        self._setup_style()
        self._build_layout()
        self._build_header()
        self._build_sidebar()
        self._build_content()

        # Pantalla inicial
        self.show_view("Inicio")

        utl.centrar_ventana(self, self.ALTO, self.ANCHO)

        self.module_routes = {
            "Productos": ("Formularios.formulario_productos", "ProductosView"),
            "Clientes": ("Formularios.formulario_clientes", "ClientesView"),
            "Usuarios": ("Formularios.formulario_usuarios", "UsuariosView"),
            "Ventas": ("Formularios.formulario_ventas", "VentasView"),
            "Reportes": ("Formularios.formulario_reportes", "ReportesView"),
            "Config.": ("Formularios.formulario_config", "ConfigView"),
        }


    def _setup_style(self):
        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=self.COL_BG)
        style.configure("Header.TFrame", background=self.COL_PANEL)
        style.configure("Sidebar.TFrame", background=self.COL_SIDEBAR)
        style.configure("Content.TFrame", background=self.COL_BG)

        style.configure("Title.TLabel", background=self.COL_PANEL, foreground=self.COL_TEXT,
                        font=("Segoe UI", 14, "bold"))
        style.configure("Info.TLabel", background=self.COL_PANEL, foreground=self.COL_MUTED,
                        font=("Segoe UI", 10))

        style.configure("Card.TFrame", background=self.COL_CARD)
        style.configure("CardTitle.TLabel", background=self.COL_CARD, foreground=self.COL_TEXT,
                        font=("Segoe UI", 12, "bold"))
        style.configure("CardText.TLabel", background=self.COL_CARD, foreground=self.COL_MUTED,
                        font=("Segoe UI", 10))

    def _build_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header = ttk.Frame(self, style="Header.TFrame", padding=(16, 10))
        self.header.grid(row=0, column=0, sticky="nsew")

        self.body = ttk.Frame(self, style="TFrame")
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)

        self.sidebar = ttk.Frame(self.body, style="Sidebar.TFrame", padding=(12, 12))
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.configure(width=260)

        self.content = ttk.Frame(self.body, style="Content.TFrame", padding=(16, 16))
        self.content.grid(row=0, column=1, sticky="nsew")

    def _build_header(self):
        self.header.grid_columnconfigure(0, weight=1)

        title = ttk.Label(self.header, text="Sistema de Ventas", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w")

        info = ttk.Label(
            self.header,
            text=f"Usuario: {self.usuario}  |  Rol: {self.rol}",
            style="Info.TLabel"
        )
        info.grid(row=1, column=0, sticky="w", pady=(2, 0))

        btn_salir = tk.Button(
            self.header,
            text="Salir",
            command=self._logout,
            bg=self.COL_ACCENT,
            fg="#001018",
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            activebackground="#7dd3fc",
            activeforeground="#001018"
        )
        btn_salir.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))

    def _build_sidebar(self):
        logo_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        logo_frame.pack(fill="x", pady=(0, 12))

        canvas = tk.Canvas(logo_frame, width=48, height=48, bg=self.COL_SIDEBAR,
                           highlightthickness=0)
        canvas.pack(side="left")
        canvas.create_oval(6, 6, 42, 42, fill=self.COL_ACCENT, outline="")
        canvas.create_text(24, 24, text="SV", fill="#001018", font=("Segoe UI", 12, "bold"))

        ttk.Label(
            logo_frame,
            text="Menú Principal",
            foreground=self.COL_TEXT,
            background=self.COL_SIDEBAR,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=10)

        self.menu_buttons = []

        items = [
            ("Inicio",    "home.png",     "🏠"),
            ("Usuarios",  "users.png",    "👤"),
            ("Clientes",  "clients.png",  "🧾"),
            ("Productos", "products.png", "📦"),
            ("Ventas",    "sales.png",    "💳"),
            ("Reportes",  "reports.png",  "📊"),
            ("Config.",   "settings.png", "⚙️"),
        ]

        for name, icon_file, fallback_emoji in items:
            if self.rol.lower()== "vendedor" and name=="Usuarios":
                continue

            btn = self._sidebar_button(
                text=name,
                icon_file=icon_file,
                fallback=fallback_emoji,
                command=lambda n=name: self.show_view(n)
            )
            btn.pack(fill="x", pady=6)
            self.menu_buttons.append(btn)

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", pady=14)

        foot = tk.Label(
            self.sidebar,
            text="© IST - TECLEMAS | v1.0",
            bg=self.COL_SIDEBAR,
            fg=self.COL_MUTED,
            font=("Segoe UI", 9)
        )
        foot.pack(side="bottom", pady=(8, 0))

    def _build_content(self):
        self.view_container = ttk.Frame(self.content, style="Content.TFrame")
        self.view_container.pack(fill="both", expand=True)

    # -------------------- BUTTON FACTORY --------------------
    def _sidebar_button(self, text, icon_file, fallback, command):
        img = self._load_icon(icon_file, size=(20, 20))
        label = f"  {text}" if img else f"{fallback}  {text}"

        btn = tk.Button(
            self.sidebar,
            text=label,
            image=img if img else None,
            compound="left",
            command=command,
            anchor="w",
            bg=self.COL_BTN,
            fg=self.COL_TEXT,
            relief="flat",
            padx=14,
            pady=10,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            activebackground=self.COL_BTN_HOVER,
            activeforeground=self.COL_TEXT
        )

        btn._icon_ref = img
        btn.bind("<Enter>", lambda e: btn.configure(bg=self.COL_BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.configure(bg=self.COL_BTN))
        return btn

    def _load_icon(self, filename, size=(20, 20)):
        if not PIL_AVAILABLE:
            return None

        path = os.path.join(self.icons_dir, filename)
        if not os.path.exists(path):
            return None

        key = (path, size)
        if key in self.icons:
            return self.icons[key]

        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize(size)
            tk_img = ImageTk.PhotoImage(img)
            self.icons[key] = tk_img
            return tk_img
        except Exception:
            return None

    # -------------------- NAVIGATION --------------------
    def show_view(self, name):
        for w in self.view_container.winfo_children():
            w.destroy()

        card = ttk.Frame(self.view_container, style="Card.TFrame", padding=(18, 18))
        card.pack(fill="both", expand=True)

        ttk.Label(card, text=name, style="CardTitle.TLabel").pack(anchor="w")

        description_map = {
            "Inicio": "Panel general. Aquí puedes mostrar métricas rápidas: ventas del día, stock bajo, etc.",
            "Usuarios": "Gestión de usuarios: crear, editar, roles/permisos, reset de contraseña.",
            "Clientes": "Gestión de clientes: registro, actualización de datos, historial de compras.",
            "Productos": "Gestión de productos: catálogo, stock, precios, estado (activo/inactivo).",
            "Ventas": "Registro de ventas: carrito, cálculo total, forma de pago, factura/recibo.",
            "Reportes": "Reportes: ventas por fecha, productos más vendidos, clientes frecuentes.",
            "Config.": "Configuraciones: parámetros del sistema, respaldos, conexión BD, etc."
        }

        ttk.Label(
            card,
            text=description_map.get(name, "Módulo en construcción."),
            style="CardText.TLabel",
            wraplength=800,
            justify="left"
        ).pack(anchor="w", pady=(10, 14))

        action_btn = tk.Button(
            card,
            text=f"Abrir módulo: {name}",
            #command=lambda: self._open_module(name),
            command=lambda n=name: self._open_module(n),
            bg=self.COL_ACCENT,
            fg="#001018",
            relief="flat",
            padx=14,
            pady=10,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            activebackground="#7dd3fc",
            activeforeground="#001018"
        )
        action_btn.pack(anchor="w")

    def _open_module(self, module_name):

        route = self.module_routes.get(module_name)

        if not route:
            messagebox.showinfo("Módulo", f"Módulo '{module_name}' en construcción.")
            return

        module_path, class_name = route

        try:
            mod = importlib.import_module(module_path)
            ViewClass = getattr(mod, class_name)

            win = tk.Toplevel(self)
            win.title(f"Módulo: {module_name}")
            win.geometry("1100x650")
            win.configure(bg=self.COL_BG)

            palette = {
                "COL_BG": self.COL_BG,
                "COL_PANEL": self.COL_PANEL,
                "COL_CARD": self.COL_CARD,
                "COL_TEXT": self.COL_TEXT,
                "COL_MUTED": self.COL_MUTED,
                "COL_ACCENT": self.COL_ACCENT,
            }

            ViewClass(win, palette=palette)

        except Exception as e:
            messagebox.showerror("Error abriendo módulo", str(e))
        #messagebox.showinfo("Módulo", f"Aquí abrirías el módulo: {module_name}")

    def _logout(self):
        self.destroy()






