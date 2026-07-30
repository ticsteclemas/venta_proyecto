import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import json
from datetime import datetime


class OrganizadorTareasApp:
    def __init__(self):
        self.archivo = "tareas.json"
        self.fondo_config = "fondo_config.json"

        self.tareas = []
        self.subtareas_mostradas = {}

        self.imagen_fondo_original = None
        self.fondo_tk = None

        self.ventana = tk.Tk()
        self.ventana.title("🗂️ Sistema de Gestión de Tareas Personal")
        self.ventana.geometry("900x800")
        self.ventana.resizable(True, True)

        self._crear_ui()
        self._cargar_fondo_guardado()

        self.tareas = self._cargar_tareas()
        self._actualizar_lista()

        self.ventana.bind("<Configure>", self._redimensionar_fondo)
        self.lista.bind("<Double-Button-1>", self._toggle_subtareas)

        self._centrar_ventana()
        self._verificar_notificaciones()

    # ---------------- UI ----------------
    def _crear_ui(self):
        self.canvas = tk.Canvas(self.ventana, width=900, height=600)
        self.canvas.pack(fill="both", expand=True)

        # Lista
        frame_lista = tk.Frame(self.ventana)
        self.canvas.create_window(450, 185, window=frame_lista)

        scroll_y = tk.Scrollbar(frame_lista, orient="vertical")
        scroll_x = tk.Scrollbar(frame_lista, orient="horizontal")

        self.lista = tk.Listbox(
            frame_lista,
            width=90,
            height=18,
            font=("Arial", 12),
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=self.lista.yview)
        scroll_x.config(command=self.lista.xview)

        self.lista.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        frame_lista.grid_rowconfigure(0, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)

        # Botones
        botones = [
            ("Agregar Tarea", self._agregar_tarea),
            ("Ver Detalles", self._ver_detalles),
            ("Editar Tarea", self._editar_tarea),
            ("Marcar Completada", self._marcar_completada),
            ("Eliminar Tarea", self._eliminar_tarea),
            ("Filtrar Tareas", self._filtrar_tareas),
            ("Cambiar Fondo", self._cambiar_fondo),
            ("Salir", self.ventana.quit)
        ]

        y = 400
        for texto, accion in botones:
            btn = tk.Button(self.ventana, text=texto, width=25, font=("Arial", 11), command=accion)
            self.canvas.create_window(450, y, window=btn)

            if texto == "Cambiar Fondo":
                btn_quitar = tk.Button(
                    self.ventana, text="🚫", font=("Arial", 11, "bold"),
                    command=self._quitar_fondo, border=0, relief="flat",
                    width=3, height=1
                )
                self.canvas.create_window(450 + 135, y, window=btn_quitar)

            y += 50

    # ---------------- Util ----------------
    def _centrar_ventana(self):
        self.ventana.update_idletasks()
        w = self.ventana.winfo_width()
        h = self.ventana.winfo_height()
        sw = self.ventana.winfo_screenwidth()
        sh = self.ventana.winfo_screenheight()
        x = int((sw - w) / 2)
        y = int((sh - h) / 2)
        self.ventana.geometry(f"{w}x{h}+{x}+{y}")

    # ---------------- JSON ----------------
    def _cargar_tareas(self):
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def _guardar_tareas(self):
        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump(self.tareas, f, indent=4, ensure_ascii=False)

    # ---------------- Lista ----------------
    def _actualizar_lista(self):
        self.subtareas_mostradas = {}
        self.lista.delete(0, tk.END)

        for i, t in enumerate(self.tareas):
            estado = "✅" if t.get("estado") == "completada" else "⏳"
            self.lista.insert(
                tk.END,
                f"{i+1}. {estado} {t.get('titulo','Sin título')} - {t.get('prioridad','Media')} - {t.get('fecha_limite','Sin fecha')}"
            )

    # ---------------- Fondo ----------------
    def _guardar_ruta_fondo(self, ruta):
        with open(self.fondo_config, "w", encoding="utf-8") as f:
            json.dump({"ruta_fondo": ruta}, f)

    def _cargar_ruta_fondo(self):
        try:
            with open(self.fondo_config, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("ruta_fondo")
        except Exception:
            return None

    def _cargar_fondo_guardado(self):
        ruta = self._cargar_ruta_fondo()
        if ruta:
            try:
                self.imagen_fondo_original = Image.open(ruta)
                self._redimensionar_fondo()
            except Exception:
                self.imagen_fondo_original = None

    def _cambiar_fondo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen de fondo",
            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.gif")]
        )
        if not ruta:
            return

        try:
            self.imagen_fondo_original = Image.open(ruta)
            self._redimensionar_fondo()
            self._guardar_ruta_fondo(ruta)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}")

    def _quitar_fondo(self):
        self.imagen_fondo_original = None
        self.fondo_tk = None
        self.canvas.delete("fondo")
        self._guardar_ruta_fondo("")

    def _redimensionar_fondo(self, event=None):
        if self.imagen_fondo_original is None:
            self.canvas.delete("fondo")
            return

        w = self.ventana.winfo_width()
        h = self.ventana.winfo_height()
        if w < 2 or h < 2:
            return

        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.ANTIALIAS

        img = self.imagen_fondo_original.resize((w, h), resample)
        self.fondo_tk = ImageTk.PhotoImage(img)

        self.canvas.delete("fondo")
        self.canvas.create_image(0, 0, image=self.fondo_tk, anchor="nw", tags="fondo")

    # ---------------- Subtareas ----------------
    def _toggle_subtareas(self, event=None):
        sel = self.lista.curselection()
        if not sel:
            return

        idx = sel[0]

        # Click sobre subtarea (si ya está desplegada)
        for tarea_idx, subt_idxs in self.subtareas_mostradas.items():
            if idx in subt_idxs:
                sub_pos = subt_idxs.index(idx)
                subtarea = self.tareas[tarea_idx]["subtareas"][sub_pos]
                subtarea["estado"] = "completada" if subtarea["estado"] == "pendiente" else "pendiente"
                self._guardar_tareas()
                self._actualizar_lista()
                self._abrir_subtareas(tarea_idx)
                return

        # Toggle abrir/cerrar
        if idx in self.subtareas_mostradas:
            self._ocultar_subtareas(idx)
        else:
            self._abrir_subtareas(idx)

    def _abrir_subtareas(self, idx):
        tarea = self.tareas[idx]
        subtareas = tarea.get("subtareas", [])
        if not subtareas:
            return

        subt_idxs = []
        for i, sub in enumerate(subtareas):
            estado = "✅" if sub["estado"] == "completada" else "⏳"
            self.lista.insert(idx + 1 + i, f"     {estado} {sub['texto']}")
            subt_idxs.append(idx + 1 + i)

        self.subtareas_mostradas[idx] = subt_idxs

    def _ocultar_subtareas(self, idx):
        subt_idxs = self.subtareas_mostradas.pop(idx, [])
        for i in reversed(subt_idxs):
            self.lista.delete(i)

    # ---------------- Acciones ----------------
    def _agregar_tarea(self):
        # (Aquí puedes pegar tu modal original, igual que antes)
        messagebox.showinfo("Info", "Aquí va tu ventana modal de agregar tarea 😊")

    def _ver_detalles(self):
        messagebox.showinfo("Info", "Aquí va tu ventana de detalles 😊")

    def _editar_tarea(self):
        messagebox.showinfo("Info", "Aquí va tu ventana de editar 😊")

    def _marcar_completada(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una tarea")
            return
        i = sel[0]
        self.tareas[i]["estado"] = "completada"
        self._guardar_tareas()
        self._actualizar_lista()

    def _eliminar_tarea(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una tarea")
            return
        i = sel[0]
        if messagebox.askyesno("Eliminar", f"¿Eliminar la tarea '{self.tareas[i]['titulo']}'?"):
            self.tareas.pop(i)
            self._guardar_tareas()
            self._actualizar_lista()

    def _filtrar_tareas(self):
        messagebox.showinfo("Info", "Aquí va tu ventana de filtros 😊")

    # ---------------- Notificaciones ----------------
    def _verificar_notificaciones(self):
        hoy = datetime.now().date()
        notificaciones = []

        for t in self.tareas:
            if t.get("estado") == "completada":
                continue

            fecha_str = (t.get("fecha_limite") or "").strip()
            if not fecha_str:
                continue

            try:
                fecha_limite = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            dias = (fecha_limite - hoy).days
            t.setdefault("notificado_1_dia", False)
            t.setdefault("notificado_vencido", False)

            if dias == 1 and not t["notificado_1_dia"]:
                notificaciones.append(("warning", "⏳ Tarea por vencer", f"La tarea:\n\n'{t['titulo']}'\n\nVence mañana."))
                t["notificado_1_dia"] = True

            if dias <= 0 and not t["notificado_vencido"]:
                notificaciones.append(("error", "⛔ Tiempo agotado", f"La tarea:\n\n'{t['titulo']}'\n\nha alcanzado o superado su fecha límite."))
                t["notificado_vencido"] = True

        if notificaciones:
            self._guardar_tareas()
            self._mostrar_notificaciones(notificaciones)

        self.ventana.after(60000, self._verificar_notificaciones)

    def _mostrar_notificaciones(self, notificaciones):
        if not notificaciones:
            return

        tipo, titulo, msg = notificaciones.pop(0)

        if tipo == "warning":
            messagebox.showwarning(titulo, msg)
        else:
            messagebox.showerror(titulo, msg)

        self.ventana.after(200, lambda: self._mostrar_notificaciones(notificaciones))

    # ---------------- Run ----------------
    def run(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    app = OrganizadorTareasApp()
    app.run()