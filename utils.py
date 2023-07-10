import pathlib
from PySide6.QtGui import QIcon, QPainter, QColor
from PySide6.QtCore import Qt, QRect, QPoint, QSize

ICONS_FOLDER = pathlib.Path(__file__).parent.joinpath("icons")


def load_svg(svg_name: str) -> QIcon:
    return QIcon(str(ICONS_FOLDER.joinpath(f"{svg_name}.svg")))


def draw_svg(painter: QPainter, svg: QIcon, size: QSize, rect: QRect, color: str):
    """Draws a svg image on the widget.

    Args:
        painter (QPainter): The painter used to draw.
        svg     (QIcon)   : Svg to draw.
        size    (QSize)   : Desired image size.
        rect    (QRect)   : Rectangle to draw in.
        color   (str)     : Color of the svg.
    """
    if size == QSize(0, 0) or not svg:
        return
    
    pixmap = svg.pixmap(size)

    i_paint = QPainter(pixmap)
    i_paint.setCompositionMode(QPainter.CompositionMode_SourceIn)
    i_paint.fillRect(pixmap.rect(), color)

    svg_top_left_corner = QPoint(rect.center().x() - size.width() / 2, rect.center().y() - size.height() / 2)
    painter.drawPixmap(svg_top_left_corner, pixmap)

    del i_paint
    del pixmap
