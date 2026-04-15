# Local Network Chat Protocol (CLI Version)

A custom application-layer chat protocol implemented in Python, designed for peer-to-peer communication over a local network.

## Project Overview
This project implements the **Simple Local Network Chat Protocol (SLNCP)**. It features a decentralized discovery mechanism using UDP broadcasts and a reliable, half-duplex chat stream over TCP.

### Key Features
- **UDP Discovery:** Locates peers on the local subnet by nickname.
- **TCP Handshake:** Validates connections using a unique UUID and a discovery deadline.
- **Simplex Message Exchange:** Strict half-duplex communication rules (one message at a time).
- **Base64 Encoding:** Ensures message payloads never conflict with protocol delimiters.
- **Clean Termination:** Synchronized connection closure on both ends.

## Prerequisites
- Python 3.x
- Recommended Environment: `/Users/mursalatul/programming/own/after-dinner-projects/after-dinner-projects-py-env`

## How to Use

### 1. Start the Recipient
The recipient listens for discovery broadcasts and responds if the nickname matches.
```bash
python recipient.py <Your_Nickname>
# Example:
python recipient.py Alice
```

### 2. Start the Initiator
The initiator sends a broadcast to find a specific peer and establishes the connection.
```bash
python initiator.py <Target_Nickname> <Timeout_Seconds>
# Example:
python initiator.py Alice 60
```

### 3. Chatting
- Type your message and press **Enter**.
- You must wait for the peer's response (or an implicit ACK) before sending your next message.
- Type `exit` to close the connection.

## Files
- `protocol.py`: Core protocol definitions and encoding logic.
- `initiator.py`: The application that starts the communication.
- `recipient.py`: The application that receives and responds to requests.
- `chat_session.py`: Manages the interactive terminal chat loop.
- `Protocol_Specification.md`: Technical documentation of the protocol design.
