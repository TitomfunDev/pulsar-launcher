# PySide6 Imports
from PySide6.QtWidgets import QApplication, QMessageBox

def show_question(name, description):
    reply = QMessageBox.question(
        None,
        name,
        description,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes
    )

    return reply == QMessageBox.StandardButton.Yes

def show_warning(name, description):
    QMessageBox.warning(
        None,
        name,
        description
    )