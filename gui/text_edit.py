"""
File with class for text edit widget to display logs of calculation.
"""

from datetime import datetime
import PyQt5.QtWidgets as qt


class TextEdit(qt.QTextEdit):
    """
    Class for text edit widget to display logs.
    """

    def __init__(self):
        super().__init__()

    def append(self, text: str):
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        super().append(f"{log_time} - {text}")
