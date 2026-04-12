import socket
import base64
import time

# --- Protocol Configurations ---
UDP_PORT = 50000
DELIMITER = "|"
TERMINATOR = "\n"
ENCODING = "utf-8"

# --- Message Types (Prefixes) ---
# Discovery via UDP
DISCOVER = "DISCOVER"

# Connection via TCP
HANDSHAKE = "HANDSHAKE"
HANDSHAKE_RESPONSE = "HANDSHAKE_RESPONSE"
TEXT = "TEXT"
ACK = "ACK"
CLOSE = "CLOSE"

def encode_text(text):
    """Encodes text to Base64 to prevent payload delimiter collisions."""
    return base64.b64encode(text.encode(ENCODING)).decode(ENCODING)

def decode_text(b64_str):
    """Decodes Base64 string back to standard text."""
    return base64.b64decode(b64_str.encode(ENCODING)).decode(ENCODING)

def send_msg(sock, prefix, *args):
    """Constructs and sends a delimited UTF-8 message over a socket."""
    msg = prefix
    for arg in args:
        msg += f"{DELIMITER}{arg}"
    msg += TERMINATOR
    try:
        sock.sendall(msg.encode(ENCODING))
    except Exception:
        # Ignore broken pipes on shutdown
        pass

def recv_msg(sock):
    """Reads a single newline-separated message from a TCP socket."""
    data = b""
    while True:
        try:
            chunk = sock.recv(1)
        except socket.timeout:
            continue
        except Exception:
            return None, []
            
        if not chunk:
            return None, []
        data += chunk
        if chunk == b'\n':
            break
            
    decoded = data.decode(ENCODING).strip()
    if not decoded:
        return None, []
        
    parts = decoded.split(DELIMITER)
    return parts[0], parts[1:]
