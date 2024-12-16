import asyncio
import websockets
import queue

# Lista para almacenar conexiones activas
connected_clients = set()
service_queue = queue.Queue()

async def chat_handler(websocket, path):
    """
    Maneja la conexión WebSocket con los clientes.
    """
    # Agregar cliente conectado
    connected_clients.add(websocket)
    print(f"Nuevo cliente conectado: {websocket.remote_address}")

    try:
        async for message in websocket:
            print(f"Mensaje recibido: {message}")
            # Añadir el mensaje a la cola de servicio
            service_queue.put(message)

            # Reenviar el mensaje a todos los demás clientes conectados
            for client in connected_clients:
                if client != websocket:  # Evitar eco al cliente que envió
                    await client.send(f"Cola procesando: {message}")

    except websockets.ConnectionClosed:
        print(f"Cliente desconectado: {websocket.remote_address}")
    finally:
        # Eliminar cliente de la lista al desconectarse
        connected_clients.remove(websocket)

async def process_queue():
    """
    Procesa la cola de servicios y notifica a los clientes conectados.
    """
    while True:
        if not service_queue.empty():
            # Procesar mensajes en la cola
            message = service_queue.get()
            print(f"Procesando mensaje: {message}")
            for client in connected_clients:
                await client.send(f"Mensaje procesado: {message}")
                # Aquí también puedes actualizar el panel lateral de la cola, si lo necesitas

        await asyncio.sleep(1)  # Simular un tiempo de procesamiento

async def main():
    print("Iniciando servidor WebSocket en ws://localhost:8765...")
    websocket_server = websockets.serve(chat_handler, "localhost", 8765)
    await asyncio.gather(websocket_server, process_queue())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Servidor detenido.")
