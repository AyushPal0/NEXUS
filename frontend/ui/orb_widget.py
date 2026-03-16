from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPainter, QColor


class OrbWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.radius = 40
        self.growing = True

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def animate(self):

        if self.growing:
            self.radius += 1
            if self.radius > 50:
                self.growing = False
        else:
            self.radius -= 1
            if self.radius < 40:
                self.growing = True

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor(0, 150, 255)

        painter.setBrush(color)
        painter.setPen(color)

        center_x = self.width() // 2
        center_y = self.height() // 2

        painter.drawEllipse(
            center_x - self.radius,
            center_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )