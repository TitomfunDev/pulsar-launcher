# Pulsar Dependencies
from core import game, auth

# UI Dependencies
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

try:
    from version import INTERNAL_TAG
except ImportError:
    INTERNAL_TAG = "v0.0.0-dev"

class GameLauncherWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, version_name):
        super().__init__()
        self.version_name = version_name

    def run(self):
        try:
            game.launch(self.version_name)
            self.finished.emit(True, "Game launched!")
        except Exception as e:
            self.finished.emit(False, f"Launching Error : {str(e)}")


class MainLauncherWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pulsar Launcher - ALPHA UI")
        self.resize(800, 500)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.title_label = QLabel("Pulsar Launcher")
        self.title_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #89b4fa;"
        )
        layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        self.status_label = QLabel("Prêt à lancer le jeu")
        self.status_label.setStyleSheet("font-size: 14px; color: #a6adc8;")
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        self.play_btn = QPushButton("JOUER")
        self.play_btn.setFixedSize(220, 55)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #11111b;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #94e2d5;
            }
            QPushButton:pressed {
                background-color: #89dceb;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #7f849c;
            }
        """)
        self.logout_btn = QPushButton("LOGOUT")
        self.logout_btn.setFixedSize(100, 30)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FF4747;
            }
            QPushButton:pressed {
                background-color: #750101;
            }
            QPushButton:disabled {
                background-color: #157A12;
                color: #FFFFFF;
            }
        """)

        self.play_btn.clicked.connect(self.on_play_clicked)
        layout.addWidget(self.play_btn, alignment=Qt.AlignCenter)

        self.logout_btn.clicked.connect(self.on_logout_clicked)
        layout.addWidget(self.logout_btn, alignment=Qt.AlignCenter)

        self.launcher_thread = None

        self.version_label = QLabel("Current version : " + INTERNAL_TAG)
        self.version_label.setStyleSheet("font-size: 14px; color: #a6adc8;")
        layout.addWidget(self.version_label, alignment=Qt.AlignCenter)

    def on_play_clicked(self):
        self.play_btn.setEnabled(False)
        self.logout_btn.setEnabled(False)
        self.status_label.setText("Lancement en cours...")

        self.launcher_thread = GameLauncherWorker("build-a-village-2026-halloween")
        self.launcher_thread.finished.connect(self.on_launch_finished)
        self.launcher_thread.start()

    def on_launch_finished(self, success, message):
        self.status_label.setText(message)

        self.play_btn.setEnabled(True)
        self.logout_btn.setEnabled(True)


    def on_logout_clicked(self):
        self.logout_btn.setEnabled(False)
        self.status_label.setText("Disconnected. Please restart the Launcher")
        auth.logout()