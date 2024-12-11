import socketio
import eventlet
import mysql.connector
from mysql.connector import Error

# Crear una instancia de Socket.IO
sio = socketio.Server(cors_allowed_origins="*")

# Crear una aplicación de WSGI
app = socketio.WSGIApp(sio)

# Diccionario para almacenar SID y nombre de usuario
usuarios_conectados = {}

#Conexion a la base de datos
def ConexionDB():
    try:
        connection = mysql.connector.connect(
            host="34.42.104.166",
            database="tictactuedb",
            user="root",
            password="123456"
        )
        return connection
    except Error as ex:
        print(f"Error al conectarse a DB: {ex}")
        return None


# Manejar la conexión de un cliente
@sio.event
def connect(sid, environ):
    print(f"Cliente conectado: {sid}")

# Manejar la recepción de mensajes
@sio.event
def tableroServidor(sid, data):
    print(f"Usuarios conectados: {usuarios_conectados}")
    tablero = data['tablero']
    isXTurn = data['isXTurn']
    print(f'Mensaje recibido: {tablero}')
    # Reenviar el mensaje a todos los clientes conectados
    #sio.send(sid, data)  # Esto envía solo al remitente
    #sio.emit('message', data)  # Esto envía a todos los clientes
    sio.emit("tableroCliente",{"data": tablero, "turno": isXTurn}, skip_sid=sid)


# Manejar la recepción de mensajes
@sio.event
def mensaje(sid, data):
    print(f'Mensaje recibido: {data}')
    # Reenviar el mensaje a todos los clientes conectados
    #sio.send(sid, data)  # Esto envía solo al remitente
    #sio.emit('message', data)  # Esto envía a todos los clientes
    sio.emit("mensajeCliente", data, skip_sid=sid)

@sio.event
def insert_usuario(sid, data):
    connDB = ConexionDB()
    if connDB is None:
        print("Error: No se pudo conectar a la base de datos.")
        sio.emit("registroRespuesta", {"success": False, "message": "Error en el servidor"}, to=sid)

    try:
        cursor = connDB.cursor()
        sql = """
            INSERT INTO users (name, password, nickname, status)
            VALUES (%s, %s, %s, %s);
        """
      
        cursor.execute(sql, (data["name"], data["password"], data["nickname"], data["status"]))
        connDB.commit()
        sio.emit("registroRespuesta", {"success": True, "message": "Usuario registrado con éxito"}, to=sid)
    except Exception as e:
        print(f"Error al insertar el usuario: {e}")
        sio.emit("registroRespuesta", {"success": False, "message": "Error en el servidor"}, to=sid)

# Manejo del login
@sio.event
def login(sid, data):
    connDB = ConexionDB()
    try:
        nickname = data["nickname"]
        password = data["password"]
        cursor = connDB.cursor()
        sql = "SELECT nickname FROM users u WHERE nickname = %s and password = %s;"
        cursor.execute(sql, (nickname, password))
        resultado = cursor.fetchone()

        if resultado:
            # Marcar cliente como conectado
            usuarios_conectados[nickname] = sid
            sio.emit("loginRespuesta", {"success": True, "message": "Login exitoso"}, to=sid)
        else:
            sio.emit("loginRespuesta", {"success": False, "message": "Credenciales incorrectas"}, to=sid)

    except KeyError as e:
        missing_key = str(e)
        sio.emit("loginRespuesta", {"success": False, "message": f"Falta el campo: {missing_key}"}, to=sid)
    except Exception as e:
        print("Error en login:", e)
        sio.emit("loginRespuesta", {"success": False, "message": "Error en el servidor"}, to=sid)

# Ejecutar el servidor
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 5000)), app)