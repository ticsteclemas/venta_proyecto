import tkinter as tk
from tkinter import ttk, messagebox
from Modulo.cliente import *
class ClientesView(ttk.Frame):
    def __init__(self, parent, palette=None):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        palette = palette or {}
        self.COL_BG = palette.get("COL_BG", "#0f172a")
        self.COL_PANEL = palette.get("COL_PANEL", "#111c3a")
        self.COL_CARD = palette.get("COL_CARD", "#0b1a3a")
        self.COL_TEXT = palette.get("COL_TEXT", "#e5e7eb")
        self.COL_MUTED = palette.get("COL_MUTED", "#94a3b8")
        self.COL_ACCENT = palette.get("COL_ACCENT", "#38bdf8")

        self._build_ui()

    def _build_ui(self):
        #frame principal
        root = tk.Frame(self, bg=self.COL_BG)
        root.pack(fill="both", expand=True)

        # Header interno
        header = tk.Frame(root, bg=self.COL_PANEL, padx=16, pady=12)
        header.pack(fill="x", pady=(0, 14))

        #etiqueta Módulo de Clientes
        tk.Label(
            header, text="Módulo: Clientes",
            bg=self.COL_PANEL, fg=self.COL_TEXT,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")

        tk.Label(
            header, text="Gestión de clientes (id, Cédula, Nombre, Apellidos)",
            bg=self.COL_PANEL, fg=self.COL_TEXT,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(10,0))

        # Cuerpo 2 columnas
        body = tk.Frame(root, bg=self.COL_BG)
        body.pack(fill="both", expand=True)

        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        #left
        left = tk.Frame(body, bg=self.COL_BG)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 14))

        form_card = tk.Frame(left, bg=self.COL_CARD, padx=14, pady=14)
        form_card.pack(fill="x")

        tk.Label(
            form_card, text="Formulario",
            bg=self.COL_CARD, fg=self.COL_TEXT,
            font=("Segoe UI", 12,"bold")
        ).pack(anchor="w")



        grid = tk.Frame(form_card, bg=self.COL_CARD)
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=0)
        grid.grid_columnconfigure(1, weight=1)

        # Variables
        self.var_id = tk.StringVar(value="(auto)")
        self.cedula = tk.StringVar()
        self.nombres = tk.StringVar()
        self.apellidos = tk.StringVar()

        def lbl(txt):
            return tk.Label(grid, text=txt, bg=self.COL_CARD, fg=self.COL_MUTED, font=("Segoe UI", 9))

        lbl("ID (id_clientes)").grid(row=0, column=0, sticky="w", pady=(0, 5))
        e_id = ttk.Entry(grid, textvariable=self.var_id, width=26)
        e_id.grid(row=0, column=1, sticky="w", pady=6, padx=(10, 0))
        e_id.configure(state="disabled")

        lbl("Cédula").grid(row=1, column=0, sticky="w", pady=(5, 5))
        e_cedula = ttk.Entry(grid, textvariable=self.cedula, width=26)
        e_cedula.grid(row=1, column=1, sticky="w", pady=6, padx=(10, 0))

        lbl("Nombres").grid(row=2, column=0, sticky="w", pady=(5, 5))
        e_nombres=ttk.Entry(grid, textvariable=self.nombres, width=26)
        e_nombres.grid(row=2, column=1, sticky="w", pady=6, padx=(10, 0))

        lbl("Apellidos").grid(row=3, column=0, sticky="w", pady=(5, 5))
        e_apellidos = ttk.Entry(grid, textvariable=self.apellidos, width=26)
        e_apellidos.grid(row=3, column=1, sticky="w", pady=6, padx=(10, 0))

        #grupos de botones
        btns = tk.Frame(form_card, bg=self.COL_CARD)
        btns.pack(fill="x", pady=(14, 0))

        self._btn(btns, "Guardar", command=self._guardar_cliente).pack(fill="x", pady=4)
        self._btn(btns, "Actualizar", command=self).pack(fill="x", pady=4)
        self._btn(btns, "Eliminar", command=self).pack(fill="x", pady=4)
        self._btn(btns, "Limpiar", command=self._limpiar_campos).pack(fill="x", pady=4)

        # -------- DERECHA: tabla + búsqueda --------
        right = tk.Frame(body, bg=self.COL_BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        topbar = tk.Frame(right, bg=self.COL_BG)
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        topbar.grid_columnconfigure(1, weight=1)

        tk.Label(topbar, text="Buscar:", bg=self.COL_BG, fg=self.COL_MUTED, font=("Segoe UI", 10)).grid(row=0, column=0,
                                                                                 sticky="w")
        self.var_buscar = tk.StringVar()

        #Barra buscar
        ttk.Entry(topbar, textvariable=self.var_buscar).grid(row=0, column=1, sticky="ew", padx=(8, 8))

        self._btn_small(topbar, "Filtrar", self._filtrar_cliente).grid(row=0, column=2, padx=(0, 6))
        self._btn_small(topbar, "Refrescar", self._cargar_tabla).grid(row=0, column=3, padx=(0, 6))


        #frame o contenedor para la presentación de los datos
        table_card = tk.Frame(right, bg=self.COL_CARD, padx=12, pady=12)
        table_card.grid(row=1, column=0, sticky="nsew")

        cols = ("id_clientes", "Cédula", "Nombres", "Apellidos")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings", height=14)
        self.tree.pack(side="left", fill="both", expand=True)

        vs = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        vs.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vs.set)

        self.tree.heading("id_clientes", text="ID_CLIENTES")
        self.tree.heading("Cédula", text="Cédula")
        self.tree.heading("Nombres", text="Nombres")
        self.tree.heading("Apellidos", text="Apellidos")

        self.tree.column("id_clientes", width=80, anchor="center")
        self.tree.column("Cédula", width=80, anchor="center")
        self.tree.column("Nombres", width=80, anchor="center")
        self.tree.column("Apellidos", width=80, anchor="center")

        self._cargar_tabla()
        e_cedula.focus_set()







    def _btn(self, parent, text, command, ghost=False):
        if not ghost:
            return tk.Button(
                parent, text=text, command=command,
                bg=self.COL_ACCENT, fg="#001018",
                relief="flat", padx=14, pady=10,
                cursor="hand2", font=("Segoe UI", 10, "bold"),
                activebackground="#7dd3fc", activeforeground="#001018"
            )
        return tk.Button(
            parent, text=text, command=command,
            bg=self.COL_PANEL, fg=self.COL_TEXT,
            relief="flat", padx=14, pady=10,
            cursor="hand2", font=("Segoe UI", 10, "bold"),
            activebackground=self.COL_CARD, activeforeground=self.COL_TEXT
        )

    def _btn_small(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command,
            bg=self.COL_PANEL, fg=self.COL_TEXT,
            relief="flat", padx=10, pady=6,
            cursor="hand2", font=("Segoe UI", 9, "bold"),
            activebackground=self.COL_CARD, activeforeground=self.COL_TEXT
        )

    def _limpiar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _cargar_tabla(self):
        clientes = listar_clientes()
        self._limpiar_tabla()
        for c in clientes:
            self.tree.insert("", "end",
                             values=(c[0],
                                     c[1],
                                     c[2],
                                     c[3]))
    def _filtrar_cliente(self):
        q=(self.var_buscar.get() or "").strip()
        clientes = buscar_clientes(q)
        self._limpiar_tabla()
        for c in clientes:
            self.tree.insert("", "end",
                             values=(c[0],
                                     c[1],
                                     c[2],
                                     c[3]))
    def _guardar_cliente(self):
        cedula = self.cedula.get()
        nombres = self.nombres.get()
        apellidos = self.apellidos.get()

        insertar_clientes(cedula, nombres, apellidos)
        messagebox.showinfo("REGISTRO GUARDADO",
                            f" El cliente {nombres} {apellidos} se ha guardado correctamente ")
        self._cargar_tabla()
        self._limpiar_campos()

    def _limpiar_campos(self):
        self.var_id.set("Auto")
        self.cedula.set("")
        self.nombres.set("")
        self.apellidos.set("")




































if __name__ == "__main__":
    roo = tk.Tk()
    roo.title("Prueba clientes")
    roo.geometry("1100x650")
    ClientesView(roo, palette=None)
    roo.mainloop()