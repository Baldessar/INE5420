from PySide6 import QtCore, QtWidgets, QtGui

class Line():
  def __init__(self, name, x1, y1, x2, y2, color):
    self.coords = [(x1, y1), (x2, y2)]
    self.color = color if color is not None and color != '' else '#000000'
    self.x2 = x2
    self.y2 = y2

  def draw(self, painter, transformX, transformY):
    [(x1, y1), (x2, y2)] = self.coords
    x1 = transformX(x1)
    y1 = transformY(y1)
    x2 = transformX(x2)
    y2 = transformY(y2)

    line = QtCore.QLine(x1, y1, x2, y2)

    painter.setPen(self.color)
    painter.drawLine(line)


class Point():
  def __init__(self, name, x, y, color):
    self.coords = [(x, y)]
    self.color = color if color is not None and color != '' else '#000000'

  def draw(self, painter, transformX, transformY):
    [(x, y)] = self.coords
    x = transformX(x)
    y = transformY(y)

    painter.setPen(self.color)
    painter.drawPoint(QtCore.QPoint(x, y))


class Wireframe():
  def __init__(self, name, coords, color):
    self.coords = coords
    self.color = color if color is not None and color != '' else '#000000'

  def draw(self, painter, transformX, transformY):
    polygon = QtGui.QPolygon()

    painter.setPen(self.color)
    for [x, y] in self.coords:
      point = QtCore.QPoint(transformX(x), transformY(y))
      polygon.append(point)

    painter.drawPolygon(polygon)
