# SCCSE — Secure Cross-Clipboard Sharing Environment

A secure, cryptography-driven desktop application that enables **confidential, authenticated, and ephemeral clipboard sharing** between paired devices.  
The system is designed with a strong emphasis on **modern cryptographic practices**, **secure software architecture**, and **professional-grade user experience**, while remaining fully local and transparent for academic inspection.

---

## Project Overview

SCCSE allows two (or more) devices to securely exchange clipboard contents using a **hybrid cryptographic design** that combines:

- Asymmetric key exchange
- Symmetric authenticated encryption
- Digital signatures for integrity and authenticity
- Time-to-Live (TTL) enforcement for sensitive content
- Secure local history storage (encrypted at rest)

The application was developed as part of **CENG625 – Cryptography and Advanced Computer Security**, with a focus on *correct cryptographic usage rather than re-implementing primitives*.

---

## Key Features

### Cryptographic Security
- Hybrid encryption using **X25519 + AES-GCM**
- Metadata signing with **Ed25519**
- Authenticated sender verification
- Tamper detection on received messages
- Secure pairing via public key exchange

### Ephemeral High-Security Mode
- Optional TTL-based message expiration
- Clipboard auto-purge after TTL expiry
- No high-security content logged or persisted
- Designed for passwords, secrets, and sensitive text

### Secure History
- Encrypted local history using AES-GCM
- Separate encryption key stored locally
- Medium-security messages only
- Clear distinction between transient and persistent data

### Modern Desktop UI
- Multi-tab interface
- Visual security indicators
- Live activity and security logs
- Device pairing management
- Designed to resemble a real cryptographic utility

### Multi-Device Simulation
- Supports multiple logical devices on the same machine
- Device isolation via environment variables
- Ideal for demos, screenshots, and testing

---

## Cryptographic Design

### Algorithms Used
| Purpose | Algorithm |
|------|----------|
| Key Exchange | X25519 |
| Digital Signatures | Ed25519 |
| Symmetric Encryption | AES-256-GCM |
| Hashing | SHA-256 (internal) |

### Design Principles
- **No custom crypto**
- **Authenticated encryption everywhere**
- **Separation of encryption and signing keys**
- **Explicit metadata binding**
- **Fail-closed verification**

---

## Message Flow

1. Clipboard content is captured
2. Metadata is constructed (timestamp, TTL, sender ID)
3. Metadata is signed using Ed25519
4. Payload is encrypted using AES-GCM
5. AES key is derived via X25519 shared secret
6. Bundle is transmitted to the server
7. Receiver verifies signature
8. Receiver decrypts payload
9. TTL is enforced (if applicable)

---

Running the System (Terminal Guide)
-----------------------------------

This section explains how to run SCCSE locally, simulate multiple devices, pair them securely, and perform encrypted clipboard exchange.

### 1️ Prerequisites

Ensure the following are installed:

*   **Python 3.10 or newer**
    
*   pip package manager
    
*   A terminal (Command Prompt / PowerShell / Bash)
    

Verify Python version:

`   python --version   `

### 2️ Install Dependencies

From the project root directory:

`   pip install -r requirements.txt   `

### 3️ Start the Relay Server

Open **Terminal 1** and run:

`   py -m server.app   `

You should see output similar to:

`   INFO: Uvicorn running on http://127.0.0.1:8000   `

⚠️ Keep this terminal open.The server acts as an **untrusted relay** and must remain running.

### 4️ Simulate Device A (First Client)

Open **Terminal 2** and set the device identity:

`   set SCCSE_DEVICE=A   `

Generate cryptographic keys for Device A:

`   py -m client.pairing generate   `

Export Device A’s public keys:

`   py -m client.pairing export   `

✔ This prints a **JSON public bundle** — copy it.

### 5️ Simulate Device B (Second Client)

Open **Terminal 3** and set the second device identity:

`   set SCCSE_DEVICE=B   `

Generate keys for Device B:

`   py -m client.pairing generate   `

Export Device B’s public bundle:

`   py -m client.pairing export   `

✔ Copy the JSON output.

### 6️ Pair the Devices (Mutual Trust)

#### On Device A terminal:

`   py -m client.pairing import   `

Paste **Device B’s JSON bundle**, then press:

`   Ctrl + Z  Enter   `

You should see:

`   ✔ Peer imported successfully   `

#### On Device B terminal:

`   py -m client.pairing import   `

Paste **Device A’s JSON bundle**, then:

`   Ctrl + Z  Enter   `

### 7️ Launch the Client Applications

#### Start Device A UI:

`   set SCCSE_DEVICE=A  py -m client.app   `

#### Start Device B UI (new terminal):

`   set SCCSE_DEVICE=B  py -m client.app   `

 You should now see **two independent UI windows**, each representing a different secure device.

### 8️ Secure Clipboard Demo Flow

1.  Copy text into **Device A**
    
2.  Select **Device B** from the peer dropdown
    
3.  Click **🔒 Encrypt & Send**
    
4.  On Device B, click **📥 Receive & Decrypt**
    
5.  Decrypted text appears in Device B’s clipboard
    
6.  TTL countdown starts for sensitive content
    

### 9️ Reset History (Clean Demo)

To reset encrypted history before recording or screenshots:

`   delete client\data_device_A\history.enc  delete client\data_device_B\history.enc   `

(Use rm instead of delete on Linux/macOS)

### Notes

*   Each device uses **separate cryptographic identities**
    
*   The server **never sees plaintext**
    
*   Password-type clipboard content:
    
    *   Is **not logged**
        
    *   Expires automatically via TTL
        
    *   Is removed from clipboard upon expiration


> ⚠️ **Security Note**  

> No cryptographic keys, clipboard history, or sensitive artifacts are stored in this repository.  

> All secrets are generated locally per device and excluded via `.gitignore`.