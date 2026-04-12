import socket
import sys
import time
from protocol import *
from chat_session import ChatSession

def run_recipient(my_nickname):
    # Bind to Local UDP broadcast port for receiving initiator queries
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Enable address/port reuse for flexible testing instances
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass
        
    udp_sock.bind(('', UDP_PORT))
    print(f"[*] Listening for discovery broadcasts mapped to '{my_nickname}' on UDP {UDP_PORT}...")
    
    while True:
        try:
            data, addr = udp_sock.recvfrom(4096)
        except Exception as e:
            print(f"[-] UDP Rx Exception: {e}")
            continue
            
        msg = data.decode(ENCODING).strip()
        parts = msg.split(DELIMITER)
        
        # Unpack structure strictly correlating against Custom Protocol specifications
        if len(parts) >= 5 and parts[0] == DISCOVER:
            nickname = parts[1]
            try:
                deadline_ts = float(parts[2])
                tcp_port = int(parts[3])
            except ValueError:
                print("[-] Received improperly typed numeric fields in DISCOVER. Ignoring.")
                continue
                
            req_uuid = parts[4]
            
            # --- Check specific node identity
            if nickname == my_nickname:
                print(f"\n[+] Relevant discovery query logged originating from {addr[0]}")
                
                # Verify expiration vector
                if time.time() > deadline_ts:
                    print("[-] Payload temporal interval surpassed standard allowance. Deposed.")
                    continue
                    
                print(f"[*] Attempting upstream connection to TCP Coordinator [{addr[0]}:{tcp_port}]...")
                tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    tcp_sock.connect((addr[0], tcp_port))
                except Exception as e:
                    print(f"[-] Failed upstream negotiation: {e}")
                    continue
                    
                # Initiate Handshake per Step-3 specs
                send_msg(tcp_sock, HANDSHAKE, req_uuid)
                print("[*] Handshake query submitted. Pending verification state...")
                
                prefix, args = recv_msg(tcp_sock)
                if prefix == HANDSHAKE_RESPONSE:
                    status = args[0]
                    if status == "ACCEPT":
                        print("[+] Exchange ACCEPTED by protocol coordinator!")
                        
                        # Mount active dialogue pipeline
                        session = ChatSession(tcp_sock)
                        session.start()
                    else:
                        reason = args[1] if len(args) > 1 else "Unknown Response Vector"
                        print(f"[-] Session REJECTED upstream. Provided Context: {reason}")
                        tcp_sock.close()
                else:
                    print("[-] Desynchronized or illegal framework condition encountered during handshake pipeline.")
                    tcp_sock.close()
                
                print(f"\n[*] Listening constraint restabilized for '{my_nickname}' on UDP {UDP_PORT}...")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python recipient.py <Your Account Nickname>")
        sys.exit(1)
        
    my_nickname_arg = sys.argv[1]
    
    try:
        run_recipient(my_nickname_arg)
    except KeyboardInterrupt:
        print("\n[*] Exiting application.")
        sys.exit(0)
