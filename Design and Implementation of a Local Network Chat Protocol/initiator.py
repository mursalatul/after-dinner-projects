import socket
import time
import uuid
import sys
from protocol import *
from chat_session import ChatSession

def run_initiator(target_nickname, timeout_sec):
    """
    Executes the initiator role for the local network chat protocol.

    Initiates discovery using UDP broadcasts, establishes a TCP server to await
    connections, verifies the handshake, and launches the chat session.

    Args:
        target_nickname (str): The requested nickname of the recipient to discover.
        timeout_sec (int): Allowable time in seconds to wait for a connection.
    """
    req_uuid = str(uuid.uuid4())
    deadline_ts = time.time() + timeout_sec
    
    # 1. Setup listening TCP server socket dynamically allocating an available ephemeral port
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(('0.0.0.0', 0))
    tcp_sock.listen(1)
    tcp_sock.settimeout(1.0)
    _, tcp_port = tcp_sock.getsockname()
    
    # 2. Transmit Discovery payload via UDP Broadcast Frame
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    # Formulate Discover string structure per Custom Protocol standard
    discover_msg = f"{DISCOVER}{DELIMITER}{target_nickname}{DELIMITER}{deadline_ts}{DELIMITER}{tcp_port}{DELIMITER}{req_uuid}{TERMINATOR}"
    print(f"[*] Broadcasting discovery for '{target_nickname}' on UDP {UDP_PORT}...")
    
    try:
        udp_sock.sendto(discover_msg.encode(ENCODING), ('<broadcast>', UDP_PORT))
    except Exception as e:
        print(f"[-] Broadcast failure: {e}. Switching to alternate interfaces...")
        # Fallback to local subnet broadcast if generic broadcast fails
        try:
            udp_sock.sendto(discover_msg.encode(ENCODING), ('255.255.255.255', UDP_PORT))
        except Exception:
            # Final fallback for local testing on macOS without an active network route
            udp_sock.sendto(discover_msg.encode(ENCODING), ('127.255.255.255', UDP_PORT))
        
    print(f"[*] Waiting for connection on TCP port {tcp_port} for {timeout_sec} seconds...")
    
    conn = None
    # Wait until deadline_ts triggers to accept incoming connections
    while time.time() < deadline_ts:
        try:
            conn, addr = tcp_sock.accept()
            print(f"[+] Connection received from {addr[0]}")
            break
        except socket.timeout:
            # Poll iteratively every second maintaining check for arbitrary constraints
            continue
            
    if not conn:
        print("[-] Deadline expired. No recipient connected.")
        tcp_sock.close()
        return
        
    conn.settimeout(None) # Clear polling timeout for synchronized stream processing
    
    # --- Step 3: Handshake verification processing
    prefix, args = recv_msg(conn)
    
    if prefix != HANDSHAKE or len(args) != 1:
        print("[-] Malformed Handshake sequence transmitted.")
        send_msg(conn, HANDSHAKE_RESPONSE, "REJECT", "Invalid_Format")
        conn.close()
        return
        
    received_uuid = args[0]
    if received_uuid != req_uuid:
        print(f"[-] UUID Context mismatch. Expected {req_uuid}, Transmitted {received_uuid}")
        send_msg(conn, HANDSHAKE_RESPONSE, "REJECT", "UUID_Mismatch")
        conn.close()
        return
        
    if time.time() > deadline_ts:
        print("[-] Exceeded Handshake temporal boundings.")
        send_msg(conn, HANDSHAKE_RESPONSE, "REJECT", "Deadline_Expired")
        conn.close()
        return
        
    print("[+] Transport Handshake validated correctly. Confirming...")
    send_msg(conn, HANDSHAKE_RESPONSE, "ACCEPT", "OK")
    
    # --- Step 4: Dispatch established chat session
    session = ChatSession(conn)
    session.start()
    
    tcp_sock.close()
    print("[*] Initiator task concluded cleanly.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python initiator.py <Recipient Nickname> <Timeout Seconds>")
        sys.exit(1)
        
    nickname_arg = sys.argv[1]
    timeout_arg = int(sys.argv[2])
    run_initiator(nickname_arg, timeout_arg)
