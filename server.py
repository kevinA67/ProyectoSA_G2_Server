import socketio
import eventlet

# Crear una instancia de Socket.IO
sio = socketio.Server(cors_allowed_origins="*")

# Crear una aplicación de WSGI
app = socketio.WSGIApp(sio)

# Diccionario para almacenar SID y nombre de usuario
usuarios_conectados = {
  "kevin": "",
  "alexis": ""
}

# Manejar la conexión de un cliente
@sio.event
def connect(sid, environ):
    print(f"Cliente conectado: {sid}")


# Escuchar el evento 'registrarUsuario' enviado por el cliente
@sio.event
def registrarUsuario(sid, nombre_usuario):
    # Asociar el SID con el nombre de usuario
    if(usuarios_conectados["kevin"] == ""):
        usuarios_conectados["kevin"] = sid
    else:
        usuarios_conectados["alexis"] = sid
    print(f"Usuarios conectados: {usuarios_conectados}")

# Manejar la recepción de mensajes
@sio.event
def tableroServidor(sid, data):
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

# Ejecutar el servidor
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 5000)), app)