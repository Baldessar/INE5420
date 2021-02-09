from PySide6 import QtCore, QtWidgets, QtGui

class Line():
  def __init__(self, name, x1, y1, x2, y2):
    self.x1 = x1
    self.y1 = y1
    self.x2 = x2
    self.y2 = y2

  def draw(self, painter, transformX, transformY):
    x1 = transformX(self.x1)
    y1 = transformY(self.y1)
    x2 = transformX(self.x2)
    y2 = transformY(self.y2)

    print(x1, y1, x2, y2)

    line = QtCore.QLine(x1, y1, x2, y2)

    painter.drawLine(line)


class Point():
  def __init__(self, name, x, y):
    self.x = x
    self.y = y

  def draw(self, painter, transformX, transformY):
    x = transformX(self.x)
    y = transformY(self.y)

    painter.drawPoint(QtCore.QPoint(x, y))


class Wireframe():
  def __init__(self, name,points):
    self.points = points

  def draw(self, painter, transformX, transformY):
    polygon = QtGui.QPolygon()

    for [x, y] in self.points:
      point = QtCore.QPoint(transformX(x), transformY(y))
      polygon.append(point)

    painter.drawPolygon(polygon)
