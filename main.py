import os
import re
import subprocess

import paramiko

from PyQt6.QtCore import Qt, QTime, QThread, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QPushButton,
                             QListWidget, QMenu, QWidget, QLabel,
                             QComboBox, QHBoxLayout, QListWidgetItem, QMessageBox, QSpacerItem, QSizePolicy, QTabWidget,
                             QFrame)
from cryptography.fernet import Fernet

os.environ["PATH"] = "/usr/sbin:" + os.environ["PATH"]
import os
# print("Path: ", os.environ["PATH"])

# Set the PATH as a global variable
# Define the full paths to the commands
SUDO_PATH = "/usr/bin/sudo"
USBIP_PATH = "/bin/usbip"
CONFIG_FILE = "config.json"
AUTO_CONNECT_FILE = "auto_connect_devices.json"

AUTO_CONNECT_FILE = "auto_connect_devices.json"

def load_auto_connect_devices():
    try:
        with open(AUTO_CONNECT_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_auto_connect_devices(devices):
    with open(AUTO_CONNECT_FILE, "w") as file:
        json.dump(devices, file, indent=4)


from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QSpinBox, QCheckBox, QDialogButtonBox
import json

class HostSinkConfigurationDialog(QDialog):
    def __init__(self, selected_host, parent=None):
        super().__init__(parent)

        self.selected_host = selected_host  # Store the selected host
        self.setWindowTitle("Configure Host Sink and Client Source Settings")
        self.parent_client = parent

        main_layout = QVBoxLayout(self)

        # Titles
        client_title = QLabel("Client Source Settings")
        client_title.setStyleSheet("font-weight: bold;")
        host_title = QLabel("Host Sink Settings")
        host_title.setStyleSheet("font-weight: bold;")

        # Left column for Client Source Settings
        client_source_layout = QFormLayout()
        self.source_ip_client_field = QLineEdit("0.0.0.0")
        client_source_layout.addRow("Source IP:", self.source_ip_client_field)

        self.source_port_client_field = QSpinBox()
        self.source_port_client_field.setRange(1, 65535)
        self.source_port_client_field.setValue(46000)
        client_source_layout.addRow("Source Port:", self.source_port_client_field)

        self.latency_field = QSpinBox()
        self.latency_field.setRange(1, 1000)
        self.latency_field.setValue(24)
        client_source_layout.addRow("Client Latency (ms):", self.latency_field)

        self.always_process_field = QCheckBox("Always Process")
        self.always_process_field.setChecked(True)
        client_source_layout.addRow("Always Process:", self.always_process_field)

        self.client_session_name_field = QLineEdit("rtp-source")
        client_source_layout.addRow("Session Name:", self.client_session_name_field)

        self.client_audio_format_field = QLineEdit("S16BE")
        client_source_layout.addRow("Audio Format:", self.client_audio_format_field)

        self.client_audio_rate_field = QSpinBox()
        self.client_audio_rate_field.setRange(8000, 96000)
        self.client_audio_rate_field.setValue(8000)
        client_source_layout.addRow("Audio Rate:", self.client_audio_rate_field)

        self.client_audio_channels_field = QSpinBox()
        self.client_audio_channels_field.setRange(1, 8)
        self.client_audio_channels_field.setValue(1)
        client_source_layout.addRow("Audio Channels:", self.client_audio_channels_field)

        self.client_node_name_field = QLineEdit("rtp-source")
        client_source_layout.addRow("Node Name:", self.client_node_name_field)

        self.client_node_description_field = QLineEdit("RTP-source")
        client_source_layout.addRow("Node Description:", self.client_node_description_field)

        # Right column for Host Sink Settings
        host_sink_layout = QFormLayout()
        self.source_ip_field = QLineEdit("0.0.0.0")
        host_sink_layout.addRow("Source IP:", self.source_ip_field)

        self.destination_ip_field = QLineEdit("192.168.1.214")
        host_sink_layout.addRow("Destination IP:", self.destination_ip_field)

        self.destination_port_field = QSpinBox()
        self.destination_port_field.setRange(1, 65535)
        self.destination_port_field.setValue(46000)
        host_sink_layout.addRow("Destination Port:", self.destination_port_field)

        self.mtu_field = QSpinBox()
        self.mtu_field.setRange(128, 1500)
        self.mtu_field.setValue(256)
        host_sink_layout.addRow("MTU:", self.mtu_field)

        self.ttl_field = QSpinBox()
        self.ttl_field.setRange(1, 255)
        self.ttl_field.setValue(1)
        host_sink_layout.addRow("TTL:", self.ttl_field)

        self.loop_field = QCheckBox("Loop")
        self.loop_field.setChecked(True)
        host_sink_layout.addRow("Net Loop:", self.loop_field)

        self.min_ptime_field = QSpinBox()
        self.min_ptime_field.setRange(1, 10)
        self.min_ptime_field.setValue(2)
        host_sink_layout.addRow("Min P-Time:", self.min_ptime_field)

        self.max_ptime_field = QSpinBox()
        self.max_ptime_field.setRange(1, 10)
        self.max_ptime_field.setValue(10)
        host_sink_layout.addRow("Max P-Time:", self.max_ptime_field)

        self.session_name_field = QLineEdit("rtp-sink")
        host_sink_layout.addRow("Session Name:", self.session_name_field)

        self.audio_format_field = QLineEdit("S16BE")
        host_sink_layout.addRow("Audio Format:", self.audio_format_field)

        self.audio_rate_field = QSpinBox()
        self.audio_rate_field.setRange(8000, 96000)
        self.audio_rate_field.setValue(8000)
        host_sink_layout.addRow("Audio Rate:", self.audio_rate_field)

        self.audio_channels_field = QSpinBox()
        self.audio_channels_field.setRange(1, 8)
        self.audio_channels_field.setValue(1)
        host_sink_layout.addRow("Audio Channels:", self.audio_channels_field)

        self.node_name_field = QLineEdit("rtp-sink")
        host_sink_layout.addRow("Node Name:", self.node_name_field)

        self.node_description_field = QLineEdit("RTP-sink")
        host_sink_layout.addRow("Node Description:", self.node_description_field)

        # Combine the two columns
        columns_layout = QHBoxLayout()
        left_column = QVBoxLayout()
        left_column.addWidget(client_title)
        left_column.addLayout(client_source_layout)
        left_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        right_column = QVBoxLayout()
        right_column.addWidget(host_title)
        right_column.addLayout(host_sink_layout)
        right_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        columns_layout.addLayout(left_column)
        columns_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        columns_layout.addLayout(right_column)

        main_layout.addLayout(columns_layout)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        self.buttons.rejected.connect(self.reject)

        # Apply>Enable>Test Button
        apply_enable_test_button = QPushButton("Apply>Enable>Test")
        apply_enable_test_button.clicked.connect(self.apply_enable_test)

        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push buttons to the right
        button_layout.addWidget(apply_enable_test_button)
        button_layout.addWidget(self.buttons)

        main_layout.addLayout(button_layout)

        # Load existing settings
        self.load_settings()

    def load_settings(self):
        """Load settings from JSON files and populate the fields."""
        try:
            with open("host_sink_config.json", "r", encoding="utf-8") as host_sink_file:
                host_sink_settings = json.load(host_sink_file)

                self.source_ip_field.setText(host_sink_settings.get("source_ip", "0.0.0.0"))
                self.destination_ip_field.setText(host_sink_settings.get("destination_ip", ""))
                self.destination_port_field.setValue(host_sink_settings.get("destination_port", 46000))
                self.mtu_field.setValue(host_sink_settings.get("mtu", 256))
                self.ttl_field.setValue(host_sink_settings.get("ttl", 1))
                self.loop_field.setChecked(host_sink_settings.get("loop", True))
                self.min_ptime_field.setValue(host_sink_settings.get("min_ptime", 2))
                self.max_ptime_field.setValue(host_sink_settings.get("max_ptime", 10))
                self.session_name_field.setText(host_sink_settings.get("session_name", ""))
                self.audio_format_field.setText(host_sink_settings.get("audio_format", ""))
                self.audio_rate_field.setValue(host_sink_settings.get("audio_rate", 8000))
                self.audio_channels_field.setValue(host_sink_settings.get("audio_channels", 1))
                self.node_name_field.setText(host_sink_settings.get("node_name", ""))
                self.node_description_field.setText(host_sink_settings.get("node_description", ""))

            with open("client_source_config.json", "r", encoding="utf-8") as client_source_file:
                client_source_settings = json.load(client_source_file)

                self.source_ip_client_field.setText(client_source_settings.get("source_ip", ""))
                self.source_port_client_field.setValue(client_source_settings.get("source_port", 46000))
                self.latency_field.setValue(client_source_settings.get("latency", 24))
                self.always_process_field.setChecked(client_source_settings.get("always_process", True))
                self.client_session_name_field.setText(client_source_settings.get("session_name", ""))
                self.client_audio_format_field.setText(client_source_settings.get("audio_format", ""))
                self.client_audio_rate_field.setValue(client_source_settings.get("audio_rate", 8000))
                self.client_audio_channels_field.setValue(client_source_settings.get("audio_channels", 1))
                self.client_node_name_field.setText(client_source_settings.get("node_name", ""))
                self.client_node_description_field.setText(client_source_settings.get("node_description", ""))

        except FileNotFoundError:
            # print("Configuration files not found. Using default values.")
            self.parent_client.add_message("Configuration files not found. Using default values.")
        except Exception as e:
            # print(f"Error loading settings: {e}")
            self.parent_client.add_message(f"Error loading settings: {e}")

    def apply_enable_test(self):
        """Applies settings and refreshes audio devices."""
        # Save settings
        self.save_settings()

        # Enable the modules with the new settings
        self.enable_settings()

        # Test the connection
        self.test_connection()

        # Call the refresh_audio_devices method from the parent
        if self.parent_client:
            self.parent_client.refresh_audio_devices()
        else:
            print("Parent client is not available to refresh audio devices.")
            self.parent_client.add_message("Parent client is not available to refresh audio devices.")


    def enable_settings(self):
        self.push_host_pw_sink_settings()
        self.push_client_pw_source_settings()

    def push_client_pw_source_settings(self):
        try:
            # Load the host sink configuration from the JSON file
            with open("client_source_config.json", "r") as f:
                client_source_config = json.load(f)

            # Extract the values from the JSON file
            source_ip = client_source_config.get("source_ip", "0.0.0.0")
            source_port = client_source_config.get("source_port", 46000)
            latency = client_source_config.get("latency", 256)
            always_process = "true" if client_source_config.get("always_process", True) else "false"
            session_name = client_source_config.get("session_name", "rtp-sink")
            audio_format = client_source_config.get("audio_format", "S16BE")
            audio_rate = client_source_config.get("audio_rate", 8000)
            audio_channels = client_source_config.get("audio_channels", 1)
            node_name = client_source_config.get("node_name", "rtp-sink")
            node_description = client_source_config.get("node_description", "RTP-sink")

            # Define the content of the file
            file_content = f"""
    context.modules = [
    {{
        name = libpipewire-module-rtp-source
        args = {{
            source.ip = "{source_ip}"
            source.port = {source_port}
            sess.latency.msec = {latency}
            node.always-process = {always_process}
            sess.name = "{session_name}"
            sess.media = "audio"
            audio.format = "{audio_format}"
            audio.rate = {audio_rate}
            audio.channels = {audio_channels}
            audio.position = "[ FC ]"
            stream.props = {{
                media.class = "Audio/Source"
                node.name = "{node_name}"
                node.description = "{node_description}"
            }}
        }}
    }}
    ]
    """

            # Write the content to the file
            file_path = os.path.expanduser("~/.config/pipewire/pipewire.conf.d/usbip_pipewire_app_client_source.conf")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists

            with open(file_path, "w") as config_file:
                config_file.write(file_content)

            # Restart PipeWire
            subprocess.run(["systemctl", "--user", "restart", "pipewire.service"], check=True)

        except FileNotFoundError:
            # print("Configuration file not found: client_source_config.json")
            self.parent_client.add_message("Configuration file not found: client_source_config.json")
        except json.JSONDecodeError:
            # print("Error parsing the JSON file.")
            self.parent_client.add_message("Error parsing the JSON file.")
        except subprocess.CalledProcessError as e:
            # print(f"Error restarting PipeWire: {e}")
            self.parent_client.add_message(f"Error restarting PipeWire: {e}")
        except Exception as e:
            # print(f"An unexpected error occurred: {e}")
            self.parent_client.add_message(f"An unexpected error occurred: {e}")

    def push_host_pw_sink_settings(self):
        """Enable PipeWire RTP sink module on the selected host."""
        # Fetch the selected host details (host_ip, user, password)
        if self.selected_host:
            host_ip = self.selected_host['host_ip']
            user = self.selected_host['user']
            password = self.selected_host['password']
            # print(f"Selected host: {host_ip}, User: {user}")  # Debugging output
        else:
            print("No selected host available.")
            self.parent_client.add_message("No selected host available.")
            return

        # Load the host sink configuration from the JSON file
        with open("host_sink_config.json", "r") as f:
            host_sink_config = json.load(f)

        # Extract the values from the JSON file
        source_ip = host_sink_config.get("source_ip", "0.0.0.0")
        destination_ip = host_sink_config.get("destination_ip", "192.168.1.214")
        destination_port = host_sink_config.get("destination_port", 46000)
        mtu = host_sink_config.get("mtu", 256)
        ttl = host_sink_config.get("ttl", 1)
        loop = "true" if host_sink_config.get("loop", True) else "false"
        min_ptime = host_sink_config.get("min_ptime", 2)
        max_ptime = host_sink_config.get("max_ptime", 10)
        session_name = host_sink_config.get("session_name", "rtp-sink")
        audio_format = host_sink_config.get("audio_format", "S16BE")
        audio_rate = host_sink_config.get("audio_rate", 8000)
        audio_channels = host_sink_config.get("audio_channels", 1)
        node_name = host_sink_config.get("node_name", "rtp-sink")
        node_description = host_sink_config.get("node_description", "RTP-sink")

        # Define the content of the file
        file_content = f"""
                context.modules = [
                {{
                    name = libpipewire-module-rtp-sink
                    args = {{
                        source.ip = "{source_ip}"
                        destination.ip = "{destination_ip}"
                        destination.port = {destination_port}
                        net.mtu = {mtu}
                        net.ttl = {ttl}
                        net.loop = {str(loop).lower()}
                        sess.min-ptime = {min_ptime}
                        sess.max-ptime = {max_ptime}
                        sess.name = "{session_name}"
                        sess.media = "audio"
                        audio.format = "{audio_format}"
                        audio.rate = {audio_rate}
                        audio.channels = {audio_channels}
                        audio.position = "[ FC ]"
                        stream.props = {{
                            media.class = "Audio/Sink"
                            node.name = "{node_name}"
                            node.description = "{node_description}"
                        }}
                    }}
                }}
                ]
                """

        # Write the content to the file
        file_path = "~/.config/pipewire/pipewire.conf.d/usbip_pipewire_client.conf"
        command = f"echo '{file_content}' > {file_path}"

        # Debugging output: print the constructed command
        # print(f"Command to send over SSH: {command}")

        # Establish SSH connection to the host
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Debugging output: print SSH connection attempt
        # print(f"Connecting to {host_ip} with username {user}...")
        ssh.connect(host_ip, username=user, password=password)

        # Execute the pw-cli command to load the RTP sink module on the remote host
        stdin, stdout, stderr = ssh.exec_command(command)

        # Read the output and error streams
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Debugging output: print the command output and error (if any)
        if error:
            # print(f"Error: {error}")
            self.parent_client.add_message(f"Error: {error}")
        else:
            # print(f"Output: {output}")
            # print("RTP sink module enabled successfully on remote host.")
            self.parent_client.add_messagef(f"Output: {output}")
            self.parent_client.add_message("RTP sink module enabled successfully on remote host.")

        # Close the SSH connection
        # Execute the pw-cli command to load the RTP sink module on the remote host
        stdin, stdout, stderr = ssh.exec_command("systemctl --user restart pipewire.service")
        # Read the output and error streams
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Debugging output: print the command output and error (if any)
        if error:
            # print(f"Error: {error}")
            self.parent_client.add_message(f"Error: {error}")
        else:
            # print(f"Output: {output}")
            # print("Pipewire successfully restarted on remote host.")
            self.parent_client.add_message(f"Output: {output}")
            self.parent_client.add_message("Pipewire successfully restarted on remote host.")

        ssh.close()

        # Return the output for further inspection
        return output

    def save_settings(self):
        # Save the host sink settings
        host_sink_settings = {
            "source_ip": self.source_ip_field.text(),
            "destination_ip": self.destination_ip_field.text(),
            "destination_port": self.destination_port_field.value(),
            "mtu": self.mtu_field.value(),
            "ttl": self.ttl_field.value(),
            "loop": self.loop_field.isChecked(),
            "min_ptime": self.min_ptime_field.value(),
            "max_ptime": self.max_ptime_field.value(),
            "session_name": self.session_name_field.text(),
            "audio_format": self.audio_format_field.text(),
            "audio_rate": self.audio_rate_field.value(),
            "audio_channels": self.audio_channels_field.value(),
            "node_name": self.node_name_field.text(),
            "node_description": self.node_description_field.text()
        }

        client_source_settings = {
            "source_ip": self.source_ip_client_field.text(),
            "source_port": self.source_port_client_field.value(),
            "latency": self.latency_field.value(),
            "always_process": self.always_process_field.isChecked(),
            "session_name": self.client_session_name_field.text(),
            "audio_format": self.client_audio_format_field.text(),
            "audio_rate": self.client_audio_rate_field.value(),
            "audio_channels": self.client_audio_channels_field.value(),
            "node_name": self.client_node_name_field.text(),
            "node_description": self.client_node_description_field.text()
        }

        try:
            # Use json.dumps to create the JSON string
            with open("host_sink_config.json", "w", encoding="utf-8") as host_sink_file:
                host_sink_file.write(json.dumps(host_sink_settings, indent=4))
            # print("Host sink settings saved to host_sink_config.json")
            self.parent_client.add_message("Host sink settings saved to host_sink_config.json")
            with open("client_source_config.json", "w", encoding="utf-8") as client_source_file:
                client_source_file.write(json.dumps(client_source_settings, indent=4))
            # print("Client source settings saved to client_source_config.json")
            self.parent_client.add_message("Client source settings saved to client_source_config.json")
        except Exception as e:
            # print(f"Failed to save settings: {e}")
            self.parent_client.add_message(f"Failed to save settings: {e}")

    def test_connection(self):
        """Test if the PipeWire node with the specified name exists on the host."""
        client_node_name = self.client_node_name_field.text().strip()

        if not client_node_name:
            QMessageBox.warning(self, "Test Connection", "Host node name is empty!")
            return

        try:
            # Use pw-cli to list available nodes
            result = subprocess.run(
                ["pw-cli", "ls", "Node"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr)

            # Check if the node name exists in the list
            nodes = result.stdout.splitlines()
            if any(client_node_name in node for node in nodes):
                QMessageBox.information(
                    self,
                    "Test Connection",
                    f"Successfully found host node on client '{client_node_name}'."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Test Connection",
                    f"No host node found with the name '{client_node_name}'."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Test Connection",
                f"Failed to test connection.\n\nError: {e}",
            )


def list_devices_on_host(host_ip, user, password):
    """List USB devices on the host and number them."""
    devices = []

    # Set up SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host_ip, username=user, password=password)

    # Execute command to list USB devices
    stdin, stdout, stderr = ssh.exec_command('sudo usbip list -l')

    # Read and process the command output
    output = stdout.readlines()
    n = 0
    device_info = ""
    for line in output:
        if line.startswith("Listing USB devices on host"):
            continue
        if line.strip() == "":
            if device_info:
                devices.append(device_info)
                device_info = ""
            continue
        if 'busid' in line:
            if device_info:
                devices.append(device_info)
            n += 1
            device_info = f"{n} - {line.strip()}\n"
        else:
            device_info += f"{line.strip()}\n"

    if device_info:
        devices.append(device_info)


    # Close SSH connection
    ssh.close()
    # print("DEVICES: ", devices)
    return devices


def get_attached_devices():
    """Executes 'sudo usbip port' on this machine and returns the attached devices with their host IP."""
    attached_devices = []

    # Execute the usbip port command on this machine
    result = subprocess.run(['sudo', 'usbip', 'port'], stdout=subprocess.PIPE)

    # Read and process the command output
    output = result.stdout.decode().splitlines()
    for line in output:
        if '-> usbip://' in line:
            # print("LINE: ", line)
            # Example line: 5-1 -> usbip://192.168.1.232:3240/1-1.1
            device_info = line.split('->')[-1].strip()  # Get everything after '->'
            busid = device_info.split('/')[-1]  # Get the part after the last forward slash
            host_ip = device_info.split('://')[1].split(':')[0]  # Get the host IP (before the port)
            # print(f"BUSID: {busid}, HOST_IP: {host_ip}")
            attached_devices.append((busid, host_ip))  # Store as a tuple

    # print("ATTACHED DEVICES: ", attached_devices)
    return attached_devices


def is_device_attached(busid, host_ip, attached_devices):
    """Checks if the device with the given busid and host_ip is already attached."""
    return (busid, host_ip) in attached_devices


def save_last_selected_host(index):
    """Save the last selected host index to a configuration file."""
    try:
        config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)

        config["last_selected_host_index"] = index
        print(f"Saving config: {config}")

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving last selected host: {e}")





def get_key():
    """Get or generate the encryption key."""
    try:
        with open('key.key', 'rb') as key_file:
            key = key_file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open('key.key', 'wb') as key_file:
            key_file.write(key)
    return key


class USBIPClient(QMainWindow):
    class Device:
        def __init__(self, device_data, host_ip):
            device_data_parts = device_data.split()  # Split the string into words
            self.number = "Number: " + device_data_parts[0]
            self.busid = device_data_parts[4]
            self.description = " ".join(device_data_parts[6:])  # Grab everything after the 4th word

            self.host_ip = host_ip  # Store the associated host IP
            self.connected = False  # Initialize as disconnected

        def set_connected(self):
            """Set the device as connected."""
            self.connected = True

        def set_disconnected(self):
            """Set the device as disconnected."""
            self.connected = False

        def __str__(self):
            return f"{self.number} - {self.description} (Bus ID: {self.busid}, Host IP: {self.host_ip})"

        def update_widget_status(self, widget):
            """Update the widget's status based on the device connection status."""
            if self.connected:
                widget.set_connected()  # If connected, update the widget's status
            else:
                widget.set_disconnected()  # If disconnected, update the widget's status

    class DeviceWidget(QWidget):
        def __init__(self, device: 'USBIPClient.Device'):
            super().__init__()
            self.layout = QHBoxLayout(self)
            self.status_icon = QLabel()  # Label to display the green dot
            self.status_icon.setText("⚪")  # Default to white dot for "disconnected"
            self.status_icon.setStyleSheet("color: gray; font-size: 16px;")  # Set style for the dot
            self.device_label = QLabel(f"{device.busid} - {device.description}")


            self.layout.addWidget(self.status_icon)
            self.layout.addWidget(self.device_label)

            self.layout.addStretch()

            self.device = device  # Store the Device object as an attribute

        def set_connected(self):
            self.status_icon.setText("🟢")  # Change to green dot for "connected"
            self.status_icon.setStyleSheet("color: #00FF00; font-size: 16px;")  # Brighter green color

        def set_disconnected(self):
            self.status_icon.setText("⚪")  # Change to white dot for "disconnected"
            self.status_icon.setStyleSheet("color: gray; font-size: 16px;")  # Update style for disconnected

    def __init__(self):
        super().__init__()
        self.auto_connect_devices = load_auto_connect_devices()
        self.setWindowTitle("USB-Audio-IP Client")
        self.setGeometry(100, 100, 500, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)

        # Horizontal layout for host dropdown and buttons
        host_layout = QHBoxLayout()

        # Add a dropdown to select host
        self.host_dropdown = QComboBox()
        self.host_dropdown.currentIndexChanged.connect(self.startup_select_host)
        host_layout.addWidget(self.host_dropdown)

        # Add buttons for adding, editing, and deleting hosts
        self.config_button = QPushButton("Add")
        self.config_button.clicked.connect(self.show_config_dialog)
        host_layout.addWidget(self.config_button)

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_host)
        host_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Remove")
        self.delete_button.clicked.connect(self.delete_host)
        host_layout.addWidget(self.delete_button)

        # Add host layout to the usbip tab
        self.layout.addLayout(host_layout)

        # Create the QTabWidget for tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # **USBIP Device Stuff Tab**
        self.usbip_tab = QWidget()
        self.usbip_tab_layout = QVBoxLayout(self.usbip_tab)

        # Hosts configuration
        self.hosts = []
        self.selected_host = None

        # Block signals temporarily while loading hosts
        self.host_dropdown.blockSignals(True)
        self.load_hosts()
        self.host_dropdown.blockSignals(False)  # Re-enable signals

        # Connect the currentIndexChanged signal to click_select_host
        self.host_dropdown.currentIndexChanged.connect(self.click_select_host)

        # Ensure the selected host matches the saved index
        last_selected_index = self.load_last_selected_host()
        if last_selected_index is not None and 0 <= last_selected_index < len(self.hosts):
            self.host_dropdown.setCurrentIndex(last_selected_index)
            self.startup_select_host(last_selected_index)

        self.auto_connect_devices = load_auto_connect_devices()

        # Horizontal layout for the buttons (including the new Restart USBIP button)
        button_layout = QHBoxLayout()

        # Add Restart USBIP button
        self.restart_button = QPushButton("Restart USBIP")
        self.restart_button.clicked.connect(self.restart_usbip)
        button_layout.addWidget(self.restart_button)

        # Add Refresh USB Devices button
        self.refresh_button = QPushButton("Refresh USB Devices")
        self.refresh_button.clicked.connect(self.refresh_device_list)
        button_layout.addWidget(self.refresh_button)

        # Add button layout to the usbip tab
        self.usbip_tab_layout.addLayout(button_layout)

        # Add a QListWidget for devices
        self.device_list = QListWidget()
        self.device_list.itemDoubleClicked.connect(self.connect_device)
        self.device_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.device_list.customContextMenuRequested.connect(self.show_context_menu)
        self.usbip_tab_layout.addWidget(self.device_list)

        # Add USBIP tab to the tab widget
        self.tabs.addTab(self.usbip_tab, "USBIP Devices")

        # **Pipewire Audio Settings Tab**
        self.pipewire_tab = QWidget()
        self.pipewire_tab_layout = QVBoxLayout(self.pipewire_tab)

        # Configure Button for Host Sink Settings
        self.configure_button = QPushButton("Configure Host Sink and Client Source Settings")
        self.configure_button.clicked.connect(self.show_configuration_dialog)
        self.pipewire_tab_layout.addWidget(self.configure_button)

        # Horizontal layout for audio buttons (including Restart Client and Host PW)
        audio_button_layout = QHBoxLayout()

        # Add Restart Client PW button
        self.restart_client_pw_button = QPushButton("Restart Client PW")
        self.restart_client_pw_button.clicked.connect(self.restart_client_pipewire)
        audio_button_layout.addWidget(self.restart_client_pw_button)

        # Add Restart Host PW button
        self.restart_host_pw_button = QPushButton("Restart Host PW")
        self.restart_host_pw_button.clicked.connect(self.restart_host_pipewire)
        audio_button_layout.addWidget(self.restart_host_pw_button)

        # Add Refresh Audio Devices button
        self.refresh_audio_button = QPushButton("Refresh Audio Devices")
        self.refresh_audio_button.clicked.connect(self.refresh_audio_devices)
        audio_button_layout.addWidget(self.refresh_audio_button)

        # Add the audio button layout to the pipewire tab layout
        self.pipewire_tab_layout.addLayout(audio_button_layout)

        # Section Title for Pipewire Audio Streaming
        self.pipewire_title = QLabel("Host Audio Devices")
        self.pipewire_title.setStyleSheet("font-size: 16px; font-weight: bold;")  # Styling for the title
        self.pipewire_tab_layout.addWidget(self.pipewire_title)

        # Section to display the audio devices
        self.audio_devices_list = QListWidget()
        self.pipewire_tab_layout.addWidget(self.audio_devices_list)

        # Section Title for Pipewire Audio Streaming
        self.pipewire_title = QLabel("Host Linked Audio Devices")
        self.pipewire_title.setStyleSheet("font-size: 16px; font-weight: bold;")  # Styling for the title
        self.pipewire_tab_layout.addWidget(self.pipewire_title)

        # Section to display the linked devices
        self.linked_devices_list = QListWidget()  # Add this list for linked devices
        self.pipewire_tab_layout.addWidget(self.linked_devices_list)  # Add it to the layout

        # Add Pipewire tab to the tab widget
        self.tabs.addTab(self.pipewire_tab, "Pipewire Streams")

        # **Messages Tab**
        self.messages_tab = QWidget()
        self.messages_tab_layout = QVBoxLayout(self.messages_tab)

        # Add a QListWidget to display system messages
        self.messages_list = QListWidget()
        self.messages_tab_layout.addWidget(self.messages_list)

        # Add Messages tab to the tab widget
        self.tabs.addTab(self.messages_tab, "Messages")

        self.refresh_device_list()
        self.refresh_audio_devices()

        # Debug statement to confirm UI initialization
        print("Initialization complete.")

    def load_last_selected_host(self):
        """Load the last selected host index from a configuration file."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    # print(f"Loaded config: {config}")
                    return config.get("last_selected_host_index")
        except Exception as e:
            # print(f"Error loading last selected host: {e}")
            self.add_message(f"Error loading last selected host: {e}")
        return None

    def restart_client_pipewire(self):
        """Method to restart the client PipeWire and handle errors."""
        try:
            # Attempt to restart PipeWire using systemctl
            subprocess.run(["systemctl", "--user", "restart", "pipewire.service"], check=True)
            # On success, add a success message
            self.add_message("Client PipeWire restarted successfully.", message_type="info")
        except subprocess.CalledProcessError as e:
            # On failure, add an error message
            error_message = f"Failed to restart Client PipeWire: {str(e)}"
            self.add_message(error_message, message_type="error")

    def add_message(self, message, message_type="info"):
        """Method to add messages with colored dots to the Messages tab."""
        current_time = QTime.currentTime().toString("HH:mm:ss")
        formatted_message = f"{current_time} - {message}"

        item = QListWidgetItem(formatted_message)

        # Add the message to the list
        self.messages_list.addItem(item)

    def restart_host_pipewire(self):
        """Handle the restart of USBIP service and refresh the device list."""
        # print("Restarting Host Pipewire...")

        # # Ensure a host is selected
        # if self.selected_host is None:
        #     self.show_config_dialog()
        #     return

        host_ip = self.selected_host['host_ip']
        username = self.selected_host['user']
        password = self.selected_host['password']

        try:
            # print(f"Attempting to connect to {host_ip} with user {username}")
            ssh = paramiko.SSHClient()

            # Set missing host key policy to auto add
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the remote SSH server
            ssh.connect(host_ip, username=username, password=password)
            # print(f"Connected to {host_ip}. Restarting Host Pipewire service...")

            # Execute the command to restart the USBIP service
            stdin, stdout, stderr = ssh.exec_command("systemctl --user restart pipewire")
            # stdin.write(f"{password}\n")  # Provide password for sudo
            # stdin.flush()

            # Capture command output and error
            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                self.add_message(f"Failed to restart Host Pipewire service: {error}")
            else:
                # print(f"Host Pipewire service restarted successfully: {output}")
                self.add_message("Host Pipewire service restarted successfully.")

                # Refresh the device list after restarting the USBIP service
                # self.refresh_audio_devices()
                self.refresh_linked_devices()

        except paramiko.SSHException as e:
            self.add_message(f"SSH connection error: {e}")
        except Exception as e:
            self.add_message(f"Error restarting Host Pipewire service: {str(e)}")
        finally:
            ssh.close()
            # print("SSH connection closed.")

    def restart_usbip(self):
        """Handle the restart of USBIP service and refresh the device list."""
        if not self.selected_host:
            self.add_message("No host selected. Please select a host.", message_type="error")
            return

        host_ip = self.selected_host['host_ip']
        username = self.selected_host['user']
        password = self.selected_host['password']

        # Create a dialog to show that the process is running
        self.restart_dialog = QMessageBox(self)
        # self.restart_dialog.setIcon(QMessageBox.Information)
        self.restart_dialog.setText("Restarting Host USBIP. This may take a while...")
        self.restart_dialog.setWindowTitle("Restarting USBIP Service")
        # self.restart_dialog.setStandardButtons(QMessageBox.NoButton)  # No buttons (just informational)
        self.restart_dialog.setModal(True)
        self.restart_dialog.show()

        # Run the restart process in a separate thread
        self.restart_thread = RestartThread(self, host_ip, username, password)

        # Connect the signal from the thread to the slot that handles completion
        self.restart_thread.restart_complete_signal.connect(self.restart_complete)

        self.restart_thread.start()

    def restart_complete(self, message_type, message):
        """Call this when the restart operation is complete."""
        if self.restart_dialog:
            self.restart_dialog.close()  # Close the progress dialog when done
            self.restart_dialog = None

        # Add the message to the list with the appropriate message type
        self.add_message(message, message_type=message_type)

    def show_configuration_dialog(self):
        if self.selected_host:
            dialog = HostSinkConfigurationDialog(self.selected_host, parent=self)
            dialog.exec()
        else:
            print("No host selected!")



    def show_config_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Host Configuration")

        layout = QVBoxLayout(dialog)

        # Host IP input
        self.host_ip_input = QLineEdit(dialog)
        self.host_ip_input.setPlaceholderText("Host IP")
        layout.addWidget(QLabel("Host IP:"))
        layout.addWidget(self.host_ip_input)

        # Username input
        self.user_input = QLineEdit(dialog)
        self.user_input.setPlaceholderText("Username")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.user_input)

        # Password input
        self.password_input = QLineEdit(dialog)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Password")
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # Show dialog and get results
        if dialog.exec():
            host_ip = self.host_ip_input.text()
            user = self.user_input.text()
            password = self.password_input.text()
            host = {"host_ip": host_ip, "user": user, "password": password}
            self.hosts.append(host)
            self.save_hosts()
            self.update_host_dropdown()

    def edit_host(self):
        """Edit the selected host."""
        if self.selected_host:
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Host Configuration")

            layout = QVBoxLayout(dialog)

            # Host IP input
            self.host_ip_input = QLineEdit(dialog)
            self.host_ip_input.setText(self.selected_host['host_ip'])
            layout.addWidget(QLabel("Host IP:"))
            layout.addWidget(self.host_ip_input)

            # Username input
            self.user_input = QLineEdit(dialog)
            self.user_input.setText(self.selected_host['user'])
            layout.addWidget(QLabel("Username:"))
            layout.addWidget(self.user_input)

            # Password input
            self.password_input = QLineEdit(dialog)
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_input.setText(self.selected_host['password'])
            layout.addWidget(QLabel("Password:"))
            layout.addWidget(self.password_input)

            # Dialog buttons
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # Show dialog and get results
            if dialog.exec():
                self.selected_host['host_ip'] = self.host_ip_input.text()
                self.selected_host['user'] = self.user_input.text()
                self.selected_host['password'] = self.password_input.text()
                self.save_hosts()
                self.update_host_dropdown()

    def ping_host(self, host_ip):
        """Ping the host to check if it is reachable."""
        try:
            # Perform the ping using the system's ping command
            response = subprocess.run(
                ["ping", "-c", "1", host_ip],  # Ping once (-c 1)
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # Check if the response indicates success (exit code 0)
            if response.returncode == 0:
                return True
            else:
                # Check the stderr for details on why it failed
                # print(f"Ping failed: {response.stderr.decode()}")
                return False
        except Exception as e:
            # print(f"Error while pinging host {host_ip}: {e}")
            return False

    def refresh_device_list(self):
        self.device_list.clear()
        try:
            # if self.selected_host is None:
            #     self.show_config_dialog()

            if self.selected_host:
                host_ip = self.selected_host['host_ip']

                try:
                    devices_data = list_devices_on_host(
                        host_ip,
                        self.selected_host['user'],
                        self.selected_host['password']
                    )
                except Exception as e:
                    self.add_message(f"Unable to connect to host: {str(e)}")
                    return

                # Get the list of attached devices from the 'usbip port' command on the client machine
                try:
                    attached_devices = get_attached_devices()
                except Exception as e:
                    self.add_message(f"Failed to retrieve attached devices: {str(e)}")
                    return


                self.devices = []

                # Loop through each device and check if it is already attached
                for device_data in devices_data:
                    try:
                        # print("DEVICE DATA: ", device_data)
                        # Pass host_ip to the Device constructor
                        device = self.Device(device_data, host_ip)

                        # Check if the device is already attached by matching busid and host_ip
                        if is_device_attached(device.busid, device.host_ip, attached_devices):
                            device.set_connected()  # Mark as connected by updating the 'connected' attribute
                        else:
                            device.set_disconnected()  # Mark as disconnected if not found in attached devices

                        self.devices.append(device)

                        # Print the device details
                        # print("DEVICE: ", device)

                        # Create custom widget and add it as a list item
                        device_widget = self.DeviceWidget(device)
                        list_item = QListWidgetItem(self.device_list)
                        list_item.setSizeHint(device_widget.sizeHint())
                        self.device_list.addItem(list_item)
                        self.device_list.setItemWidget(list_item, device_widget)

                        # Update the widget's status based on the device's connection status
                        device.update_widget_status(device_widget)

                    except Exception as e:
                        # print(f"Failed to process device {device_data}: {str(e)}")
                        self.add_message(f"Error processing device: {device_data}")

                for device in self.devices:
                    if device.busid in self.auto_connect_devices and not device.connected:
                        self.bind_unbind_device(device.host_ip, self.selected_host['user'],
                                                self.selected_host['password'],
                                                "bind", device.busid)
                        device.set_connected()

        except Exception as e:
            self.add_message(f"An error occurred: {str(e)}")

    # def display_error_message(self, message):
    #     """Display an error message in the QListWidget."""
    #     error_message = QLabel(message)
    #     error_item = QListWidgetItem(self.device_list)  # Create a QListWidgetItem for the error message
    #     error_item.setSizeHint(error_message.sizeHint())  # Set size hint for the item
    #     self.device_list.addItem(error_item)  # Add the item to the list
    #     self.device_list.setItemWidget(error_item, error_message)  # Set the QLabel as the widget for the item

    def connect_device(self, item):
        device_widget = self.device_list.itemWidget(item)  # Get the widget to access the Device object
        if device_widget.device:
            device = device_widget.device  # Retrieve the Device object

            # Use the device's host_ip and busid for the connection
            host_ip = device.host_ip
            busid = device.busid
            command = "bind"

            # Call the bind/unbind method using the host_ip and busid
            if self.bind_unbind_device(host_ip, self.selected_host['user'], self.selected_host['password'], command, busid):

                # Update the widget with the green dot
                item_widget = self.device_list.itemWidget(item)
                if item_widget.device:
                    item_widget.set_connected()
                    device.set_connected()

    def disconnect_device(self, item):
        device_widget = self.device_list.itemWidget(item)  # Get the widget to access the Device object
        if device_widget.device:
            device = device_widget.device  # Retrieve the Device object

            # Use the device's host_ip and busid for the connection
            host_ip = device.host_ip
            busid = device.busid
            command = "unbind"

            # Call the bind/unbind method using the host_ip and busid
            if self.bind_unbind_device(host_ip, self.selected_host['user'], self.selected_host['password'], command, busid):

                # Update the widget with the green dot
                item_widget = self.device_list.itemWidget(item)
                if item_widget.device:
                    item_widget.set_disconnected()
                    device.set_disconnected()

    def add_auto_connect_device(self, device, item):
        self.auto_connect_devices.append(device.busid)
        save_auto_connect_devices(self.auto_connect_devices)
        QMessageBox.information(self, "Device Added", f"Device {device.busid} added to auto-connect.")
        self.connect_device(item)

    def remove_auto_connect_device(self, device):
        self.auto_connect_devices.remove(device.busid)
        save_auto_connect_devices(self.auto_connect_devices)
        QMessageBox.information(self, "Device Removed", f"Device {device.busid} removed from auto-connect.")

    def show_context_menu(self, pos):
        item = self.device_list.itemAt(pos)
        if not item:
            return  # No item at the position, do nothing

        # Create the main context menu
        menu = QMenu(self)

        # Add auto-connect options directly to the main menu
        device_widget = self.device_list.itemWidget(item)
        if device_widget.device:
            device = device_widget.device
            if device.connected:
                menu.addAction("Detach", lambda: self.disconnect_device(item))
            else:
                menu.addAction("Attach", lambda: self.connect_device(item))
            if device.busid in self.auto_connect_devices:
                menu.addAction("Remove from Auto-Connect", lambda: self.remove_auto_connect_device(device))
            else:
                menu.addAction("Add to Auto-Connect", lambda: self.add_auto_connect_device(device, item))

        # Execute the context menu
        action = menu.exec(self.device_list.viewport().mapToGlobal(pos))
        #
        # # Handle Attach/Detach actions
        # if action == connect_action:
        #     self.connect_device(item)
        # elif action == detach_action:
        #     self.disconnect_device(item)

    def bind_unbind_device(self, host_ip, user, password, command, busid):
        """Bind or unbind a device based on user selection."""
        try:
            print(f"Attempting to connect to {host_ip} with user {user}")
            ssh = paramiko.SSHClient()

            # Set missing host key policy to auto add
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Print the host IP and username for debugging
            print(f"Connecting to {host_ip} as {user}...")

            # Connect to the remote SSH server
            ssh.connect(host_ip, username=user, password=password)

            print(f"Connected to {host_ip}. Executing command...")

            # Execute the command
            stdin, stdout, stderr = ssh.exec_command(f'sudo usbip {command} -b {busid}')

            # Print command output for debugging
            print(f"Command output: {stdout.read().decode()}")
            print(f"Command error: {stderr.read().decode()}")

        except paramiko.SSHException as e:
            print(f"SSH connection error: {e}")
            return False
        finally:
            ssh.close()
            print("SSH connection closed.")
        if command == "unbind":
            return True
        if command == "bind":
            try:
                # if os.name == 'nt':  # If running on Windows
                #     result = subprocess.run(["usbip", "attach", "-r", host_ip, "-b", busid], capture_output=True)
                # else:
                result = subprocess.run(["sudo", "usbip", "attach", "-r", host_ip, "-b", busid],
                                            capture_output=True)
            except FileNotFoundError:
                result = subprocess.run(["sudo", "usbip", "attach", "-r", host_ip, "-b", busid], capture_output=True)

            if result.returncode == 0:
                print(f"Successfully attached {busid} from {host_ip}.")
                return True
            else:
                print(f"Failed to attach {busid} from {host_ip}. {result.stderr.decode()}")
                return False

    def delete_host(self):
        """Delete the selected host."""
        if self.selected_host:
            self.hosts.remove(self.selected_host)
            self.save_hosts()
            self.update_host_dropdown()

    def load_hosts(self):
        """Load hosts from an encrypted file."""
        try:
            key = get_key()
            cipher_suite = Fernet(key)
            with open('hosts.enc', 'rb') as config_file:
                encrypted_data = config_file.read()
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            self.hosts = json.loads(decrypted_data.decode())
            self.update_host_dropdown()

            # Load the last selected host index
            last_selected_index = self.load_last_selected_host()
            print(f"Loaded last selected index: {last_selected_index}")

            # Ensure dropdown is populated before setting the index
            if last_selected_index is not None and 0 <= last_selected_index < len(self.hosts):
                self.host_dropdown.setCurrentIndex(last_selected_index)
                # self.startup_select_host(last_selected_index)
        except FileNotFoundError:
            self.hosts = []

    def startup_select_host(self, index):
        """Select a host and save the selection."""
        if index >= 0 and index < len(self.hosts):
            self.selected_host = self.hosts[index]
            # print(f"Selected host: {self.selected_host['host_ip']}")
            save_last_selected_host(index)
        else:
            # print(f"Invalid index: {index}")
            self.add_message(f"Invalid index: {index}")

    # Define the click_select_host function
    def click_select_host(self):
        selected_index = self.host_dropdown.currentIndex()
        if 0 <= selected_index < len(self.hosts):
            self.selected_host = self.hosts[selected_index]
            # print(f"Selected host: {self.selected_host}")
            self.refresh_device_list()
            self.refresh_audio_devices()
            # Add additional logic as needed

    def save_hosts(self):
        """Save the hosts list to an encrypted file."""
        try:
            key = get_key()
            cipher_suite = Fernet(key)
            encrypted_data = cipher_suite.encrypt(json.dumps(self.hosts).encode())
            with open('hosts.enc', 'wb') as config_file:
                config_file.write(encrypted_data)
        except Exception as e:
            # print(f"Error saving hosts: {e}")
            self.add_message(f"Error saving hosts: {e}")

    def update_host_dropdown(self):
        """Update the dropdown menu with the list of hosts."""
        self.host_dropdown.clear()
        for host in self.hosts:
            self.host_dropdown.addItem(host['host_ip'])

    def refresh_audio_devices(self):
        """Fetch and display available audio devices."""
        if self.selected_host:
            # Get the list of audio devices from the host
            pw_cli_output = self.fetch_audio_devices(
                self.selected_host['host_ip'],
                self.selected_host['user'],
                self.selected_host['password']
            )

            # Parse and filter the audio devices
            audio_devices = self.parse_audio_devices(pw_cli_output)

            # Clear the existing list
            self.audio_devices_list.clear()

            # Add each audio device to the list widget with a link button to the left
            for device in audio_devices:
                # Create an empty list item
                item = QListWidgetItem()

                # Create a QWidget to contain the button and device name
                widget = QWidget()
                layout = QHBoxLayout()  # Horizontal layout for button and label

                # Create the link button with a fixed size
                link_button = QPushButton("Link")
                link_button.setFixedWidth(80)  # Set a fixed width for the buttons
                # Connect the button click event to show the device link menu
                link_button.clicked.connect(
                    lambda checked, device=device, button=link_button: self.show_device_link_menu(device, audio_devices,
                                                                                                  button))

                # Create the label for the device name
                device_label = QLabel(device)

                # Add the button and label to the layout
                layout.addWidget(link_button)  # Button first (left side)
                layout.addWidget(device_label)  # Label next (right side)

                # Set the layout to the QWidget
                widget.setLayout(layout)

                # Attach the QWidget to the QListWidgetItem
                item.setSizeHint(widget.sizeHint())  # Make sure the widget size fits the item
                self.audio_devices_list.addItem(item)
                self.audio_devices_list.setItemWidget(item, widget)

            # Fetch linked devices and update the UI
            self.refresh_linked_devices()

    def refresh_linked_devices(self):
        """Fetch and display linked devices."""
        if self.selected_host:
            # Fetch the linked devices using the 'pw-link -l' command
            linked_devices_output = self.fetch_linked_devices(
                self.selected_host['host_ip'],
                self.selected_host['user'],
                self.selected_host['password']
            )


            # Clear the existing linked devices list
            self.linked_devices_list.clear()

            self.linked_devices_list.addItem(linked_devices_output)

    def fetch_linked_devices(self, host_ip, user, password):
        """Fetch the linked devices from the host using pw-link -ls."""
        try:
            # Establish SSH connection
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host_ip, username=user, password=password)

            # Run the pw-link -ls command to get the list of linked devices
            stdin, stdout, stderr = ssh.exec_command("pw-link -l")
            output = stdout.read().decode()

            # Close the SSH connection
            ssh.close()

            return output
        except Exception as e:
            self.add_message(f"Failed to fetch linked devices: {str(e)}")
            return ""


    def show_device_link_menu(self, device, audio_devices, button):
        """Show a menu to select a device to link with."""
        menu = QMenu(self)

        # Create a menu action for each other device
        for other_device in audio_devices:
            if other_device != device:
                action = QAction(other_device, self)
                action.triggered.connect(
                    lambda checked, device=device, other_device=other_device: self.link_audio_devices(device,
                                                                                                      other_device))
                menu.addAction(action)

        # Show the menu at the position of the clicked button
        menu.exec(button.mapToGlobal(button.pos()))

    def link_audio_devices(self, device1, device2):
        """Send SSH command to link two audio devices."""
        try:
            # Establish SSH connection
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.selected_host['host_ip'], username=self.selected_host['user'],
                        password=self.selected_host['password'])

            # Send the pw-link command
            command = f"pw-link {device1} {device2}"
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()

            # Check for any error in the output
            if error:
                self.add_message(f"Error linking devices: {error}")
            else:
                self.add_message(f"Successfully linked {device1} and {device2}.")

            self.refresh_linked_devices()
            # Close the SSH connection
            ssh.close()

        except Exception as e:
            self.add_message(f"Failed to link audio devices: {str(e)}")

    def parse_audio_devices(self, pw_cli_output):
        """Parse and filter audio devices from the pw-cli output."""
        audio_devices = []

        # Split the output into blocks of each device info
        device_blocks = pw_cli_output.split('id ')

        for block in device_blocks:
            # Check if the block contains "Audio" in node.description
            if "node.description = " in block and "Audio" in block:
                # Extract the node.name
                match = re.search(r'node.name = "(.*?)"', block)
                if match:
                    audio_device = match.group(1)
                    audio_devices.append(audio_device)

        return audio_devices

    def fetch_audio_devices(self, host_ip, user, password):
        """Fetch available audio devices from the host using pw-cli."""
        try:
            # Establish SSH connection
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host_ip, username=user, password=password)

            # Run the pw-cli ls Node command to get the list of nodes
            stdin, stdout, stderr = ssh.exec_command("pw-cli ls Node")
            output = stdout.read().decode()

            # Close the SSH connection
            ssh.close()

            return output
        except Exception as e:
            self.add_message(f"Failed to fetch audio devices: {str(e)}")
            return ""


class RestartThread(QThread):
    """Thread to handle the restart of USBIP service in the background."""
    restart_complete_signal = pyqtSignal(str, str)  # Signal to notify completion

    def __init__(self, parent, host_ip, username, password):
        super().__init__(parent)
        self.host_ip = host_ip
        self.username = username
        self.password = password

    def run(self):
        """Run the SSH command to restart USBIP."""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host_ip, username=self.username, password=self.password)

            # Restart USBIP service
            stdin, stdout, stderr = ssh.exec_command("sudo systemctl restart usbipd")

            # Capture the output
            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                self.restart_complete_signal.emit("error", f"Failed to restart USBIP service: {error}")
            else:
                self.restart_complete_signal.emit("info", "USBIP service restarted successfully.")
                # self.parent().refresh_device_list()

        except paramiko.SSHException as e:
            self.restart_complete_signal.emit("error", f"SSH connection error: {e}")
        except Exception as e:
            self.restart_complete_signal.emit("error", f"Error restarting USBIP service: {str(e)}")
        finally:
            ssh.close()

if __name__ == "__main__":
    app = QApplication([])
    client = USBIPClient()
    client.show()
    app.exec()
