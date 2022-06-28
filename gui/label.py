"""
File with class for label widget. Text in label is attached to content of another widget.
"""

from typing import Optional
import PyQt5.QtWidgets as qt
from PyQt5.QtCore import pyqtSlot


class Label(qt.QLabel):
    """
    Class for label widget. Text in label is attached to content of another widget.
    """

    def __init__(self, default_text: Optional[str] = "", format_for_text: Optional[str] = ""):
        """
        :param default_text: default text;
        :param format_for_text: format to show text in label.
        """

        super().__init__()
        self._default_text: str = default_text
        self._format: str = format_for_text
        self.setText(self._default_text)

    def set_default_text(self, default_text: str):
        """
        Method sets default text to label.
        :param default_text: default text.
        """

        self._default_text = default_text

    def set_format(self, format_for_text: str):
        """
        Method sets format to show text in label.
        :param format_for_text: format.
        """

        self._format = format_for_text

    @pyqtSlot(str)
    def update_text(self, text: str):
        """
        Method updates text in label.
        :param text: new text for label.
        """

        if not text:
            self.setText(self._default_text)
        else:
            self.setText(self._format.format(text))

    @pyqtSlot(int)
    def update_value(self, value: int):
        """
        Method updates text in label.
        :param value: new value for label.
        """

        if not isinstance(value, int):
            self.setText(self._default_text)
        else:
            self.setText(self._format.format(value))
