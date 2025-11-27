import socket
import threading
import sys

clients = []        # store client addresses
peer_conn = None    # UDP socket
peer_addr = None    # peer address

def broadcast(message, source_conn=None):
    """Send message to all clients connected to this server"""
    for addr in clients:
        if addr != source_conn:
            peer_conn.sendto(message.encode(), addr)     # CHANGED

def handle_client(conn, addr):
    """Unused in UDP, but kept exactly as in original"""
    pass

def client_listener(host, port):
    global peer_conn
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # CHANGED
    peer_conn = server                                           # reuse same socket
    server.bind((host, port))
    print(f"[LISTENING] Client connections on {host}:{port}")
    while True:
        msg, addr = server.recvfrom(1024)                        # CHANGED
        msg = msg.decode()

        if addr not in clients:
            clients.append(addr)
            print(f"[NEW CLIENT] {addr} connected")

        print(f"[CLIENT {addr}] {msg}")

        # broadcast to local clients
        broadcast(msg, source_conn=addr)

        # forward to peer server
        if peer_addr:
            peer_conn.sendto(msg.encode(), peer_addr)            # CHANGED

def peer_listener(host, port):
    global peer_conn, peer_addr
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # CHANGED
    peer_conn = server
    server.bind((host, port))
    print(f"[LISTENING] Peer server on {host}:{port}")

    while True:
        msg, addr = server.recvfrom(1024)                        # CHANGED
        peer_addr = addr
        msg = msg.decode()
        print(f"[PEER CONNECTED] from {addr}")
        print(f"[PEER MSG] {msg}")

        broadcast(msg)

def connect_to_peer(host, port):
    global peer_conn, peer_addr
    peer_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # CHANGED
    peer_addr = (host, port)

    # UDP has no connect(), send a hello packet instead
    peer_conn.sendto(b"HELLO", peer_addr)

    print(f"[CONNECTED] to peer server at {host}:{port}")
    handle_peer(peer_conn)

def handle_peer(conn):
    """Handle messages from peer server"""
    while True:
        msg, addr = conn.recvfrom(1024)                        # CHANGED
        msg = msg.decode()
        print(f"[PEER MSG] {msg}")
        broadcast(msg)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python server.py A|B")
        sys.exit(0)

    role = sys.argv[1].upper()
    host = "127.0.0.1"

    if role == "A":
        threading.Thread(target=client_listener, args=(host, 9000)).start()
        threading.Thread(target=peer_listener, args=(host, 9001)).start()

    elif role == "B":
        threading.Thread(target=client_listener, args=(host, 9010)).start()
        threading.Thread(target=connect_to_peer, args=(host, 9001)).start()

    else:
        print("Invalid role! Use A or B.")



import socket
import threading
import sys

def receive_messages(sock):
    while True:
        try:
            msg, _ = sock.recvfrom(1024)        # CHANGED
            print(msg.decode())
        except:
            break

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python client.py A|B username")
        sys.exit(0)

    server_choice = sys.argv[1].upper()
    username = sys.argv[2]
    host = "127.0.0.1"

    if server_choice == "A":
        port = 9000
    elif server_choice == "B":
        port = 9010
    else:
        print("Invalid choice! Use A or B")
        sys.exit(0)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # CHANGED

    print(f"[CONNECTED] to Server {server_choice} as {username}")

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        msg = input()
        if msg.lower() == "exit":
            break
        full_msg = f"{username}: {msg}"
        sock.sendto(full_msg.encode(), (host, port))           # CHANGED

    sock.close()
