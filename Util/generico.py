from PIL import ImageTk, Image

def leer_imagen(path, size):
    return ImageTk.PhotoImage(Image.open(path).resize(size, Image.Resampling.LANCZOS))


def centrar_ventana(ventana, aplicacion_largo, aplicacion_ancho):
    ventana.update_idletasks()

    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_largo = ventana.winfo_screenheight()

    x = int((pantalla_ancho - aplicacion_ancho) / 2)
    y = int((pantalla_largo - aplicacion_largo) / 2)
    print("Segundo cambio en otro archivo")

    return ventana.geometry(f"{aplicacion_ancho}x{aplicacion_largo}+{x}+{y}")