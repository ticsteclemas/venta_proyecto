import tkinter as tk
from tkinter import ttk, messagebox


class ProductosView(ttk.Frame):


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

        # Estado
        self.id_seleccionado = None
        self._auto_id = 3  # siguiente id simulado

        # Datos de ejemplo (simula BD)
        self.data = [
            {"id_productos": 1, "marca": "sprite", "stock": 30, "precio": 1.5},
            {"id_productos": 2, "marca": "coca cola", "stock": 15, "precio": 2.8},
        ]

        self._build_ui()
        self._refresh_table()

    # ---------------- UI ----------------
    def _build_ui(self):
        root = ttk.Frame(self)
        root.pack(fill="both", expand=True)

        # Header interno
        header = tk.Frame(root, bg=self.COL_PANEL, padx=16, pady=12)
        header.pack(fill="x", pady=(0, 14))

        tk.Label(
            header, text="Módulo: Productos",
            bg=self.COL_PANEL, fg=self.COL_TEXT,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Gestión de productos (id_productos, marca, stock, precio).",
            bg=self.COL_PANEL, fg=self.COL_MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        # Cuerpo 2 columnas
        body = tk.Frame(root, bg=self.COL_BG)
        body.pack(fill="both", expand=True)

        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # -------- IZQUIERDA: formulario --------
        left = tk.Frame(body, bg=self.COL_BG)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 14))

        form_card = tk.Frame(left, bg=self.COL_CARD, padx=14, pady=14)
        form_card.pack(fill="x")

        tk.Label(
            form_card, text="Formulario",
            bg=self.COL_CARD, fg=self.COL_TEXT,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            form_card, text="Seleccione un producto en la tabla para editar.",
            bg=self.COL_CARD, fg=self.COL_MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(2, 10))

        # Variables
        self.var_id = tk.StringVar(value="(auto)")
        self.var_marca = tk.StringVar()
        self.var_stock = tk.StringVar()
        self.var_precio = tk.StringVar()

        grid = tk.Frame(form_card, bg=self.COL_CARD)
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=0)
        grid.grid_columnconfigure(1, weight=1)

        def lbl(txt):
            return tk.Label(grid, text=txt, bg=self.COL_CARD, fg=self.COL_MUTED, font=("Segoe UI", 9))

        # id_productos (solo lectura)
        lbl("ID (id_productos)").grid(row=0, column=0, sticky="w", pady=6)
        e_id = ttk.Entry(grid, textvariable=self.var_id, width=26)
        e_id.grid(row=0, column=1, sticky="ew", pady=6, padx=(10, 0))
        e_id.configure(state="disabled")

        # marca
        lbl("Marca").grid(row=1, column=0, sticky="w", pady=6)
        self.ent_marca = ttk.Entry(grid, textvariable=self.var_marca, width=26)
        self.ent_marca.grid(row=1, column=1, sticky="ew", pady=6, padx=(10, 0))

        # stock
        lbl("Stock").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(grid, textvariable=self.var_stock, width=10).grid(row=2, column=1, sticky="w", pady=6, padx=(10, 0))

        # precio
        lbl("Precio").grid(row=3, column=0, sticky="w", pady=6)
        ttk.Entry(grid, textvariable=self.var_precio, width=10).grid(row=3, column=1, sticky="w", pady=6, padx=(10, 0))

        # Botonera
        btns = tk.Frame(form_card, bg=self.COL_CARD)
        btns.pack(fill="x", pady=(14, 0))

        self._btn(btns, "Guardar", self._save).pack(fill="x", pady=4)
        self._btn(btns, "Actualizar", self._update).pack(fill="x", pady=4)
        self._btn(btns, "Eliminar", self._delete).pack(fill="x", pady=4)
        self._btn(btns, "Limpiar", self._clear).pack(fill="x", pady=4)

        # -------- DERECHA: tabla + búsqueda --------
        right = tk.Frame(body, bg=self.COL_BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        topbar = tk.Frame(right, bg=self.COL_BG)
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        topbar.grid_columnconfigure(1, weight=1)

        tk.Label(topbar, text="Buscar:", bg=self.COL_BG, fg=self.COL_MUTED, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
        self.var_buscar = tk.StringVar()

        ttk.Entry(topbar, textvariable=self.var_buscar).grid(row=0, column=1, sticky="ew", padx=(8, 8))

        self._btn_small(topbar, "Filtrar", self._filter).grid(row=0, column=2, padx=(0, 6))
        self._btn_small(topbar, "Ver todo", self._refresh_table).grid(row=0, column=3)

        table_card = tk.Frame(right, bg=self.COL_CARD, padx=12, pady=12)
        table_card.grid(row=1, column=0, sticky="nsew")

        tk.Label(
            table_card, text="Listado de productos",
            bg=self.COL_CARD, fg=self.COL_TEXT,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            table_card, text="Estructura real: id_productos, marca, stock, precio.",
            bg=self.COL_CARD, fg=self.COL_MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(2, 10))




        cols = ("id_productos","marca", "stock", "precio")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings", height=14)
        self.tree.pack(side="left", fill="both", expand=True)

        vs = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        vs.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vs.set)

        self.tree.heading("id_productos", text="ID")
        self.tree.heading("marca", text="Marca")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("precio", text="Precio")


        self.tree.column("id_productos", width=80, anchor="center")
        self.tree.column("marca", width=300, anchor="w")
        self.tree.column("stock", width=90, anchor="center")
        self.tree.column("precio", width=90, anchor="center")


        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        self.ent_marca.focus_set()

    # -------- botones estilo ----------
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

    # ---------------- tabla ----------------
    def _refresh_table(self):
        self._fill_table(self.data)

    def _fill_table(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in rows:
            self.tree.insert(
                "", "end",
                values=(p["id_productos"], p["marca"], p["stock"], f'{p["precio"]:.2f}')
            )

    def _filter(self):
        q = (self.var_buscar.get() or "").strip().lower()
        if not q:
            self._refresh_table()
            return

        filtrados = []
        for p in self.data:
            if q in str(p["id_productos"]).lower() or q in p["marca"].lower():
                filtrados.append(p)

        self._fill_table(filtrados)

    # ---------------- selección ----------------
    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return

        values = self.tree.item(sel[0], "values")
        self.id_seleccionado = int(values[0])

        self.var_id.set(values[0])
        self.var_marca.set(values[1])
        self.var_stock.set(values[2])
        self.var_precio.set(values[3])

    # ---------------- CRUD (sin validaciones) ----------------
    def _clear(self):
        self.id_seleccionado = None
        self.var_id.set("(auto)")
        self.var_marca.set("")
        self.var_stock.set("")
        self.var_precio.set("")
        self.tree.selection_remove(self.tree.selection())
        self.ent_marca.focus_set()

    def _save(self):
        nuevo = {
            "id_productos": self._auto_id,
            "marca": self.var_marca.get(),
            "stock": int(self.var_stock.get() or 0),
            "precio": float(self.var_precio.get() or 0),
        }
        self._auto_id += 1
        self.data.append(nuevo)
        self._refresh_table()
        self._clear()
        messagebox.showinfo("Productos", "Producto guardado (simulado).")

    def _update(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Productos", "Seleccione un producto de la tabla para actualizar.")
            return

        for p in self.data:
            if p["id_productos"] == self.id_seleccionado:
                p["marca"] = self.var_marca.get()
                p["stock"] = int(self.var_stock.get() or 0)
                p["precio"] = float(self.var_precio.get() or 0)
                break

        self._refresh_table()
        self._clear()
        messagebox.showinfo("Productos", "Producto actualizado (simulado).")

    def _delete(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Productos", "Seleccione un producto de la tabla para eliminar.")
            return

        if not messagebox.askyesno("Confirmación", "¿Desea eliminar este producto?"):
            return

        self.data = [p for p in self.data if p["id_productos"] != self.id_seleccionado]
        self._refresh_table()
        self._clear()
        messagebox.showinfo("Productos", "Producto eliminado (simulado).")
