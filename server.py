import asyncio
import websockets

# Lista para almacenar conexiones activas
connected_clients = set()

async def chat_handler(websocket, path):
    """
    Maneja la conexión WebSocket con los clientes.
    """
    # Agregar cliente conectado
    connected_clients.add(websocket)
    print(f"Nuevo cliente conectado: {websocket.remote_address}")

    try:
        # Escuchar mensajes del cliente
        async for message in websocket:
            print(f"Mensaje recibido: {message}")
            # Reenviar el mensaje a todos los demás clientes conectados
            for client in connected_clients:
                if client != websocket:  # Evitar eco al cliente que envió
                    await client.send(message)
    except websockets.ConnectionClosed:
        print(f"Cliente desconectado: {websocket.remote_address}")
    finally:
        # Eliminar cliente de la lista al desconectarse
        connected_clients.remove(websocket)

# Configurar el servidor WebSocket
async def main():
    print("Iniciando servidor WebSocket en ws://localhost:8765...")
    async with websockets.serve(chat_handler, "localhost", 8765):
        await asyncio.Future()  # Mantener el servidor activo

# Iniciar el servidor
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Servidor detenido.")
