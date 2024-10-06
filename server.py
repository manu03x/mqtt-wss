import asyncio
import websockets
import ssl
import sqlite3  # Para usar SQLite como base de datos
import paho.mqtt.client as mqtt

# Conectar a la base de datos SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS mqtt_data
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, message TEXT)''')
conn.commit()

# Configuración SSL/TLS
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # Solo permitir TLS 1.2 o 1.3

# Manejar WebSocket
async def echo(websocket, path):
    async for message in websocket:
        print(f"Mensaje recibido del cliente WebSocket: {message}")
        await websocket.send(f"Echo: {message}")

# Guardar datos del MQTT en la base de datos
def save_to_db(topic, message):
    cursor.execute("INSERT INTO mqtt_data (topic, message) VALUES (?, ?)", (topic, message))
    conn.commit()
    print(f"Guardado en la DB: {topic} - {message}")

# Callback para cuando se recibe un mensaje del MQTT
def on_message(client, userdata, msg):
    print(f"Mensaje recibido del MQTT: {msg.topic} - {msg.payload.decode()}")
    save_to_db(msg.topic, msg.payload.decode())

# Configurar MQTT
def setup_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("mqtt.eclipseprojects.io", 1883, 60)  # Broker MQTT público
    client.subscribe("test/topic")  # Suscribirse a un tema
    client.loop_start()  # Iniciar el loop de MQTT

# Iniciar servidor WebSocket
async def start_websocket():
    async with websockets.serve(echo, "localhost", 8765, ssl=ssl_context):
        print("Servidor WebSocket seguro corriendo en ws://localhost:8765")
        await asyncio.Future()  # Mantener el servidor corriendo

# Ejecutar todo
if __name__ == "__main__":
    setup_mqtt()  # Iniciar MQTT
    asyncio.run(start_websocket())  # Iniciar WebSocket

