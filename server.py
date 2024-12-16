import asyncio
import websockets
import json
import uuid  # Para generar IDs únicos

connected_clients = {}  # Diccionario para almacenar clientes conectados {websocket: {"id":, "name":}}

# Manejar conexiones y mensajes
async def chat_handler(websocket, path):
    try:
        # Recibe el nombre del cliente al conectar
        name_message = await websocket.recv()
        name_data = json.loads(name_message)
        if name_data["type"] == "set_name":
            client_name = name_data["name"]
            client_id = str(uuid.uuid4())  # Generar un ID único
            connected_clients[websocket] = {"id": client_id, "name": client_name}

            print(f"{client_name} se ha conectado.")
            await notify_all_clients()

            # Escuchar mensajes
            async for message in websocket:
                data = json.loads(message)

                # Enviar mensaje dirigido a un destinatario
                if data["type"] == "send_message":
                    recipient_name = data["to"]
                    content = data["content"]
                    sender_name = connected_clients[websocket]["name"]

                    await send_message_to_recipient(recipient_name, sender_name, content)

    except websockets.ConnectionClosed:
        print("Un cliente se ha desconectado.")
    finally:
        # Remover cliente desconectado y notificar
        connected_clients.pop(websocket, None)
        await notify_all_clients()

# Enviar un mensaje al destinatario especificado
async def send_message_to_recipient(recipient_name, sender_name, content):
    for client, info in connected_clients.items():
        if info["name"] == recipient_name:
            await client.send(json.dumps({
                "type": "new_message",
                "from": sender_name,
                "content": content
            }))
            break

# Notificar a todos los clientes la lista actualizada de usuarios
async def notify_all_clients():
    users_list = [{"name": client["name"]} for client in connected_clients.values()]
    update_message = json.dumps({"type": "update_users", "users": users_list})

    for client in connected_clients:
        await client.send(update_message)

# Iniciar servidor
async def main():
    print("Servidor WebSocket escuchando en ws://localhost:8765")
    async with websockets.serve(chat_handler, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
