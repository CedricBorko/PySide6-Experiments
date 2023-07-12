from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QLabel, QHBoxLayout, QDoubleSpinBox, QSpinBox
from PySide6.QtGui import QPainter, QPaintEvent, QColor
from PySide6.QtCore import Qt


class TextInput(QWidget):
    def __init__(self, label: str, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.v_layout = QVBoxLayout()
        self.v_layout.setSpacing(4)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.h_layout = QHBoxLayout()
        self.h_layout.setSpacing(4)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.label = QLabel(label)
        self.input = QLineEdit()

        self.set_vertical()

    def set_vertical(self) -> None:
        while self.v_layout.count():
            self.v_layout.takeAt(0)

        self._layout.takeAt(0)
        self._layout.addLayout(self.v_layout)

        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.input)

    def set_horizontal(self) -> None:
        while self.v_layout.count():
            self.v_layout.takeAt(0)

        self._layout.addLayout(self.h_layout)

        self.h_layout.addWidget(self.label)
        self.h_layout.addWidget(self.input)


class NumberInput(QWidget):
    def __init__(self, label: str, floating_point: bool = False, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.v_layout = QVBoxLayout()
        self.v_layout.setSpacing(4)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.h_layout = QHBoxLayout()
        self.h_layout.setSpacing(4)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.label = QLabel(label)
        self.input_float = QDoubleSpinBox()
        self.input = QSpinBox()

        self.set_floating_point(floating_point)
        self.set_vertical()

    def set_range(self, low: float, high: float) -> None:
        self.input.setRange(low, high)
        self.input_float.setRange(low, high)

    def set_value(self, value: float) -> None:
        self.input.setValue(value)
        self.input_float.setValue(value)

    def set_floating_point(self, floating_point: bool) -> None:
        self.input.setVisible(not floating_point)
        self.input_float.setVisible(floating_point)

    def set_vertical(self) -> None:
        while self.v_layout.count():
            self.v_layout.takeAt(0)

        self._layout.takeAt(0)
        self._layout.addLayout(self.v_layout)

        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.input)

    def set_horizontal(self) -> None:
        while self.v_layout.count():
            self.v_layout.takeAt(0)

        self._layout.addLayout(self.h_layout)

        self.h_layout.addWidget(self.label)
        self.h_layout.addWidget(self.input)


import sys
from PySide6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    w = QWidget()
    w.setLayout(QVBoxLayout())
    ti = TextInput("Vorname")
    ni = NumberInput("Linienstärke")
    w.layout().addWidget(ti)
    w.layout().addWidget(ni)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
