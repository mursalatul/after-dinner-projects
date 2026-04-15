# Local Network Chat Protocol (UI Version)

A graphical implementation of the Simple Local Network Chat Protocol (SLNCP), featuring a modern user interface for local peer-to-peer communication.

## Project Overview
This version of the SLNCP project provides a **Tkinter-based GUI** for both the Initiator and Recipient roles. It manages background networking threads to keep the interface responsive while handling discovery, handshaking, and chatting.

### Key Features
- **Graphical Interface:** Easy-to-use windows with status indicators and message logs.
- **Robust Periodic Discovery:** The Initiator broadcasts every 2 seconds to ensure a reliable connection even if the Recipient starts later.
- **Visual Flow Control:** The "Send" button is automatically disabled until an ACK is received, visually demonstrating the half-duplex nature of the protocol.
- **State Synchronization:** Status bars update in real-time (e.g., turning RED when a peer disconnects).
- **One-Click Controls:** Buttons for "Stop Discovery", "Stop Listening", and "Exit".

## Prerequisites
- Python 3.x
- Recommended Environment: `/Users/mursalatul/programming/own/after-dinner-projects/after-dinner-projects-py-env`
- Uses built-in `tkinter` (no external GUI library required).

## How to Use

### 1. Start the Recipient UI
```bash
python recipient_ui.py
```
- Enter your nickname in the input field.
- Click **Start Listening**. The status will change to "Listening for broadcasts...".

### 2. Start the Initiator UI
```bash
python initiator_ui.py
```
- Enter the target peer's nickname and a discovery timeout.
- Click **Start Discovery**. The Initiator will broadcast every 2 seconds.

### 3. Chatting
- Once connected, the "Chat Room" section will appear.
- Type your message in the entry box and press **Enter** or click **Send**.
- Observe the "Send" button disabling until the peer acknowledges your message.
- Click **Exit** to terminate the session and notify the peer.

## Files
- `protocol.py`: Core logic for SLNCP frames.
- `initiator_ui.py`: Graphical application for the Initiator role.
- `recipient_ui.py`: Graphical application for the Recipient role.
- `Protocol_Specification.md`: Technical documentation of the protocol design.
