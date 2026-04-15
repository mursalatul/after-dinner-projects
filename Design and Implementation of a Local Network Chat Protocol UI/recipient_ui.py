import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import time
from protocol import *

class RecipientUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SLNCP Recipient")
        self.root.geometry("600x700")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # --- UI Components ---
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.columnconfigure(1, weight=1)
        self.main_container.rowconfigure(3, weight=1) # Log area takes space
        self.main_container.rowconfigure(4, weight=2) # Chat area takes more space
        
        ttk.Label(self.main_container, text="My Nickname:").grid(row=0, column=0, sticky=tk.W)
        self.my_nickname = tk.StringVar(value="Recipient")
        ttk.Entry(self.main_container, textvariable=self.my_nickname).grid(row=0, column=1, sticky="ew", pady=5)
        
        btn_ctrl_frame = ttk.Frame(self.main_container)
        btn_ctrl_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        btn_ctrl_frame.columnconfigure(0, weight=1)
        btn_ctrl_frame.columnconfigure(1, weight=1)

        self.listen_btn = ttk.Button(btn_ctrl_frame, text="Start Listening", command=self.start_listening)
        self.listen_btn.grid(row=0, column=0, padx=2, sticky="ew")
        
        self.stop_listen_btn = ttk.Button(btn_ctrl_frame, text="Stop Listening", command=self.stop_listening, state="disabled")
        self.stop_listen_btn.grid(row=0, column=1, padx=2, sticky="ew")
        
        self.status_label = ttk.Label(self.main_container, text="Status: Ready", foreground="blue", font=('Arial', 10, 'bold'))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        self.log_area = tk.Text(self.main_container, height=8, width=50, state="disabled", wrap="word", font=('Consolas', 9))
        self.log_area.grid(row=3, column=0, columnspan=2, pady=5, sticky="nsew")
        
        # Chat area (hidden initially, inside main_container)
        self.chat_frame = ttk.LabelFrame(self.main_container, text="Chat Room", padding="5")
        self.chat_frame.columnconfigure(0, weight=1)
        self.chat_frame.rowconfigure(0, weight=1)
        
        self.chat_display = tk.Text(self.chat_frame, height=12, width=50, state="disabled", wrap="word")
        self.chat_display.grid(row=0, column=0, columnspan=2, pady=5, sticky="nsew")
        
        self.msg_entry = ttk.Entry(self.chat_frame)
        self.msg_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        self.msg_entry.bind("<Return>", lambda e: self.send_text_msg())
        
        btn_frame = ttk.Frame(self.chat_frame)
        btn_frame.grid(row=1, column=1, sticky=tk.E)
        
        self.send_btn = ttk.Button(btn_frame, text="Send", command=self.send_text_msg)
        self.send_btn.pack(side=tk.LEFT, padx=2)
        
        self.exit_btn = ttk.Button(btn_frame, text="Exit", command=self.stop_session)
        self.exit_btn.pack(side=tk.LEFT, padx=2)
        
        # Networking State
        self.conn = None
        self.running = False
        self.listening = False
        self.ack_received = threading.Event()
        self.ack_received.set()

    def log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def chat_log(self, sender, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def start_listening(self):
        nickname = self.my_nickname.get().strip()
        if not nickname:
            messagebox.showerror("Error", "Nickname required")
            return

        self.listen_btn.config(state="disabled")
        self.stop_listen_btn.config(state="normal")
        self.my_nickname_val = nickname
        self.listening = True
        self.status_label.config(text="Status: Listening for broadcasts...", foreground="orange")
        threading.Thread(target=self.listener_thread, daemon=True).start()

    def stop_listening(self):
        self.listening = False
        self.status_label.config(text="Status: Listening stopped.", foreground="grey")
        self.listen_btn.config(state="normal")
        self.stop_listen_btn.config(state="disabled")
        self.log("Listening stopped by user.")

    def listener_thread(self):
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.settimeout(0.5) # Allow periodic checks of self.listening
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try: udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except: pass
        
        udp_sock.bind(('', UDP_PORT))
        self.log(f"Listening on UDP {UDP_PORT} for '{self.my_nickname_val}'")
        
        while self.listening:
            try:
                data, addr = udp_sock.recvfrom(4096)
                msg = data.decode(ENCODING).strip()
                parts = msg.split(DELIMITER)
                
                if len(parts) >= 5 and parts[0] == DISCOVER:
                    target_name = parts[1]
                    deadline_ts = float(parts[2])
                    tcp_port = int(parts[3])
                    req_uuid = parts[4]
                    
                    if target_name == self.my_nickname_val:
                        if time.time() > deadline_ts:
                            self.log("Received expired discovery query.")
                            continue
                        
                        self.log(f"Discovery matched! Connecting to {addr[0]}:{tcp_port}")
                        self.attempt_connection(addr[0], tcp_port, req_uuid)
                        if self.conn:
                            break # Move to chat loop
            except Exception as e:
                self.log(f"Listener error: {e}")

    def attempt_connection(self, host, port, uuid_val):
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_sock.connect((host, port))
            send_msg(tcp_sock, HANDSHAKE, uuid_val)
            
            prefix, args = recv_msg(tcp_sock)
            if prefix == HANDSHAKE_RESPONSE and args[0] == "ACCEPT":
                self.conn = tcp_sock
                self.root.after(0, self.setup_chat_ui)
                self.running = True
                self.receive_loop()
            else:
                self.log("Handshake rejected by initiator.")
                tcp_sock.close()
        except Exception as e:
            self.log(f"Connection failed: {e}")

    def setup_chat_ui(self):
        self.status_label.config(text="Status: Connected", foreground="green")
        self.stop_listen_btn.config(state="disabled")
        self.chat_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")
        self.msg_entry.config(state="normal")
        self.msg_entry.focus_set()
        self.log("Chat session established. You can now type in the box below.")
        self.root.update_idletasks() # Force UI refresh

    def send_text_msg(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return
            
        if not self.conn or not self.ack_received.is_set():
            self.log("[Protocol] Waiting for ACK from peer...")
            return
        
        try:
            self.ack_received.clear()
            self.send_btn.config(state="disabled")
            send_msg(self.conn, TEXT, encode_text(msg))
            self.chat_log("You", msg)
            self.msg_entry.delete(0, tk.END)
        except Exception as e:
            self.log(f"Send failed: {e}")
            self.cleanup()

    def receive_loop(self):
        while self.running:
            try:
                prefix, args = recv_msg(self.conn)
                if not prefix:
                    self.root.after(0, lambda: self.log("Connection lost."))
                    self.running = False
                    break
                
                if prefix == TEXT and args:
                    content = decode_text(args[0])
                    self.root.after(0, lambda c=content: self.chat_log("Peer", c))
                    send_msg(self.conn, ACK)
                elif prefix == ACK:
                    self.ack_received.set()
                    self.root.after(0, lambda: self.send_btn.config(state="normal"))
                elif prefix == CLOSE:
                    self.root.after(0, lambda: self.status_label.config(text="Status: Peer Closed Connection", foreground="red"))
                    self.root.after(0, lambda: self.log("Peer closed the connection."))
                    self.running = False
                    break
            except Exception as e:
                self.log(f"Reception error: {e}")
                break
        
        self.root.after(0, self.cleanup)

    def stop_session(self):
        if self.conn:
            try:
                send_msg(self.conn, CLOSE, "User exited")
            except:
                pass
        self.running = False
        self.cleanup()

    def cleanup(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        self.chat_frame.grid_forget()
        self.listen_btn.config(state="normal")
        self.stop_listen_btn.config(state="disabled")
        self.status_label.config(text="Status: Disconnected", foreground="grey")
        self.listening = False

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipientUI(root)
    root.mainloop()
