import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import json
from datetime import datetime

def centrar_ventana(ventana):
    ventana.update_idletasks()

    ancho_ventana = ventana.winfo_width()
    alto_ventana = ventana.winfo_height()

    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()

    x = int((ancho_pantalla - ancho_ventana) / 2)
    y = int((alto_pantalla - alto_ventana) / 2)

    ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")


archivo = "tareas.json"
fondo_config = "fondo_config.json"
tareas = []

imagen_fondo_original = None
fondo_tk = None


# Fondo de pantalla
def guardar_ruta_fondo(ruta):
    with open(fondo_config, "w", encoding="utf-8") as f:
        json.dump({"ruta_fondo": ruta}, f)

def cargar_ruta_fondo():
    try:
        with open(fondo_config, "r", encoding="utf-8") as f:
            datos = json.load(f)
            return datos.get("ruta_fondo")
    except Exception:
        return None

def cambiar_fondo():
    global imagen_fondo_original
    ruta_imagen = filedialog.askopenfilename(
        title="Seleccionar imagen de fondo",
        filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.gif")]
    )
    if ruta_imagen:
        try:
            imagen_fondo_original = Image.open(ruta_imagen)
            redimensionar_fondo()
            guardar_ruta_fondo(ruta_imagen)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}")

def quitar_fondo():
    global imagen_fondo_original, fondo_tk
    imagen_fondo_original = None
    fondo_tk = None
    canvas.delete("fondo")
    guardar_ruta_fondo("")

def redimensionar_fondo(event=None):
    global fondo_tk, imagen_fondo_original
    if imagen_fondo_original is None:
        canvas.delete("fondo")
        return

    ancho = ventana.winfo_width()
    alto = ventana.winfo_height()

    if ancho < 2 or alto < 2:
        return

    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        resample_filter = Image.ANTIALIAS

    img = imagen_fondo_original.resize((ancho, alto), resample_filter)
    fondo_tk = ImageTk.PhotoImage(img)
    canvas.delete("fondo")
    canvas.create_image(0, 0, image=fondo_tk, anchor="nw", tags="fondo")

# === Funciones para tareas ===
def cargar_tareas():
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
            if isinstance(datos, list):
                return datos
            return []
    except Exception:
        return []

def guardar_tareas():
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(tareas, f, indent=4, ensure_ascii=False)

def actualizar_lista():
    lista.delete(0, tk.END)
    for i, t in enumerate(tareas):
        estado = "✅" if t["estado"] == "completada" else "⏳"
        lista.insert(tk.END, f"{i+1}. {estado} {t.get('titulo', 'Sin título')} - {t.get('prioridad', 'Sin prioridad')} - {t.get('fecha_limite', 'Sin fecha')}")

def verificar_notificaciones():
    hoy = datetime.now().date()
    notificaciones = []

    for tarea in tareas:
        if tarea.get("estado") == "completada":
            continue

        fecha_str = tarea.get("fecha_limite", "").strip()
        if not fecha_str:
            continue

        try:
            fecha_limite = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        dias_restantes = (fecha_limite - hoy).days

        # Inicializar banderas
        tarea.setdefault("notificado_1_dia", False)
        tarea.setdefault("notificado_vencido", False)

        # 🔔 Falta 1 día
        if dias_restantes == 1 and not tarea["notificado_1_dia"]:
            notificaciones.append((
                "warning",
                "⏳ Tarea por vencer",
                f"La tarea:\n\n'{tarea['titulo']}'\n\nVence Mañana."
            ))
            tarea["notificado_1_dia"] = True

        # ⛔ Vencida
        if dias_restantes <= 0 and not tarea["notificado_vencido"]:
            notificaciones.append((
                "error",
                "⛔ Tiempo agotado",
                f"La tarea:\n\n'{tarea['titulo']}'\n\nha alcanzado o superado su fecha límite."
            ))
            tarea["notificado_vencido"] = True

    if notificaciones:
        guardar_tareas()
        mostrar_notificaciones_en_cadena(notificaciones)

    ventana.after(60000, verificar_notificaciones)

