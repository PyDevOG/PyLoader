# PyLoader Tools

PyLoader Tools is a set of tools designed for building and managing client-server applications with support for various operating systems and advanced features like auto reconnect, rootkits, and startup configuration.

## Features

### ClientBuilder

1. **Server IP and Port Configuration**
   - Allows users to specify the server IP address and port to which the clients will connect.

2. **Target OS Selection**
   - Users can select the target operating system for the client script: Windows, macOS, or Linux.

3. **Auto Reconnect**
   - Enables the client to automatically attempt to reconnect to the server if the connection is lost.

4. **Download and Execute**
   - Allows the server to instruct the client to download and execute files from specified URLs.

5. **Ping Command**
   - Enables the server to send ping commands to the client to check connectivity.

6. **Rootkit Installation**
   - Adds a placeholder for rootkit installation logic specific to each operating system (for educational purposes).

7. **Add to Startup**
   - Configures the client to automatically run at startup for the specified operating system:
     - **Windows**: Adds a batch file to the startup folder.
     - **macOS**: Creates a plist file in `~/Library/LaunchAgents`.
     - **Linux**: Creates a `.desktop` file in `~/.config/autostart`.

8. **Graphical User Interface (GUI)**
   - Provides a user-friendly interface using PyQt5 for configuring client options.

9. **Script Generation**
    - Generates a Python script based on the selected options and target operating system.

10. **Executable Creation**
    - Uses PyInstaller to create a standalone executable for Windows.

### Server

1. **Connection Management**
   - Accepts and manages multiple client connections simultaneously.
   - Displays connection details such as IP address, port, connection time, PC name, country, and antivirus status.

2. **Send Commands**
   - Allows the server to send custom commands to connected clients.

3. **Download and Execute**
   - Instructs clients to download and execute files from specified URLs.

4. **Ping Command**
   - Sends ping commands to clients to verify connectivity.

5. **Disconnect Clients**
   - Allows the server to disconnect specific clients.

6. **Notifications**
   - Displays desktop notifications for new client connections.

7. **GUI with Context Menu**
   - Provides a graphical interface using PyQt5 with a context menu for managing clients.

8. **Connection Status Updates**
   - Periodically checks and updates the status of connected clients.

9. **Client Information Retrieval**
   - Receives and displays initial information from clients such as PC name, country, and antivirus status.

10. **Error Handling**
    - Robust error handling for socket operations and client communication.

11. **Start/Stop Server**
    - Provides buttons to start and stop the server.

12. **Automatic Server Configuration**
    - Configures server settings and starts accepting connections upon launch.

## Requirements

- Python 3.x
- PyQt5
- PyInstaller
- Plyer
- Requests

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/PyDevOG/PyLoader.git
cd PyLoader
