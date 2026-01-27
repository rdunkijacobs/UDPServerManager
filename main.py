import sys
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.ui.gui import MainWindow

def load_servers():
    try:
        with open("data/servers.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading servers.json: {e}")
        return {"xiTechnology": [], "ANZA": [], "DNS": []}

def make_status_icon(color):
    from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 12, 12)
    painter.end()
    return QIcon(pixmap)

if __name__ == "__main__":
    try:
        print("Starting application...")
        app = QApplication(sys.argv)
        servers_by_location = load_servers()
        status_icons = {
            "green": make_status_icon("green"),
            "yellow": make_status_icon("yellow"),
            "red": make_status_icon("red")
        }
        window = MainWindow(servers_by_location, status_icons)
        window.show()
        window.resize(800, 500)
        print("Window shown. Entering event loop...")
        result = app.exec()
        print(f"Event loop exited with code: {result}")
        sys.exit(result)
    except Exception as e:
        import traceback
        print("Exception occurred:", e)
        traceback.print_exc()
    # (Removed legacy/duplicate code)
