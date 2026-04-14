import threading
import sys
from protocol import *

class ChatSession:
    """Manages the interactive chat session, implementing half-duplex communication rules."""
    def __init__(self, conn):
        """
        Initializes the ChatSession with a given connection.

        Args:
            conn (socket.socket): The TCP socket connection to the peer.
        """
        self.conn = conn
        self.running = True
        self.ack_event = threading.Event()
        self.ack_event.set() # Initially we can send the first message
        
    def start(self):
        """
        Starts the chat thread and begins reading user input.
        
        This method initializes a background daemon thread to listen for
        incoming messages and enters a loop to capture user input,
        ensuring half-duplex communication rules are followed.
        """
        print("\n--- Chat session established. You can start typing. Type 'exit' to quit. ---")
        
        # Start a background daemon thread to listen for incoming messages
        reader = threading.Thread(target=self.receive_loop)
        reader.daemon = True
        reader.start()
        
        try:
            while self.running:
                # Wait for user input
                msg = input("You: ")
                if not self.running:
                    break
                    
                if msg.lower() == 'exit':
                    send_msg(self.conn, CLOSE, "User initiated connection close.")
                    self.running = False
                    break
                    
                # Ensure half-duplex communication; wait for previous message payload response.
                if not self.ack_event.is_set():
                    print("[System] Waiting for previous message to be delivered...")
                    self.ack_event.wait()
                
                self.ack_event.clear() # Block future sends until ACK received
                send_msg(self.conn, TEXT, encode_text(msg))
                
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            send_msg(self.conn, CLOSE, "Session terminated")
            self.conn.close()

    def receive_loop(self):
        """
        Background loop continuously polling the TCP socket for incoming packets.

        This routine receives messages, displays text payloads, and manages
        protocol acknowledgments to maintain the half-duplex state.
        """
        while self.running:
            prefix, args = recv_msg(self.conn)
            
            if not prefix:
                self.running = False
                print("\n[System] Connection lost.")
                self.ack_event.set()
                break
                
            if prefix == TEXT:
                # Received text message, decode and print
                if len(args) > 0:
                    text_content = decode_text(args[0])
                    # Clear current line prefix so output cleanly interrupts Input() prompt
                    sys.stdout.write('\r\033[K') 
                    print(f"Peer: {text_content}")
                    sys.stdout.write("You: ")
                    sys.stdout.flush()
                # Respond with implicit ACK according to protocol rules (requires response before next tx)
                send_msg(self.conn, ACK)
                
            elif prefix == ACK:
                # Peer confirmed reception of our message
                self.ack_event.set()
                
            elif prefix == CLOSE:
                print("\n[System] Peer closed the connection.")
                self.running = False
                self.ack_event.set() # Unblock writer block
                # Unblock input block to allow clean exit
                print("Press Enter to exit.")
                break
