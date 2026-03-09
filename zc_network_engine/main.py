import os, sys, asyncio
from handlers import SocketHandler


async def main():
    server_socket= SocketHandler()

    try:
        server_socket.connect(host="127.0.0.1", port=2547)

        await server_socket.handle_connection()

    except Exception as e:
        print(f"\n[SERVER]: Error in opening socket: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass 
