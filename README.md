# RFID Management System

A Python-based GUI application for managing RFID tags, built with PyQt6 and pyserial.

## Prerequisites

- Python 3.13 or higher
- pip (Python package installer)

## Installation Steps

1. **Clone or download this repository**

2. **Install required dependencies**
   Open Command Prompt (cmd) and run the following commands:

   ```bash
   pip install pyserial
   pip install PyQt6
   pip install pyinstaller
   ```

3. **Run the application**

   You can run the application in two ways:

   a. **Run directly with Python:**
   ```bash
   python main.py
   ```

   b. **Create and run executable:**
   ```bash
   pyinstaller --noconsole --onefile --name "RFID Management System" main.py
   ```
   The executable will be created in the `dist` folder.

## Features

- RFID tag scanning and enrollment
- Serial port connection management
- Log viewing and management
- Time synchronization with RFID device
- Log synchronization with RFID device
- Real-time serial monitor

## Usage

1. Launch the application
2. Select your serial port from the dropdown menu
3. Click "Connect" to establish connection with the RFID device
4. Use the "Enroll RFID" button to scan and register new RFID tags
5. Use the "View Logs" button to see the history of RFID scans
6. Use "Sync Time" to synchronize the device's time
7. Use "Sync Logs" to retrieve logs from the device

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed correctly
2. Check if your serial port is properly connected
3. Verify that the correct serial port is selected
4. Ensure the RFID device is powered on and functioning

## File Structure

- `main.py` - Main application file
- `data.txt` - Log file (created automatically)
- `.gitignore` - Git ignore file

## Dependencies

- pyserial: For serial communication
- PyQt6: For the graphical user interface
- pyinstaller: For creating executable files (optional)

## License

This project is open source and available under the MIT License. 