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
    """
    Encodes text to Base64 to prevent payload delimiter collisions.

    Args:
        text (str): The plain text message to encode.

    Returns:
        str: The Base64 encoded string representation of the text.
    """
    return base64.b64encode(text.encode(ENCODING)).decode(ENCODING)

def decode_text(b64_str):
    """
    Decodes Base64 string back to standard text.

    Args:
        b64_str (str): The Base64 encoded string to decode.

    Returns:
        str: The decoded plain text message.
    """
    return base64.b64decode(b64_str.encode(ENCODING)).decode(ENCODING)

def send_msg(sock, prefix, *args):
    """
    Constructs and sends a delimited UTF-8 message over a socket.

    Args:
        sock (socket.socket): The socket over which to send the message.
        prefix (str): The message type prefix (e.g., TEXT, ACK, CLOSE).
        *args: Variable length argument list comprising message payload components.
    """
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
    """
    Reads a single newline-separated message from a TCP socket.

    Args:
        sock (socket.socket): The socket from which to read the message.

    Returns:
        tuple[str, list[str]]: A tuple containing the prefix and a list of delimited arguments,
                               or (None, []) upon failure or connection closure.
    """
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
