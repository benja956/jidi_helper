import sys
from PyQt6.QtWidgets import QApplication
from src.gui import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 