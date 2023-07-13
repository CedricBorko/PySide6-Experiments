from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QHBoxLayout
from PySide6.QtCore import Qt, QPoint, QRect, QSize, Signal
from PySide6.QtGui import QColor, QGuiApplication, QBrush, QPainter, QPaintEvent, QFontMetrics, QFont, QMouseEvent, QWheelEvent, QResizeEvent

from button import Button


class Slider(QWidget):
    primary_color: QColor = QColor("#008f9b")
    secondary_color: QColor = QColor("#d3d3d3")
    text_color: QColor = QColor("#3d3d3d")

    padding_h: int = 16
    padding_v: int = 8
    gap: int = 2

    value_changed = Signal(float)
    slider_pressed = Signal()
    slider_moved = Signal()
    slider_released = Signal()

    track_height: int = 8
    thumb_radius: int = 8

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._orientation = orientation
        self._show_text = True
        self._show_range = True

        self._minimum, self._maximum = 0, 100
        self._value = 50
        self._step = 1

        self.setMouseTracking(True)

        self._hovered = False
        self._pressed = False

        self._suffix = ""

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

    def contains(self, value: float) -> bool:
        return self._minimum <= value <= self._maximum

    def range(self) -> tuple[float, float]:
        return self._minimum, self._maximum

    def set_range(self, minimum: float, maximum: float) -> None:
        self.set_minimum(minimum)
        self.set_maximum(maximum)

    def extent(self) -> float:
        return self.maximum() - self.minimum()

    def suffix(self) -> str:
        return self._suffix

    def set_suffix(self, suffix: str) -> None:
        self._suffix = suffix
        self.update()

    def minimum(self) -> float:
        return self._minimum

    def set_minimum(self, minimum: float) -> None:
        if minimum > self._maximum:
            self._maximum = minimum + self._step
        self._minimum = minimum
        if not self.contains(self._value):
            self.set_value(minimum)

        self.update()

    def maximum(self) -> float:
        return self._maximum

    def set_maximum(self, maximum: float) -> None:
        if maximum < self._minimum:
            self._minimum = maximum - self._step
        self._maximum = maximum
        if not self.contains(self._value):
            self.set_value(maximum)

        self.update()

    def decimals(self) -> int:
        return max(str(self._step)[::-1].find("."), 0)

    def __text(self) -> str:
        if self.decimals() == 0:
            return str(int(self._value))
        return str(round(self._value, self.decimals()))

    def __text_minimum(self) -> str:
        if self.decimals() == 0:
            return str(int(self._minimum))
        return str(round(self._minimum, self.decimals()))

    def __text_maximum(self) -> str:
        if self.decimals() == 0:
            return str(int(self._maximum))
        return str(round(self._maximum, self.decimals()))

    def value(self) -> float:
        return self._value

    def set_value(self, value: float) -> None:
        if not self.contains(value):
            return
        new_value = self._step * round(value / self._step)
        if new_value == self._value:
            return
        self._value = new_value
        self.value_changed.emit(self._value)
        self.update()

    def step(self) -> float:
        return self._step

    def set_step(self, step: float) -> None:
        if step <= 0:
            return
        if step > abs(self._maximum - self._minimum):
            return
        self._step = step
        self.update()

    def set_text_visible(self, visible: bool) -> None:
        self._show_text = visible
        self.update()

    def set_range_text_visible(self, visible: bool) -> None:
        self._show_range = visible
        self.update()

    def set_orientation(self, orientation: Qt.Orientation) -> None:
        self._orientation = orientation
        self.update()

    def sizeHint(self) -> QSize:
        width, height = self.get_text_metrics(self.__text())

        if self._show_range:
            height *= 2
        if self._orientation == Qt.Orientation.Horizontal:
            return QSize(
                max(self.padding_h, self.thumb_radius) * 2 + width,
                height + self.padding_v * 2 + max(self.track_height, self.thumb_radius * 2) + self.spacing(),
            )

    def spacing(self) -> float:
        return max(int(self._show_text) * self.gap, self.thumb_radius)

    def get_text_metrics(self, text: str) -> QSize:
        metrics = QFontMetrics(self.font())
        return metrics.horizontalAdvance(text + self.suffix()), metrics.height()

    def __minimum_text_rect(self) -> QRect:
        if not self._show_range:
            return QRect(0, 0, 0, 0)
        width, height = self.get_text_metrics(self.__text_minimum())
        if self._orientation == Qt.Orientation.Horizontal:
            return QRect(self.padding_h, self.__track_rect().bottom() + self.spacing(), width, height)

    def __maximum_text_rect(self) -> QRect:
        if not self._show_range:
            return QRect(0, 0, 0, 0)
        width, height = self.get_text_metrics(self.__text_maximum())
        if self._orientation == Qt.Orientation.Horizontal:
            return QRect(self.__track_rect().right() - width, self.__track_rect().bottom() + self.spacing(), width, height)

    def __text_rect(self) -> QRect:
        if not self._show_text:
            return QRect(0, 0, 0, 0)

        width, height = self.get_text_metrics(self.__text())
        x = max(self.padding_h, self.thumb_radius) + (self.value() - self.minimum()) / self.extent() * (
            self.width() - max(self.padding_h, self.thumb_radius) * 2
        )
        x -= width // 2
        if self._orientation == Qt.Orientation.Horizontal:
            return QRect(x, self.padding_v, width, height)

    def __track_rect(self) -> QRect:
        if self._orientation == Qt.Orientation.Horizontal:
            return QRect(
                max(self.padding_h, self.thumb_radius),
                self.__text_rect().bottom() + self.spacing(),
                self.width() - max(self.padding_h, self.thumb_radius) * 2,
                self.track_height,
            )

    def __track_rect_highlighted(self) -> QRect:
        if self._orientation == Qt.Orientation.Horizontal:
            return QRect(self.padding_h, self.__text_rect().bottom() + self.spacing(), self.__thumb_rect().left(), self.track_height)

    def __thumb_rect(self) -> QRect:
        track = self.__track_rect()
        thumb_x = track.left() + (self.value() - self.minimum()) / self.extent() * track.width() - self.thumb_radius
        return QRect(thumb_x, track.center().y() - self.thumb_radius, self.thumb_radius * 2, self.thumb_radius * 2)

    def __get_primary_color(self) -> QColor:
        base_color = self.primary_color

        if not self.isEnabled():
            return base_color.darker(250)
        if self._pressed:
            return base_color.lighter(110)
        if self._hovered:
            return base_color.darker(120)

        return base_color

    def __get_secondary_color(self, highlighted: bool = False) -> QColor:
        if highlighted:
            return self.primary_color
        return self.secondary_color

    def __transform_position_to_value(self, point: QPoint) -> float:
        x = (point.x() - self.__track_rect().left()) / self.__track_rect().width()
        return self.minimum() + x * self.extent()

    def mouse_over_handle(self, point: QPoint) -> bool:
        cx, cy = self.__thumb_rect().center().toTuple()
        x, y = point.toTuple()

        return (x - cx) ** 2 + (y - cy) ** 2 <= self.thumb_radius * self.thumb_radius

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._hovered = self.mouse_over_handle(event.position().toPoint())
        self.update()

        if self._pressed:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.set_value(self.__transform_position_to_value(event.position()))
        elif self._hovered:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        return super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.mouse_over_handle(event.position().toPoint()) and event.buttons() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif self.__track_rect().contains(event.position().toPoint()):
            self.set_value(self.__transform_position_to_value(event.position().toPoint()))

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._pressed = False
        self.setCursor(Qt.CursorShape.PointingHandCursor if self._hovered else Qt.CursorShape.ArrowCursor)
        return super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = self._step

        modifiers = QGuiApplication.queryKeyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            delta = 10
        if modifiers == Qt.ControlModifier:
            delta = 100

        if event.angleDelta().y() < 0:
            self.set_value(self.value() - delta)
        elif event.angleDelta().y() > 0:
            self.set_value(self.value() + delta)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.update()
        self.setMinimumSize(self.sizeHint())
        return super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(self.text_color)
        painter.setFont(self.font())
        painter.drawText(self.__text_rect(), Qt.AlignmentFlag.AlignCenter, self.__text() + self.suffix())

        if self._show_range:
            painter.setPen(self.text_color.lighter(200))

            painter.drawText(self.__minimum_text_rect(), Qt.AlignmentFlag.AlignCenter, self.__text_minimum() + self.suffix())
            painter.drawText(self.__maximum_text_rect(), Qt.AlignmentFlag.AlignCenter, self.__text_maximum() + self.suffix())

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(self.__get_secondary_color()))
        painter.drawRoundedRect(self.__track_rect(), self.track_height // 2, self.track_height // 2)

        painter.setBrush(QBrush(self.__get_secondary_color(highlighted=True)))
        painter.drawRoundedRect(self.__track_rect_highlighted(), self.track_height // 2, self.track_height // 2)

        painter.setBrush(QBrush(self.__get_primary_color()))
        painter.drawEllipse(self.__thumb_rect())

        return super().paintEvent(event)
    

import sys
from PySide6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    w = QWidget()
    w.setLayout(QVBoxLayout())
    b = Button(svg_name="volume-x", svg_name_alternate="volume")
    b.setChecked(True)
    b.set_uniform_border_radius(200)

    s0 = Slider()
    s0.set_suffix("%")
    s0.set_range_text_visible(False)

    h = QHBoxLayout()
    h.setAlignment(Qt.AlignmentFlag.AlignLeft)

    h.addWidget(b)
    h.addWidget(s0)

    def on_volume_changed(volume: int) -> None:
        b.setChecked(volume != 0)

    def on_button_clicked(checked: bool) -> None:
        if not checked:
            b.stored_volume = s0.value()
            s0.set_value(0)
        else:
            s0.set_value(b.stored_volume if hasattr(b, "stored_volume") else s0.extent() // 2)
        b.update()

    s0.value_changed.connect(on_volume_changed)
    b.clicked.connect(on_button_clicked)

    w.layout().addLayout(h)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
