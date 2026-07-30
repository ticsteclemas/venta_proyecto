from Conexion.conexion_bd import ConexionDB

def listar_clientes():
    conn = ConexionDB.obtener_conexion()
    if conn is None:
         return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
        Select id_clientes, cedula, nombres, apellidos from clientes
        order by id_clientes ASC
        """)
        clientes= cursor.fetchall()

        return clientes

    except Exception as error:
        print(error)


def buscar_clientes(texto):
    conn = ConexionDB.obtener_conexion()
    if conn is None:
         return []

    try:
        cursor = conn.cursor()
        if texto == "":
            cursor.execute("""
            Select id_clientes, cedula, nombres, apellidos from clientes
            order by id_clientes ASC
            """)
        else:
            cursor.execute("""
            Select id_clientes, cedula, nombres, apellidos from clientes
            where 
            cast(cedula as TEXT) ILIKE %s
            or nombres ILIKE %s
            or apellidos ILIKE %s
            order by id_clientes ASC
            """,(f"%{texto}%",f"%{texto}%",f"%{texto}%"))

        clientes = cursor.fetchall()
        return clientes

    except Exception as error:
        print(error)


def insertar_clientes(cedula, nombres, apellidos):
    conn = ConexionDB.obtener_conexion()
    if conn is None:
         return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
                   Insert into clientes (cedula, nombres, apellidos)
                   values (%s, %s, %s)
                   """,(cedula, nombres, apellidos))
        conn.commit()
        return "Cliente insertado correctamente"

    except Exception as error:
        print(error)









