import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import uuid
import time
from protocol import *

class InitiatorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SLNCP Initiator")
        self.root.geometry("600x700")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # --- UI Components ---
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.columnconfigure(1, weight=1)
        self.main_container.rowconfigure(4, weight=1) # Log area takes space
        self.main_container.rowconfigure(5, weight=2) # Chat area takes more space
        
        ttk.Label(self.main_container, text="Target Nickname:").grid(row=0, column=0, sticky=tk.W)
        self.target_nickname = tk.StringVar(value="Recipient")
        ttk.Entry(self.main_container, textvariable=self.target_nickname).grid(row=0, column=1, sticky="ew", pady=5)
        
        ttk.Label(self.main_container, text="Timeout (seconds):").grid(row=1, column=0, sticky=tk.W)
        self.timeout = tk.StringVar(value="60")
        ttk.Entry(self.main_container, textvariable=self.timeout).grid(row=1, column=1, sticky="ew", pady=5)
        
        btn_ctrl_frame = ttk.Frame(self.main_container)
        btn_ctrl_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        btn_ctrl_frame.columnconfigure(0, weight=1)
        btn_ctrl_frame.columnconfigure(1, weight=1)

        self.start_btn = ttk.Button(btn_ctrl_frame, text="Start Discovery", command=self.start_discovery)
        self.start_btn.grid(row=0, column=0, padx=2, sticky="ew")
        
        self.stop_disc_btn = ttk.Button(btn_ctrl_frame, text="Stop Discovery", command=self.stop_discovery, state="disabled")
        self.stop_disc_btn.grid(row=0, column=1, padx=2, sticky="ew")
        
        self.status_label = ttk.Label(self.main_container, text="Status: Ready", foreground="blue", font=('Arial', 10, 'bold'))
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        self.log_area = tk.Text(self.main_container, height=8, width=50, state="disabled", wrap="word", font=('Consolas', 9))
        self.log_area.grid(row=4, column=0, columnspan=2, pady=5, sticky="nsew")
        
        # Chat area (container within main_container)
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

    def start_discovery(self):
        try:
            target = self.target_nickname.get().strip()
            total_timeout = int(self.timeout.get().strip())
            if not target: raise ValueError("Nickname required")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self.start_btn.config(state="disabled")
        self.stop_disc_btn.config(state="normal")
        self.discovering = True
        self.status_label.config(text="Status: Broadcasting...", foreground="orange")
        threading.Thread(target=self.discovery_thread, args=(target, total_timeout), daemon=True).start()

    def stop_discovery(self):
        self.discovering = False
        self.reset_ui("Discovery stopped by user.")

    def discovery_thread(self, target, timeout_sec):
        req_uuid = str(uuid.uuid4())
        deadline_ts = time.time() + timeout_sec
        
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.bind(('0.0.0.0', 0))
        tcp_sock.listen(1)
        tcp_sock.settimeout(0.5) # Reduced for faster stop check
        _, tcp_port = tcp_sock.getsockname()
        
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        discover_msg = f"{DISCOVER}{DELIMITER}{target}{DELIMITER}{deadline_ts}{DELIMITER}{tcp_port}{DELIMITER}{req_uuid}{TERMINATOR}"
        print(f"[*] Discovery message: {discover_msg.strip()}") # Local debug
        
        conn = None
        last_broadcast = 0
        while self.discovering and time.time() < deadline_ts:
            # Broadcast periodically every 2 seconds
            if time.time() - last_broadcast > 2.0:
                try:
                    udp_sock.sendto(discover_msg.encode(ENCODING), ('<broadcast>', UDP_PORT))
                except:
                    try: udp_sock.sendto(discover_msg.encode(ENCODING), ('255.255.255.255', UDP_PORT))
                    except: udp_sock.sendto(discover_msg.encode(ENCODING), ('127.255.255.255', UDP_PORT))
                last_broadcast = time.time()
                self.log("Broadcasting discovery query...")

            try:
                conn, addr = tcp_sock.accept()
                self.log(f"Connection received from {addr[0]}")
                break
            except socket.timeout:
                continue
        
        if not conn:
            self.root.after(0, lambda: self.reset_ui("Deadline expired."))
            return

        conn.settimeout(None)
        self.conn = conn
        
        # Handshake
        prefix, args = recv_msg(conn)
        if prefix != HANDSHAKE or not args or args[0] != req_uuid:
            send_msg(conn, HANDSHAKE_RESPONSE, "REJECT", "Invalid")
            conn.close()
            self.root.after(0, lambda: self.reset_ui("Handshake failed."))
            return
            
        send_msg(conn, HANDSHAKE_RESPONSE, "ACCEPT", "OK")
        self.root.after(0, self.setup_chat_ui)
        
        self.running = True
        self.receive_loop()

    def setup_chat_ui(self):
        self.status_label.config(text="Status: Connected", foreground="green")
        self.stop_disc_btn.config(state="disabled")
        self.chat_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="nsew")
        self.msg_entry.config(state="normal")
        self.msg_entry.focus_set()
        self.log("Chat session established. You can now type in the box below.")
        self.root.update_idletasks() # Force UI refresh

    def reset_ui(self, reason):
        self.status_label.config(text=f"Status: {reason}", foreground="red")
        self.start_btn.config(state="normal")
        self.stop_disc_btn.config(state="disabled")
        self.log(reason)

    def send_text_msg(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return
            
        if not self.conn or not self.ack_received.is_set():
            self.log("[Protocol] Waiting for ACK from peer...")
            return
        
        if msg.lower() == 'exit':
            self.stop_session()
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
            send_msg(self.conn, CLOSE, "User exited")
        self.running = False
        self.cleanup()

    def cleanup(self):
        if self.conn:
            self.conn.close()
        self.chat_frame.grid_forget()
        self.start_btn.config(state="normal")
        self.status_label.config(text="Status: Disconnected", foreground="grey")

if __name__ == "__main__":
    root = tk.Tk()
    app = InitiatorUI(root)
    root.mainloop()