def mostrar_notificaciones_en_cadena(lista_notificaciones):
    if not lista_notificaciones:
        return

    tipo, titulo, mensaje = lista_notificaciones.pop(0)

    if tipo == "warning":
        messagebox.showwarning(titulo, mensaje)
    else:
        messagebox.showerror(titulo, mensaje)

    # Mostrar la siguiente después de cerrar esta
    ventana.after(200, lambda: mostrar_notificaciones_en_cadena(lista_notificaciones))


subtareas_mostradas = {}

def toggle_subtareas(event):
    sel = lista.curselection()
    if not sel:
        return
    idx = sel[0]

    for tarea_idx, subt_idxs in subtareas_mostradas.items():
        if idx in subt_idxs:
            subt_idx_en_tarea = subt_idxs.index(idx)
            tarea = tareas[tarea_idx]
            subtarea = tarea["subtareas"][subt_idx_en_tarea]
            if subtarea["estado"] == "pendiente":
                subtarea["estado"] = "completada"
            else:
                subtarea["estado"] = "pendiente"
            guardar_tareas()
            actualizar_lista()
            abrir_subtareas(tarea_idx)
            return

    # Si ya desplegadas, ocultar subtareas
    if idx in subtareas_mostradas:
        ocultar_subtareas(idx)
    else:
        abrir_subtareas(idx)

def abrir_subtareas(idx):
    tarea = tareas[idx]
    subtareas = tarea.get("subtareas", [])
    if not subtareas:
        return

    subt_idxs = []

    for i, sub in enumerate(subtareas):
        estado = "✅" if sub["estado"] == "completada" else "⏳"
        texto = f"     {estado} {sub['texto']}"
        lista.insert(idx + 1 + i, texto)
        subt_idxs.append(idx + 1 + i)

    subtareas_mostradas[idx] = subt_idxs

def ocultar_subtareas(idx):
    subt_idxs = subtareas_mostradas.pop(idx, [])
    for i in reversed(subt_idxs):
        lista.delete(i)

