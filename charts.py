import PySide6
from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt, QSize, QPoint, QRect
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QMouseEvent, QPainterPath, QPen, QBrush, QResizeEvent

from math import sin, cos, pi, degrees, radians

class PieChart(QGraphicsView):

    padding: int = 16

    def __init__(self, values: list[float], labels: list[str] = None, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._values = values
        self._labels = labels if labels is not None else []

    
        self._scene = QGraphicsScene()

        self._start_angle = pi / 2
        self._inner_radius_percent = 0.7
        self.setScene(self._scene)
        self.draw_arcs()


    def __radius(self) -> int:
        return (min(self.width(), self.height()) - self.padding * 2) // 2
    
    def draw_arcs(self) -> QPainterPath:
        self._scene.clear()
        cx, cy = self.scene().sceneRect().center().toTuple()

        colors = [QColor("#f00"), QColor("#0f0"), QColor("#00f")]
        for i, value in enumerate(self._values):
            
            path = QPainterPath()
            start_angle = self._start_angle

            angle = (value / sum(self._values)) * pi * 2
            if i != 0:
                start_angle += (sum(self._values[:i]) / sum(self._values)) * pi * 2

            arc_x = cx + self.__radius() * cos(start_angle)
            arc_y = cy - self.__radius() * sin(start_angle)

            path.moveTo(arc_x, arc_y)
            path.arcTo(QRect(arc_x, arc_y, self.__radius(), self.__radius()), degrees(start_angle), degrees(angle))
            self._scene.addPath(path, QPen(colors[i]))
        
    def resizeEvent(self, event: QResizeEvent) -> None:
        self.draw_arcs()
        return super().resizeEvent(event)
    

import sys
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    p = PieChart([1, 1, 2])
    p.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()