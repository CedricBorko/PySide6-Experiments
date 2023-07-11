from enum import IntFlag
import sys
from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout, QGridLayout
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QEnterEvent, QMouseEvent, QBrush, QPen, QPainterPath, QFontMetrics, QFont, QKeySequence
from PySide6.QtCore import Qt, QRect, QPoint, QEvent, QSize, QPropertyAnimation, QEasingCurve

from utils import load_svg, draw_svg


class Button(QPushButton):
    primary_color: QColor = QColor("#008f9b")
    secondary_color: QColor = QColor("#ffffff")
    error_color: QColor = QColor("#eb2347")

    icon_background_contrast: float = 1.15

    border_radius: tuple = 4, 4, 4, 4

    margin: int = 0
    padding_h: int = 32
    padding_v: int = 16

    def __init__(self, text: str = "", svg_name: str = None, svg_name_alternate: str = None, parent: QWidget = None) -> None:
        super().__init__(text, parent)

        self._svg = load_svg(svg_name) if svg_name is not None else None
        self._alternate_svg = load_svg(svg_name_alternate) if svg_name_alternate is not None else None

        self._hovered = False
        self._pressed = False

        self._error = False
        self._error_text = None

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Verdana", 10))
        self.setIconSize(QSize(24, 24))

        self._error_in_animation = QPropertyAnimation(self, b"geometry")
        self._error_in_animation.setDuration(250)
        self._error_in_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self._error_out_animation = QPropertyAnimation(self, b"geometry")
        self._error_out_animation.setDuration(250)
        self._error_out_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self._error_in_animation.finished.connect(self._error_out_animation.start)

        self.setMouseTracking(True)

    def hitButton(self, point: QPoint) -> bool:
        return self.rect().contains(point)

    def sizeHint(self) -> QSize:
        metrics = QFontMetrics(self.font())
        height = metrics.height() + 2 * self.padding_v
        if not self.text():
            return QSize(height, height)
        return QSize(metrics.horizontalAdvance(self.text()) + self.padding_h * 2 + height, height)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._hovered = self.rect().contains(event.position().toPoint())
        self.setCursor(Qt.CursorShape.PointingHandCursor if self.hitButton(event.position().toPoint()) else Qt.CursorShape.ArrowCursor)
        return super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered = False
        return super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._pressed = True
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._pressed = False
        return super().mouseReleaseEvent(event)

    @staticmethod
    def set_primary_color(color: QColor) -> None:
        Button.primary_color = color

    @staticmethod
    def set_secondary_color(color: QColor) -> None:
        Button.secondary_color = color

    def set_primary_color(self, color: QColor) -> None:
        self.primary_color = color
        self.update()

    def set_secondary_color(self, color: QColor) -> None:
        self.secondary_color = color
        self.update()

    def set_border_radius(self, top_left: int = 0, top_right: int = 0, bottom_right: int = 0, bottom_left: int = 0) -> None:
        self.border_radius = top_left, top_right, bottom_right, bottom_left
        self.update()

    def set_uniform_border_radius(self, radius: int) -> None:
        self.border_radius = radius, radius, radius, radius
        self.update()

    def set_error(self, error: bool, error_text: str = None) -> None:
        self._error = error
        if self._error:
            if (
                self._error_in_animation.state() != QPropertyAnimation.State.Running
                and self._error_out_animation.state() != QPropertyAnimation.State.Running
            ):
                self._error_in_animation.setStartValue(self.geometry())
                self._error_in_animation.setEndValue(QRect(self.x() - 4, self.y() - 4, self.width() + 8, self.height() + 8))
                self._error_in_animation.start()

                self._error_out_animation.setStartValue(QRect(self.x() - 4, self.y() - 4, self.width() + 8, self.height() + 8))
                self._error_out_animation.setEndValue(self.geometry())
        if error_text is not None:
            self._error_text = error_text
        self.update()

    def set_svg(self, svg_name: str, alternate: bool = False) -> None:
        if alternate:
            self._alternate_svg = load_svg(svg_name)
        else:
            self._svg = load_svg(svg_name)

        self.update()

    def __get_primary_color(self) -> QColor:
        base_color = self.primary_color if not self._error else self.error_color

        if not self.isEnabled():
            return base_color.darker(250)
        if self._pressed:
            return base_color.lighter(110)
        if self._hovered:
            return base_color.darker(120)
        if self.isChecked():
            return base_color.lighter(115)

        return base_color

    def __get_secondary_color(self) -> QColor:
        if not self.isEnabled():
            return self.secondary_color.darker(150)
        if self.isChecked():
            return self.secondary_color.lighter(120)

        return self.secondary_color

    def rect(self) -> QRect:
        if not self.text():
            return QRect(
                0,
                0,
                self.height(),
                self.height(),
            )
        return QRect(
            0,
            0,
            self.width(),
            self.height(),
        )

    def __rect_path(self) -> QPainterPath:
        path = QPainterPath()

        if not any(self.border_radius):
            path.addRect(self.rect())
            return path

        border_radii = self.border_radius
        size_limiter = min(self.height() // 2, self.width() // 2)

        def draw_arc(x: int, y: int, radius: int, start_angle: int) -> None:
            path.arcTo(QRect(x, y, min(radius, size_limiter), min(radius, size_limiter)), start_angle, -90)

        def draw_line(x: int, y: int, offset_x: int, offset_y: int) -> None:
            path.lineTo(QPoint(x - min(offset_x, size_limiter), y - min(offset_y, size_limiter)))

        left = self.rect().left()
        right = self.rect().right()
        top = self.rect().top()
        bottom = self.rect().bottom()

        path.moveTo(self.rect().topLeft())
        draw_arc(0, 0, border_radii[0], 180)
        draw_line(right, top, border_radii[1] * 2, 0)
        draw_arc(right - min(border_radii[1], size_limiter), top, border_radii[1], 90)
        draw_line(right, bottom, 0, min(border_radii[2] * 2, size_limiter))
        draw_arc(right - min(border_radii[2], size_limiter), bottom - min(border_radii[2], size_limiter), border_radii[2], 0)
        draw_line(left, bottom, min(border_radii[3] * 2, size_limiter), 0)
        draw_arc(left, bottom - min(border_radii[3], size_limiter), border_radii[3], 270)

        return path

    def __svg_rect_path(self) -> QPainterPath:
        path = QPainterPath()

        if not any(self.border_radius):
            path.addRect(self.__svg_rect())
            return path

        border_radii = self.border_radius
        size_limiter = min(self.height() // 2, self.width() // 2)

        def draw_arc(x: int, y: int, radius: int, start_angle: int) -> None:
            path.arcTo(QRect(x, y, min(radius, size_limiter), min(radius, size_limiter)), start_angle, -90)

        def draw_line(x: int, y: int, offset_x: int, offset_y: int) -> None:
            path.lineTo(QPoint(x - min(offset_x, size_limiter), y - min(offset_y, size_limiter)))

        left = self.__svg_rect().left()
        right = self.__svg_rect().right()
        top = self.__svg_rect().top()
        bottom = self.__svg_rect().bottom()

        path.moveTo(self.__svg_rect().topLeft())
        draw_arc(0, 0, border_radii[0], 180)
        draw_line(right, top, border_radii[1] * 2, 0)
        draw_arc(right - min(border_radii[1], size_limiter), top, border_radii[1], 90)
        draw_line(right, bottom, 0, min(border_radii[2] * 2, size_limiter))
        draw_arc(right - min(border_radii[2], size_limiter), bottom - min(border_radii[2], size_limiter), border_radii[2], 0)
        draw_line(left, bottom, min(border_radii[3] * 2, size_limiter), 0)
        draw_arc(left, bottom - min(border_radii[3], size_limiter), border_radii[3], 270)

        return path

    def __svg_rect(self) -> QRect:
        if not self._svg:
            return QRect(0, 0, 0, 0)

        size = self.height()
        if self.layoutDirection() == Qt.LayoutDirection.LeftToRight:
            return QRect(0, 0, size, size)
        return QRect(self.rect().right() - size, 0, size, size)

    def __text_rect(self) -> QRect:
        if self.layoutDirection() == Qt.LayoutDirection.LeftToRight:
            return QRect(
                self.__svg_rect().right(),
                0,
                self.rect().width() - self.__svg_rect().width(),
                self.height(),
            )

        return QRect(0, 0, self.rect().width() - self.__svg_rect().width(), self.height())

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        background_path = self.__rect_path()
        svg_rect_path = self.__svg_rect_path()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.__get_primary_color()))

        painter.drawPath(background_path)

        painter.setPen(Qt.PenStyle.NoPen)

        if self._svg:
            painter.setBrush(QBrush(self.__get_primary_color().darker(self.icon_background_contrast * 100)))
            painter.drawPath(svg_rect_path)

        if self.text():
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        painter.setPen(QPen(self.__get_secondary_color()))
        painter.setFont(self.font())
        painter.drawText(
            self.__text_rect(), Qt.AlignmentFlag.AlignCenter, self.text() if (not self._error or self._error_text is None) else self._error_text
        )

        painter.setBrush(Qt.BrushStyle.NoBrush)

        if self._error:
            draw_svg(painter, load_svg("alert-octagon"), self.iconSize(), self.__svg_rect(), self.__get_secondary_color())

        elif self._svg and not self.isChecked() or not self._alternate_svg:
            draw_svg(painter, self._svg, self.iconSize(), self.__svg_rect(), self.__get_secondary_color())

        elif self._alternate_svg and self.isChecked():
            draw_svg(painter, self._alternate_svg, self.iconSize(), self.__svg_rect(), self.__get_secondary_color())