def agregar_tarea():
    ventana_modal = tk.Toplevel(ventana)
    ventana_modal.title("Agregar Nueva Tarea")
    ventana_modal.geometry("400x580")
    ventana_modal.resizable(False, False)
    ventana_modal.grab_set()
    ventana_modal.transient(ventana)
    ventana_modal.configure(bg="#f0f0f0")

    label_style = {"font": ("Segoe UI", 11), "bg": "#f0f0f0"}

    tk.Label(ventana_modal, text="Título:", **label_style).pack(pady=(15, 5), anchor="w", padx=20)
    entrada_titulo = tk.Entry(ventana_modal, font=("Segoe UI", 12), width=35, relief="groove", bd=2)
    entrada_titulo.pack(pady=(0, 10), padx=20)

    tk.Label(ventana_modal, text="Descripción:", **label_style).pack(pady=(5, 5), anchor="w", padx=20)
    entrada_descripcion = tk.Entry(ventana_modal, font=("Segoe UI", 12), width=35, relief="groove", bd=2)
    entrada_descripcion.pack(pady=(0, 10), padx=20)

    tk.Label(ventana_modal, text="Subtareas (una por línea):", **label_style).pack(pady=(5, 5), anchor="w", padx=20)
    entrada_subtareas = tk.Text(ventana_modal, font=("Segoe UI", 11), height=5, width=35, relief="groove", bd=2)
    entrada_subtareas.pack(pady=(0, 10), padx=20)

    tk.Label(ventana_modal, text="Fecha Límite (AAAA-MM-DD):", **label_style).pack(pady=(5, 5), anchor="w", padx=20)
    entrada_fecha = tk.Entry(ventana_modal, font=("Segoe UI", 12), width=35, relief="groove", bd=2)
    entrada_fecha.pack(pady=(0, 10), padx=20)

    tk.Label(ventana_modal, text="Prioridad:", **label_style).pack(pady=(5, 5), anchor="w", padx=20)
    prioridad_var = tk.StringVar(value="Media")
    frame_prioridad = tk.Frame(ventana_modal, bg="#f0f0f0")
    frame_prioridad.pack(pady=(0, 15), padx=20, anchor="w")
    for p in ["Alta", "Media", "Baja"]:
        rb = tk.Radiobutton(frame_prioridad, text=p, variable=prioridad_var, value=p, font=("Segoe UI", 11), bg="#f0f0f0")
        rb.pack(side="left", padx=10)

    def guardar():
        titulo = entrada_titulo.get().strip()
        if not titulo:
            messagebox.showwarning("Atención", "El título es obligatorio.")
            return
        descripcion = entrada_descripcion.get().strip()
        subtareas_texto = entrada_subtareas.get("1.0", tk.END).strip()
        lista_subtareas = [{"texto": s.strip(), "estado": "pendiente"} for s in subtareas_texto.split("\n") if s.strip()]
        fecha_limite = entrada_fecha.get().strip()
        prioridad = prioridad_var.get()

        nueva = {
            "titulo": titulo,
            "descripcion": descripcion,
            "subtareas": lista_subtareas,
            "fecha_limite": fecha_limite,
            "prioridad": prioridad,
            "estado": "pendiente",
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        tareas.append(nueva)
        guardar_tareas()
        actualizar_lista()
        ventana_modal.destroy()

    tk.Button(
        ventana_modal,
        text="Guardar",
        font=("Segoe UI", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        activebackground="#45a049",
        relief="flat",
        padx=15,
        pady=8,
        command=guardar
    ).pack(pady=(5, 20))

def ver_detalles():
    sel = lista.curselection()
    if not sel:
        messagebox.showwarning("Atención", "Selecciona una tarea")
        return

    t = tareas[sel[0]]

    detalle = tk.Toplevel(ventana)
    detalle.title("Detalles de la tarea")
    detalle.geometry("420x450")
    detalle.configure(bg="#f0f4f8")
    detalle.grab_set()

    frame = tk.Frame(detalle, bg="white", bd=2, relief="groove")
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    titulo = tk.Label(frame, text="📝 Detalles de la tarea", font=("Segoe UI", 14, "bold"), bg="white", fg="#333")
    titulo.pack(pady=(10, 20))

    def agregar_linea(etiqueta, valor):
        linea = tk.Frame(frame, bg="white")
        linea.pack(anchor="w", padx=15, pady=3)
        tk.Label(linea, text=f"{etiqueta}:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").pack(side="left")
        tk.Label(linea, text=valor or "—", font=("Segoe UI", 10), bg="white", fg="#222", wraplength=320, justify="left").pack(side="left")

    agregar_linea("Título", t['titulo'])
    agregar_linea("Descripción", t['descripcion'])
    agregar_linea("Fecha límite", t['fecha_limite'])
    agregar_linea("Prioridad", t['prioridad'])
    agregar_linea("Estado", t['estado'])
    agregar_linea("Creado", t['fecha_creacion'])

    if "subtareas" in t and t["subtareas"]:
        tk.Label(frame, text="Subtareas:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").pack(anchor="w", padx=15, pady=(10, 0))
        for s in t["subtareas"]:
            estado = "✅" if s["estado"] == "completada" else "⏳"
            texto = f"   {estado} {s['texto']}"
            tk.Label(frame, text=texto, font=("Segoe UI", 10), bg="white", fg="#333", wraplength=320, justify="left").pack(anchor="w", padx=25)

    tk.Button(detalle, text="Cerrar", font=("Segoe UI", 10), command=detalle.destroy, bg="#4a90e2", fg="white", relief="flat", padx=10, pady=5).pack(pady=10)

def marcar_completada():
    seleccion = lista.curselection()
    if not seleccion:
        messagebox.showwarning("Atención", "Seleccione una tarea")
        return
    i = seleccion[0]
    tareas[i]["estado"] = "completada"
    guardar_tareas()
    actualizar_lista()

def eliminar_tarea():
    seleccion = lista.curselection()
    if not seleccion:
        messagebox.showwarning("Atención", "Seleccione una tarea")
        return
    i = seleccion[0]
    confirmar = messagebox.askyesno("Eliminar", f"¿Eliminar la tarea '{tareas[i]['titulo']}'?")
    if confirmar:
        tareas.pop(i)
        guardar_tareas()
        actualizar_lista()

def editar_tarea():
    seleccion = lista.curselection()
    if not seleccion:
        messagebox.showwarning("Atención", "Seleccione una tarea")
        return
    i = seleccion[0]
    tarea = tareas[i]

    ventana_modal = tk.Toplevel(ventana)
    ventana_modal.title("Editar Tarea")
    ventana_modal.geometry("400x560")
    ventana_modal.resizable(False, False)
    ventana_modal.grab_set()
    ventana_modal.transient(ventana)
    ventana_modal.configure(bg="#f0f0f0")

    label_style = {"font": ("Segoe UI", 11), "bg": "#f0f0f0"}

    tk.Label(ventana_modal, text="Título:", **label_style).pack(pady=(15, 5), anchor="w", padx=20)
    entrada_titulo = tk.Entry(ventana_modal, font=("Segoe UI", 12), width=35, relief="groove", bd=2)
    entrada_titulo.insert(0, tarea["titulo"])
    entrada_titulo.pack(pady=(0, 10), padx=20)

    tk.Label(ventana_modal, text="Descripción:", **label_style).pack(pady=(5, 5), anchor="w", padx=20)
    entrada_descripcion = tk.Entry(ventana_modal, font=("Segoe UI", 12), width=35, relief="groove", bd=2)
    entrada_descripcion.insert(0, tarea["descripcion"])
    entrada_descripcion.pack(pady=(0, 10), padx=20)

    tk.Label(ventana_modal, text="Subtareas (una por línea):", **label_style).pack(pady=(5, 5), anchor="w", padx=20)
    entrada_subtareas = tk.Text(ventana_modal, font=("Segoe UI", 11), height=5, width=35, relief="groove", bd=2)
    if "subtareas" in tarea and tarea["subtareas"]:
        subtareas_texto = "\n".join([s["texto"] for s in tarea["subtareas"]])
    else:
        subtareas_texto = ""
    entrada_subtareas.insert("1.0", subtareas_texto)
    entrada_subtareas.pack(pady=(0, 10), padx=20)

    tk.Label(ventana_modal, text="Fecha Límite (AAAA-MM-DD):", **label_style).pack(pady=(5, 5), anchor="w", padx=20)
    entrada_fecha = tk.Entry(ventana_modal, font=("Segoe UI", 12), width=35, relief="groove", bd=2)
    entrada_fecha.insert(0, tarea["fecha_limite"])
    entrada_fecha.pack(pady=(0, 10), padx=20)

    tk.Label(ventana_modal, text="Prioridad:", **label_style).pack(pady=(5, 5), anchor="w", padx=20)
    prioridad_var = tk.StringVar(value=tarea.get("prioridad", "Media"))
    frame_prioridad = tk.Frame(ventana_modal, bg="#f0f0f0")
    frame_prioridad.pack(pady=(0, 15), padx=20, anchor="w")
    for p in ["Alta", "Media", "Baja"]:
        rb = tk.Radiobutton(frame_prioridad, text=p, variable=prioridad_var, value=p, font=("Segoe UI", 11), bg="#f0f0f0")
        rb.pack(side="left", padx=10)

    def guardar():
        nuevo_titulo = entrada_titulo.get().strip()
        if not nuevo_titulo:
            messagebox.showwarning("Atención", "El título es obligatorio.")
            return
        tarea["titulo"] = nuevo_titulo
        tarea["descripcion"] = entrada_descripcion.get().strip()
        subtareas_texto = entrada_subtareas.get("1.0", tk.END).strip()
        tarea["subtareas"] = [{"texto": s.strip(), "estado": "pendiente"} for s in subtareas_texto.split("\n") if s.strip()]
        tarea["fecha_limite"] = entrada_fecha.get().strip()
        tarea["prioridad"] = prioridad_var.get()
        guardar_tareas()
        actualizar_lista()
        ventana_modal.destroy()

    boton_guardar = tk.Button(
        ventana_modal,
        text="Guardar",
        font=("Segoe UI", 12, "bold"),
        bg="#2196F3",
        fg="white",
        activebackground="#1e88e5",
        relief="flat",
        padx=15,
        pady=8,
        command=guardar
    )
    boton_guardar.pack(pady=(5, 20))


# Función Filtro
def filtrar_tareas():
    ventana_filtro = tk.Toplevel(ventana)
    ventana_filtro.title("Filtrar y Ordenar Tareas")
    ventana_filtro.geometry("400x350")
    ventana_filtro.resizable(False, False)
    ventana_filtro.grab_set()
    ventana_filtro.transient(ventana)
    ventana_filtro.configure(bg="#f0f0f0")

    label_style = {"font": ("Segoe UI", 11), "bg": "#f0f0f0"}

    # Opciones de orden alfabético
    tk.Label(ventana_filtro, text="Ordenar por nombre A-Z:", **label_style).pack(pady=(15, 5), anchor="w", padx=20)
    orden_titulo_var = tk.StringVar(value="ninguno")
    frame_orden_titulo = tk.Frame(ventana_filtro, bg="#f0f0f0")
    frame_orden_titulo.pack(pady=(0, 10), padx=20, anchor="w")
    tk.Radiobutton(frame_orden_titulo, text="Ninguno", variable=orden_titulo_var, value="ninguno", font=("Segoe UI", 11), bg="#f0f0f0").pack(side="left", padx=5)
    tk.Radiobutton(frame_orden_titulo, text="Ascendente", variable=orden_titulo_var, value="asc", font=("Segoe UI", 11), bg="#f0f0f0").pack(side="left", padx=5)
    tk.Radiobutton(frame_orden_titulo, text="Descendente", variable=orden_titulo_var, value="desc", font=("Segoe UI", 11), bg="#f0f0f0").pack(side="left", padx=5)

    # Opciones de orden por fecha límite
    tk.Label(ventana_filtro, text="Ordenar por fecha límite:", **label_style).pack(pady=(15, 5), anchor="w", padx=20)
    orden_fecha_var = tk.StringVar(value="ninguno")
    frame_orden_fecha = tk.Frame(ventana_filtro, bg="#f0f0f0")
    frame_orden_fecha.pack(pady=(0, 10), padx=20, anchor="w")
    tk.Radiobutton(frame_orden_fecha, text="Ninguno", variable=orden_fecha_var, value="ninguno", font=("Segoe UI", 11), bg="#f0f0f0").pack(side="left", padx=5)
    tk.Radiobutton(frame_orden_fecha, text="Ascendente", variable=orden_fecha_var, value="asc", font=("Segoe UI", 11), bg="#f0f0f0").pack(side="left", padx=5)
    tk.Radiobutton(frame_orden_fecha, text="Descendente", variable=orden_fecha_var, value="desc", font=("Segoe UI", 11), bg="#f0f0f0").pack(side="left", padx=5)

    # Opciones de filtro por prioridad
    tk.Label(ventana_filtro, text="Filtrar por prioridad:", **label_style).pack(pady=(15, 5), anchor="w", padx=20)
    prioridad_filtro_var = tk.StringVar(value="Todas")
    frame_prioridad_filtro = tk.Frame(ventana_filtro, bg="#f0f0f0")
    frame_prioridad_filtro.pack(pady=(0, 10), padx=20, anchor="w")
    for p in ["Todas", "Alta", "Media", "Baja"]:
        tk.Radiobutton(frame_prioridad_filtro, text=p, variable=prioridad_filtro_var, value=p, font=("Segoe UI", 11), bg="#f0f0f0").pack(side="left", padx=5)

    def aplicar_filtros():
        global tareas
        # Crear copia para filtrar y ordenar
        tareas_filtradas = tareas[:]

        # Filtrar por prioridad
        prioridad_sel = prioridad_filtro_var.get()
        if prioridad_sel != "Todas":
            tareas_filtradas = [t for t in tareas_filtradas if t.get("prioridad", "") == prioridad_sel]

        # Ordenar por el título
        orden_titulo = orden_titulo_var.get()
        if orden_titulo != "ninguno":
            reverse = orden_titulo == "desc"
            tareas_filtradas.sort(key=lambda x: x.get("titulo", "").lower(), reverse=reverse)

        # Ordenar por fecha límite
        orden_fecha = orden_fecha_var.get()
        if orden_fecha != "ninguno":
            reverse = orden_fecha == "desc"
            def fecha_parse(fecha_str):
                try:
                    return datetime.strptime(fecha_str, "%Y-%m-%d")
                except:
                    return datetime.max  # tareas sin fecha al final
            tareas_filtradas.sort(key=lambda x: fecha_parse(x.get("fecha_limite", "")), reverse=reverse)

        # Actualizar la lista con tareas filtradas
        lista.delete(0, tk.END)
        for i, t in enumerate(tareas_filtradas):
            estado = "✅" if t["estado"] == "completada" else "⏳"
            lista.insert(tk.END, f"{i+1}. {estado} {t.get('titulo', 'Sin título')} - {t.get('prioridad', 'Sin prioridad')} - {t.get('fecha_limite', 'Sin fecha')}")

        ventana_filtro.destroy()

    boton_aplicar = tk.Button(
        ventana_filtro,
        text="Aplicar Filtros",
        font=("Segoe UI", 12, "bold"),
        bg="#2196F3",
        fg="white",
        activebackground="#1e88e5",
        relief="flat",
        padx=15,
        pady=8,
        command=aplicar_filtros
    )
    boton_aplicar.pack(pady=(20, 20))


#Interfaz gráfica principal del sitema
ventana = tk.Tk()
ventana.title("🗂️ Sistema de Gestión de Tareas Personal")
ventana.geometry("900x800")
ventana.resizable(True, True)

# 🔹 Centrar ventana según tamaño de pantalla
centrar_ventana(ventana)


canvas = tk.Canvas(ventana, width=900, height=600)
canvas.pack(fill="both", expand=True)

ruta_guardada = cargar_ruta_fondo()
if ruta_guardada:
    try:
        imagen_fondo_original = Image.open(ruta_guardada)
        redimensionar_fondo()
    except Exception:
        imagen_fondo_original = None
else:
    imagen_fondo_original = None

# Lista de tareas del sistema
frame_lista = tk.Frame(ventana)
canvas.create_window(450, 185, window=frame_lista)

scroll_y = tk.Scrollbar(frame_lista, orient="vertical")
scroll_x = tk.Scrollbar(frame_lista, orient="horizontal")

lista = tk.Listbox(
    frame_lista,
    width=90,
    height=18,
    font=("Arial", 12),
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

scroll_y.config(command=lista.yview)
scroll_x.config(command=lista.xview)

lista.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")

frame_lista.grid_rowconfigure(0, weight=1)
frame_lista.grid_columnconfigure(0, weight=1)

# Botones
botones = [
    ("Agregar Tarea", agregar_tarea),
    ("Ver Detalles", ver_detalles),
    ("Editar Tarea", editar_tarea),
    ("Marcar Completada", marcar_completada),
    ("Eliminar Tarea", eliminar_tarea),
    ("Filtrar Tareas", filtrar_tareas),
    ("Cambiar Fondo", cambiar_fondo),
    ("Salir", ventana.quit)
]

def on_enter(e):
    e.widget.config(bg="#ddd")

def on_leave(e):
    e.widget.config(bg="SystemButtonFace")

y_botones = 400
for texto, accion in botones:
    boton = tk.Button(ventana, text=texto, width=25, font=("Arial", 11), command=accion)
    boton.bind("<Enter>", on_enter)
    boton.bind("<Leave>", on_leave)
    canvas.create_window(450, y_botones, window=boton)

    # Botón para quitar fondo de pantalla
    if texto == "Cambiar Fondo":
        boton_quitar = tk.Button(
            ventana, text="🚫", font=("Arial", 11, "bold"),
            command=quitar_fondo, border=0, relief="flat", width=3, height=1
        )
        boton_quitar.bind("<Enter>", on_enter)
        boton_quitar.bind("<Leave>", on_leave)
        canvas.create_window(450 + 135, y_botones, window=boton_quitar)

    y_botones += 50

def scroll_mouse(event):
    lista.yview_scroll(int(-1 * (event.delta / 120)), "units")

lista.bind("<MouseWheel>", scroll_mouse)


ventana.bind("<Configure>", redimensionar_fondo)

tareas = cargar_tareas()
actualizar_lista()

# Doble Click A-Z
lista.bind("<Double-Button-1>", toggle_subtareas)

ventana.update()
centrar_ventana(ventana)

verificar_notificaciones()

ventana.mainloop()
