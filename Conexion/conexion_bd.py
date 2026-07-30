import psycopg2

class ConexionDB:
    @staticmethod
    def obtener_conexion():
        try:
            return psycopg2.connect(
                host="localhost",
                user="postgres",
                password="admin",
                database="bd_ventas"
            )


        except Exception as e:
            print("Error de conexión:", e)
            return None