def main():
    app = QApplication(sys.argv)
    w = QWidget()
    w.setLayout(QGridLayout())
    w.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

    b1 = Button("Zoom in", "zoom-in")
    b1.primary_color = QColor("#34495e")
    b1.clicked.connect(lambda: print("B1"))

    b2 = Button("Zoom out", "zoom-out")
    b2.primary_color = QColor("#34495e")
    b1.setShortcut(QKeySequence())

    b3 = Button("Test", "zap")
    b3.primary_color = QColor("#f26957")

    b4 = Button("Test", "briefcase")
    b4.primary_color = QColor("#3265d1")

    b5 = Button("Test")
    b6 = Button("Test", "chevron-down")
    b6.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    b7 = Button("Datei auswählen", "file-csv")
    b7.primary_color = QColor("#af51cf")
    b4.clicked.connect(lambda: b7.set_error(not b7._error, "Falscher Dateityp!"))

    b8 = Button("Test", "volume")
    b8.setCheckable(True)
    b8.set_svg("volume-x", True)

    w.layout().addWidget(b1, 0, 0)
    w.layout().addWidget(b2, 0, 1)
    w.layout().addWidget(b3, 1, 0)
    w.layout().addWidget(b4, 1, 1)
    w.layout().addWidget(b5, 2, 0)
    w.layout().addWidget(b6, 2, 1)
    w.layout().addWidget(b7, 3, 0)
    w.layout().addWidget(b8, 3, 1)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
