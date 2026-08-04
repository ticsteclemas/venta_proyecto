from tkinter import messagebox


# ---------------------------
# Validaciones genéricas
# ---------------------------

def validar_texto(valor: str, nombre_campo="El campo", min_len=1, max_len=None):
    """
    Valida un campo de texto.
    - No vacío
    - Longitud mínima y máxima opcional
    Retorna (True, texto_limpio) o (False, None)
    """
    texto = (valor or "").strip()

    if len(texto) < min_len:
        messagebox.showerror("Validación", f"{nombre_campo} no puede estar vacío.")
        return False, None

    if max_len is not None and len(texto) > max_len:
        messagebox.showerror("Validación", f"{nombre_campo} no debe superar {max_len} caracteres.")
        return False, None

    return True, texto


def validar_entero(valor: str, nombre_campo="El campo", min_val=None, max_val=None):
    """
    Valida un número entero.
    - Conversión a int
    - Rango mínimo y máximo opcional
    Retorna (True, int) o (False, None)
    """
    try:
        num = int((valor or "").strip())
    except:
        messagebox.showerror("Validación", f"{nombre_campo} debe ser un número entero.")
        return False, None

    if min_val is not None and num < min_val:
        messagebox.showerror("Validación", f"{nombre_campo} no puede ser menor que {min_val}.")
        return False, None

    if max_val is not None and num > max_val:
        messagebox.showerror("Validación", f"{nombre_campo} no puede ser mayor que {max_val}.")
        return False, None

    return True, num


def validar_decimal(valor: str, nombre_campo="El campo", min_val=None, max_val=None):
    """
    Valida un número decimal.
    - Conversión a float
    - Rango mínimo y máximo opcional
    Retorna (True, float) o (False, None)
    """
    try:
        num = float((valor or "").strip())
    except:
        messagebox.showerror("Validación", f"{nombre_campo} debe ser un número válido.")
        return False, None

    if min_val is not None and num < min_val:
        messagebox.showerror("Validación", f"{nombre_campo} no puede ser menor que {min_val}.")
        return False, None

    if max_val is not None and num > max_val:
        messagebox.showerror("Validación", f"{nombre_campo} no puede ser mayor que {max_val}.")
        print("Mi primer cambio")
        print("Mi segundo cambio")
        return False, None

    return True, num