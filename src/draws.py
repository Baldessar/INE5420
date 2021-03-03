from PySide6 import QtCore, QtWidgets, QtGui
import transforms as tr

class Line():
  def __init__(self, name, x1, y1, x2, y2, color):
    self.points = [(x1, y1), (x2, y2)]
    self.color = color if color is not None and color != '' else '#000000'
    self.x2 = x2
    self.y2 = y2

  def draw(self, painter, transformX, transformY):
    [(x1, y1), (x2, y2)] = self.points
    x1 = transformX(x1)
    y1 = transformY(y1)
    x2 = transformX(x2)
    y2 = transformY(y2)

    line = QtCore.QLine(x1, y1, x2, y2)

    painter.setPen(self.color)
    painter.drawLine(line)


class Point():
  def __init__(self, name, x, y, color):
    self.points = [(x, y)]
    self.color = color if color is not None and color != '' else '#000000'

  def draw(self, painter, transformX, transformY):
    [(x, y)] = self.points
    x = transformX(x)
    y = transformY(y)

    painter.setPen(self.color)
    painter.drawPoint(QtCore.QPoint(x, y))


class Wireframe():
  def __init__(self, name, points, color):
    self.points = points
    self.normalized_points = points
    self.color = color if color is not None and color != '' else '#000000'

  def set_normalized_points(self, transformations):
    self.normalized_points = tr.transform_points(self.points, transformations)

  def draw(self, painter, transformX, transformY):
    polygon = QtGui.QPolygon()

    painter.setPen(self.color)
    for [x, y] in self.normalized_points:
      point = QtCore.QPoint(transformX(x), transformY(y))
      polygon.append(point)

    painter.drawPolygon(polygon)
