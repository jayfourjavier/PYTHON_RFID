import sys
import re
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, 
    QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, 
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QDateTime, QTimer

class RFIDApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RFID Management System")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)  # Fix the window size to 800x600

        # Initialize Serial Connection
        self.serial_port = None
        self.current_rfid = None 
        # Main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Top Section (Buttons & Pages)
        top_section = QHBoxLayout()
        
        # Sidebar layout (left-side buttons)
        sidebar = QVBoxLayout()
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.view_logs_button = QPushButton("View Logs")
        self.view_logs_button.setStyleSheet("padding: 5px; font-size: 14px; font-weight: bold;")
        self.view_logs_button.clicked.connect(self.show_logs)
        
        self.enroll_rfid_button = QPushButton("Enroll RFID")
        self.enroll_rfid_button.setStyleSheet("padding: 5px; font-size: 14px; font-weight: bold;")
        self.enroll_rfid_button.clicked.connect(self.show_enroll)

        # Sync Time Button (Initially Disabled)
        self.sync_time_button = QPushButton("Sync Time")
        self.sync_time_button.setStyleSheet("padding: 5px; font-size: 14px; font-weight: bold; background-color: gray;")
        self.sync_time_button.setEnabled(False)
        self.sync_time_button.clicked.connect(self.sync_time)
        
        sidebar.addWidget(self.view_logs_button)
        sidebar.addWidget(self.enroll_rfid_button)
        sidebar.addWidget(self.sync_time_button)
        sidebar.addStretch()

        # Serial Port Selection
        self.serial_label = QLabel("Select Serial Port:")
        self.serial_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.serial_combo = QComboBox()
        self.serial_combo.setCurrentText("Select Serial Port: ")
        self.serial_combo.setStyleSheet("padding: 5px; font-size: 14px;")
        self.populate_serial_ports()

        # Refresh Serial Ports Button
        self.refresh_serial_button = QPushButton("Refresh Ports")
        self.refresh_serial_button.setStyleSheet("padding: 5px; font-size: 14px;")
        self.refresh_serial_button.clicked.connect(self.populate_serial_ports)

        self.connect_serial_button = QPushButton("Connect")
        self.connect_serial_button.setStyleSheet("padding: 5px; font-size: 14px;")
        self.connect_serial_button.clicked.connect(self.connect_serial)

        sidebar.addWidget(self.serial_label)
        sidebar.addWidget(self.serial_combo)
        sidebar.addWidget(self.refresh_serial_button)
        sidebar.addWidget(self.connect_serial_button)

        # Stack to switch between pages
        self.stack = QStackedWidget()
        
        # Enroll RFID Page
        self.enroll_page = QWidget()
        enroll_layout = QVBoxLayout()
        
        self.enroll_instructions = QLabel("📌 How to Enroll RFID:\n1. Click 'Scan RFID'.\n2. Place the RFID sticker near the scanner.\n3. Enter the item name.\n4. Click 'Save'.")
        self.enroll_instructions.setStyleSheet("font-size: 16px; font-weight: bold;")
        enroll_layout.addWidget(self.enroll_instructions)
        
        self.scan_rfid_button = QPushButton("🔍 Scan RFID")
        self.scan_rfid_button.setStyleSheet("padding: 15px; font-size: 18px; font-weight: bold;")
        self.scan_rfid_button.clicked.connect(self.scan_rfid)
        
        self.rfid_label = QLabel("Scanned RFID: None")
        self.rfid_label.setStyleSheet("font-size: 18px; font-weight: bold; color: blue;")
        
        self.item_name_input = QLineEdit()
        self.item_name_input.setPlaceholderText("Enter item name...")
        self.item_name_input.setEnabled(False)  # Disabled until RFID is scanned
        self.item_name_input.setStyleSheet("padding: 10px; font-size: 16px;")
        
        self.save_button = QPushButton("💾 Save RFID")
        self.save_button.setStyleSheet("padding: 15px; font-size: 18px; font-weight: bold;")
        self.save_button.setEnabled(False)  # Disabled until both fields are filled
        self.save_button.clicked.connect(self.save_rfid)
        
        enroll_layout.addWidget(self.scan_rfid_button)
        enroll_layout.addWidget(self.rfid_label)
        enroll_layout.addWidget(self.item_name_input)
        enroll_layout.addWidget(self.save_button)
        enroll_layout.addStretch()
        
        self.enroll_page.setLayout(enroll_layout)

        # Logs Page
        self.logs_page = QWidget()
        logs_layout = QVBoxLayout()
        
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(4)
        self.logs_table.setHorizontalHeaderLabels(["Timestamp", "RFID #", "Item", "Action"])
        self.logs_table.setStyleSheet("font-size: 18px;")
        self.logs_table.horizontalHeader().setStyleSheet("font-size: 16px; font-weight: bold;")
        
        logs_title = QLabel("📜 Logs Table")
        logs_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logs_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        logs_layout.addWidget(logs_title)
        logs_layout.addWidget(self.logs_table)
        
        self.logs_page.setLayout(logs_layout)

        # Add pages to stack
        self.stack.addWidget(self.logs_page)
        self.stack.addWidget(self.enroll_page)

        # Add widgets to top section
        top_section.addLayout(sidebar)
        top_section.addWidget(self.stack, 1)

        # Serial Monitor (Bottom Section)
        self.serial_monitor = QTextEdit()
        self.serial_monitor.setReadOnly(True)
        self.serial_monitor.setStyleSheet("background: black; color: lime; font-family: monospace; font-size: 14px; padding: 5px;")
        self.serial_monitor.setFixedHeight(200)
        
        self.clear_serial_button = QPushButton("🧹 Clear Monitor")
        self.clear_serial_button.setStyleSheet("padding: 10px; font-size: 14px;")
        self.clear_serial_button.clicked.connect(self.serial_monitor.clear)
        
        serial_layout = QVBoxLayout()
        serial_layout.addWidget(QLabel("📡 Serial Monitor"))
        serial_layout.addWidget(self.serial_monitor)
        serial_layout.addWidget(self.clear_serial_button)
        
        # Add sections to main layout
        main_layout.addLayout(top_section)
        main_layout.addLayout(serial_layout)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Default to Logs Page
        self.show_logs()
        self.populate_logs()

        # Timer for checking serial connection
        self.serial_check_timer = QTimer(self)
        self.serial_check_timer.timeout.connect(self.check_serial_connection)
        self.serial_check_timer.start(1000)  # Check connection every 1 second

        # Timer for reading serial data
        self.serial_timer = QTimer(self)
        self.serial_timer.timeout.connect(self.read_serial)
        self.serial_timer.start(500)  # Read serial data every 500ms (adjust as needed)


    def show_enroll(self):
        self.stack.setCurrentWidget(self.enroll_page)

    def show_logs(self):
        self.stack.setCurrentWidget(self.logs_page)

    def populate_logs(self):
        self.logs_table.setRowCount(0)  # Clear table before adding new data

    def populate_serial_ports(self):
        """Fetch and list available serial ports."""
        self.serial_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.serial_combo.addItem(port.device)

    def connect_serial(self):
        port = self.serial_combo.currentText()

        # If a serial connection exists, close it first
        if self.serial_port:
            if self.serial_port.is_open:
                self.serial_port.close()
            self.serial_port = None
            self.serial_monitor.append(f"🔴 Disconnected from {port}")
            self.connect_serial_button.setText("Connect")
            self.sync_time_button.setEnabled(False)
            self.sync_time_button.setStyleSheet("padding: 5px; font-size: 14px; font-weight: bold; background-color: gray;")
            return  # Exit function after disconnecting

        # Try to establish a new connection if a valid port is selected
        if port != "No Ports Found":
            try:
                self.serial_port = serial.Serial(port, 9600, timeout=1)
                self.serial_monitor.append(f"✅ Connected to {port}")
                self.connect_serial_button.setText("Disconnect")
                self.sync_time_button.setEnabled(True)
                self.sync_time_button.setStyleSheet("padding: 5px; font-size: 14px; font-weight: bold; background-color: green;")
            except serial.SerialException as e:
                self.serial_monitor.append(f"❌ Connection Failed: {str(e)}")
                self.serial_port = None

    def check_serial_connection(self):
        """Checks if the serial device is still connected."""
        if self.serial_port:
            try:
                self.serial_port.in_waiting  # Try accessing the serial buffer
            except serial.SerialException:
                self.serial_monitor.append("⚠️ Device Disconnected!")
                self.connect_serial_button.setText("Connect")
                self.sync_time_button.setStyleSheet("padding: 5px; font-size: 14px; font-weight: bold; background-color: gray;")
                self.sync_time_button.setEnabled(False)
                self.disconnect_serial()

    def sync_time(self):
        if self.serial_port and self.serial_port.is_open:
            current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            message = f"SYNC_TIME\n{current_time}\n"
            self.serial_port.write(message.encode())
            self.serial_monitor.append(f"📤 Sent: {message.strip()}")

    def sync_time(self):
        if self.serial_port and self.serial_port.is_open:
            current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            message = f"SYNC_TIME\n{current_time}\n"
            self.serial_port.write(message.encode())
            self.serial_monitor.append(f"📤 Sent: {message.strip()}")

    def read_serial(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode().strip()
                    if data:
                        self.serial_monitor.append(f"📥 Received: {data}")
                        self.serial_monitor.verticalScrollBar().setValue(self.serial_monitor.verticalScrollBar().maximum())

                        # 🔍 Check if the message contains an RFID tag
                        if data.startswith("RFID_SCANNED:"):
                            rfid_code = data.replace("RFID_SCANNED:", "").strip()
                            self.current_rfid = rfid_code  # Store RFID
                            self.rfid_label.setText(f"Scanned RFID: {rfid_code}")  # Update UI
                            self.item_name_input.setEnabled(True)  # Enable item name input
                            self.save_button.setEnabled(True)  # Enable Save button
                        
                        # ✅ Detect "ENROLL_SUCCESSFUL" and re-enable Save Button
                        elif data == "ENROLL_SUCCESSFUL":
                            self.serial_monitor.append("✅ Enrollment Successful!")
                            self.save_button.setEnabled(True)
                            self.save_button.setText("💾 Save RFID")  # Restore original text

                        # ❌ Handle Enrollment Failure
                        elif data == "ENROLL_FAILED":
                            self.serial_monitor.append("❌ Enrollment Failed. Try Again.")
                            self.save_button.setEnabled(True)
                            self.save_button.setText("💾 Save RFID")  # Restore original text

            except serial.SerialException as e:
                self.serial_monitor.append(f"⚠️ Serial Read Error: {str(e)}")

    def read_serial_data(self):
        """Reads data from the serial port and updates the monitor."""
        try:
            if self.serial_port and self.serial_port.is_open:
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:
                    self.serial_monitor.append(f"📥 Received: {data}")
        except serial.SerialException as e:
            self.serial_monitor.append(f"⚠️ Serial Read Error: {e}")
            self.disconnect_serial()  # Close the connection properly

    def disconnect_serial(self):
        """Safely disconnects the serial port."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_monitor.append("❌ Serial Disconnected.")
            self.serial_port = None


    def scan_rfid(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_monitor.append("🔍 Scanning RFID...")
            self.serial_port.write(b"SCAN_NOW\n")  # Send command to Arduino
        else:
            self.serial_monitor.append("❌ No Serial Connection")

    def save_rfid(self):
        item_name = self.item_name_input.text().strip()
        
        if not item_name:
            self.serial_monitor.append("⚠️ Item name cannot be empty!")
            return  # Stop execution if item name is missing

        # Normalize spaces (replace multiple spaces with a single space)
        item_name = re.sub(r'\s+', ' ', item_name)

        if self.current_rfid and self.serial_port and self.serial_port.is_open:
            message = f"ENROLL\n{item_name},{self.current_rfid}\n"
            self.serial_port.write(message.encode())  # Send message
            self.serial_monitor.append(f"📤 Sent:\n{message.strip()}")

            # Disable Save Button and Change Text to "SAVING..."
            self.save_button.setEnabled(False)
            self.save_button.setText("⏳ SAVING...")

            # Reset UI inputs but keep button disabled until "ENROLL_SUCCESSFUL"
            self.item_name_input.clear()
            self.rfid_label.setText("Scanned RFID: None")
            self.current_rfid = None
            self.item_name_input.setEnabled(False)
        else:
            self.serial_monitor.append("❌ No scanned RFID or serial connection!")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RFIDApp()
    window.show()
    sys.exit(app.exec())
