from Conexion.conexion_bd import ConexionDB
class Login:

    def __init__(self, usuario, password):
        self.usuario_correcto = usuario
        self.password_correcto = password

    def validar(self):
        conexion = ConexionDB.obtener_conexion()
        if conexion is None:
            return False

        cursor = conexion.cursor()
        sql = """
                    SELECT "rol", "nombres", "apellidos"
                    FROM "Usuario"
                    WHERE "user" = %s AND "pass" = %s
                        
                """
        cursor.execute(sql, (self.usuario_correcto, self.password_correcto))
        resultado = cursor.fetchone()

        cursor.close()
        conexion.close()

        if resultado:
            return {
                "rol": resultado[0],
                "nombres": resultado[1],
                "apellidos": resultado[2]
            }
        else:
            return None