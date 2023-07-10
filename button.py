from enum import IntFlag
import sys
from PySide6.QtWidgets import QApplication, QPushButton, QLabel, QWidget, QStyle, QVBoxLayout
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QEnterEvent, QMouseEvent, QBrush, QPen, QPainterPath, QFontMetrics, QFont
from PySide6.QtCore import Qt, QRect, QPoint, QEvent, QSize

from utils import load_svg, draw_svg


class Button(QPushButton):
    primary_color: QColor = QColor("#008f9b")
    secondary_color: QColor = QColor("#ffffff")
    icon_background_darkness: int = 150

    border_width: int = 0
    border_radius: tuple = 0, 0, 0, 0

    margin: int = 8
    padding: int = 24

    def __init__(self, text: str, svg_name: str, parent: QWidget = None) -> None:
        super().__init__(text, parent)

        self._svg = load_svg(svg_name)

        self._hovered = False
        self._pressed = False

        self._border_radius_percentage = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Verdana", 9, QFont.Weight.Bold))
        self.setIconSize(QSize(24, 24))

    def sizeHint(self) -> QSize:
        metrics = QFontMetrics(self.font())
        height = metrics.height() + 2 * self.padding
        return QSize(metrics.horizontalAdvance(self.text()) + self.padding * 2 + height, height)

    def set_border_radius_percentage(self, use_percentage: bool) -> None:
        self._border_radius_percentage = use_percentage
        self.update()

    def enterEvent(self, event: QEnterEvent) -> None:
        self._hovered = True
        return super().enterEvent(event)

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

    def set_border_width(self, width: int) -> None:
        self.border_width = max(0, width)
        self.update()

    def set_border_radius(self, top_left: int = 0, top_right: int = 0, bottom_right: int = 0, bottom_left: int = 0) -> None:
        self.border_radius = top_left, top_right, bottom_right, bottom_left
        self.update()

    def set_equal_border_radius(self, radius: int) -> None:
        self.border_radius = radius, radius, radius, radius
        self.update()

    def __get_primary_color(self) -> QColor:
        if not self.isEnabled():
            return self.primary_color.darker(250)
        if self._pressed:
            return self.primary_color.lighter(110)
        if self._hovered:
            return self.primary_color.darker(120)
        if self.isChecked():
            return self.primary_color.lighter(105)

        return self.primary_color

    def __get_secondary_color(self) -> QColor:
        if not self.isEnabled():
            return self.secondary_color.darker(150)
        if self.isChecked():
            return self.secondary_color.lighter(120)

        return self.secondary_color

    def rect(self) -> QRect:
        return QRect(
            self.margin,
            self.margin,
            self.width() - self.margin * 2,
            self.height() - self.margin * 2,
        )

    def __rect_path(self) -> QPainterPath:
        path = QPainterPath()

        if not any(self.border_radius):
            path.addRect(self.rect())
            return path

        border_radius = self.border_radius
        if self._border_radius_percentage:
            border_radius = tuple(map(lambda br: br / 100 * self.height(), border_radius))

        # Top Left
        path.moveTo(self.rect().topLeft())

        path.arcTo(
            QRect(
                self.margin,
                self.margin,
                min(border_radius[0], min(self.height() // 2, self.width() // 2)),
                min(border_radius[0], min(self.height() // 2, self.width() // 2)),
            ),
            180,
            -90,
        )

        # Top
        path.lineTo(
            QPoint(
                self.rect().right() - min(border_radius[1] * 2, min(self.height() // 2, self.width() // 2)),
                self.rect().top(),
            )
        )

        # Top Right
        path.arcTo(
            QRect(
                self.rect().right() - min(border_radius[1], min(self.height() // 2, self.width() // 2)),
                self.rect().top(),
                min(border_radius[1], min(self.height() // 2, self.width() // 2)),
                min(border_radius[1], min(self.height() // 2, self.width() // 2)),
            ),
            90,
            -90,
        )

        # Right
        path.lineTo(QPoint(self.rect().right(), self.rect().bottom() - min(border_radius[2] * 2, min(self.height() // 2, self.width() // 2))))

        # Bottom Right
        path.arcTo(
            QRect(
                self.rect().right() - min(border_radius[2], min(self.height() // 2, self.width() // 2)),
                self.rect().bottom() - min(border_radius[2], min(self.height() // 2, self.width() // 2)),
                min(border_radius[2], min(self.height() // 2, self.width() // 2)),
                min(border_radius[2], min(self.height() // 2, self.width() // 2)),
            ),
            0,
            -90,
        )

        # Bottom
        path.lineTo(
            QPoint(
                self.rect().left() + min(border_radius[3], min(self.height() // 2, self.width() // 2)),
                self.rect().bottom(),
            )
        )

        path.arcTo(
            QRect(
                self.rect().left(),
                self.rect().bottom() - min(border_radius[3], min(self.height() // 2, self.width() // 2)),
                min(border_radius[3], min(self.height() // 2, self.width() // 2)),
                min(border_radius[3], min(self.height() // 2, self.width() // 2)),
            ),
            270,
            -90,
        )

        return path

    def __svg_rect_path(self) -> QPainterPath:
        path = QPainterPath()

        if not any(self.border_radius):
            path.addRect(self.__svg_rect())
            return path

        border_radius = self.border_radius
        if self._border_radius_percentage:
            border_radius = tuple(map(lambda br: br / 100 * self.height(), border_radius))

        # Top Left
        path.moveTo(self.rect().topLeft())

        path.arcTo(
            QRect(
                self.margin,
                self.margin,
                min(border_radius[0], min(self.height() // 2, self.width() // 2)),
                min(border_radius[0], min(self.height() // 2, self.width() // 2)),
            ),
            180,
            -90,
        )

        # Top
        path.lineTo(
            QPoint(
                self.__svg_rect().right() - min(border_radius[1] * 2, min(self.height() // 2, self.width() // 2)),
                self.__svg_rect().top(),
            )
        )

        # Top Right
        path.arcTo(
            QRect(
                self.__svg_rect().right() - min(border_radius[1], min(self.height() // 2, self.width() // 2)),
                self.__svg_rect().top(),
                min(border_radius[1], min(self.height() // 2, self.width() // 2)),
                min(border_radius[1], min(self.height() // 2, self.width() // 2)),
            ),
            90,
            -90,
        )

        # Right
        path.lineTo(
            QPoint(self.__svg_rect().right(), self.__svg_rect().bottom() - min(border_radius[2] * 2, min(self.height() // 2, self.width() // 2)))
        )

        # Bottom Right
        path.arcTo(
            QRect(
                self.__svg_rect().right() - min(border_radius[2], min(self.height() // 2, self.width() // 2)),
                self.__svg_rect().bottom() - min(border_radius[2], min(self.height() // 2, self.width() // 2)),
                min(border_radius[2], min(self.height() // 2, self.width() // 2)),
                min(border_radius[2], min(self.height() // 2, self.width() // 2)),
            ),
            0,
            -90,
        )

        # Bottom
        path.lineTo(
            QPoint(
                self.__svg_rect().left() + min(border_radius[3], min(self.height() // 2, self.width() // 2)),
                self.__svg_rect().bottom(),
            )
        )

        path.arcTo(
            QRect(
                self.__svg_rect().left(),
                self.__svg_rect().bottom() - min(border_radius[3], min(self.height() // 2, self.width() // 2)),
                min(border_radius[3], min(self.height() // 2, self.width() // 2)),
                min(border_radius[3], min(self.height() // 2, self.width() // 2)),
            ),
            270,
            -90,
        )

        return path

    def __svg_rect(self) -> QRect:
        if not self._svg:
            return QRect(self.margin, self.margin, 0, 0)
        return QRect(self.margin, self.margin, self.height() - self.margin * 2, self.height() - self.margin * 2)

    def __text_rect(self) -> QRect:
        return QRect(self.__svg_rect().right(), self.margin, self.width() - (self.margin + self.padding) * 2, self.height() - self.margin * 2)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.border_width == 0:
            painter.setPen(Qt.PenStyle.NoPen)

        background_path = self.__rect_path()
        svg_rect_path = self.__svg_rect_path()

        painter.setBrush(QBrush(self.__get_primary_color()))
        painter.drawPath(background_path)
        painter.setBrush(QBrush(self.__get_primary_color().darker(self.icon_background_darkness)))
        painter.drawPath(svg_rect_path)

        if self.text():
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        painter.setPen(QPen(self.__get_secondary_color()))
        painter.setFont(self.font())
        painter.drawText(self.__text_rect(), Qt.AlignmentFlag.AlignCenter, self.text())

        painter.setBrush(Qt.BrushStyle.NoBrush)

        if self._svg:
            draw_svg(painter, self._svg, self.iconSize(), self.__svg_rect(), self.__get_secondary_color())


def main():
    app = QApplication(sys.argv)
    w = QWidget()
    w.setLayout(QVBoxLayout())
    Button.primary_color = QColor("#34495e")
    b1 = Button("Test", "zoom-in")
    w.layout().addWidget(b1)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()