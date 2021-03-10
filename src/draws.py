from PySide6 import QtCore, QtWidgets, QtGui

import transforms as tr
import clip

class Point():
  def __init__(self, name, x, y, color):
    self.points = [(x, y)]
    self.normalized_points = self.points
    self.name = name
    self.color = color if color is not None and color != '' else '#000000'

  def set_normalized_points(self, transformations):
    self.normalized_points = tr.transform_points(self.points, transformations)

  def draw(self, painter, transformX, transformY):
    clipped = clip.clipPoint(self.normalized_points[0])

    if clipped is not None:
      (x, y) = clipped
      x = transformX(x)
      y = transformY(y)

      painter.setPen(self.color)
      painter.drawPoint(QtCore.QPoint(x, y))


class Line():
  def __init__(self, name, x1, y1, x2, y2, color):
    self.points = [(x1, y1), (x2, y2)]
    self.name = name
    self.normalized_points = self.points
    self.color = color if color is not None and color != '' else '#000000'
    self.x2 = x2
    self.y2 = y2


  def set_normalized_points(self, transformations):
    self.normalized_points = tr.transform_points(self.points, transformations)

  def draw(self, painter, transformX, transformY):
    clipped = clip.liangBarsky(self.normalized_points)

    if clipped is not None:
      [(x1, y1), (x2, y2)] = clipped

      line = QtCore.QLine(transformX(x1), transformY(y1), transformX(x2), transformY(y2))
      # line.append(QtCore.QPoint(transformX(x1), transformY(y1)))
      # line.append(QtCore.QPoint(transformX(x2), transformY(y2)))

      painter.setPen(self.color)
      painter.drawLine(line)


class Wireframe():
  def __init__(self, name, points, color):
    self.points = points
    self.name = name
    self.normalized_points = points
    self.color = color if color is not None and color != '' else '#000000'

  def set_normalized_points(self, transformations):
    self.normalized_points = tr.transform_points(self.points, transformations)

  def draw(self, painter, transformX, transformY):

    painter.setPen(self.color)
    clipped = clip.sutherlandHodgman(self.normalized_points)

    if clipped is not None:
      points = []
      for [x, y] in clipped:
        points.append({'x': transformX(x), 'y': transformY(y)})

      for i in range(len(points)):
        current_point = points[i]
        next_point = points[ (i+1) % len(points)]
        line = QtCore.QLine(current_point['x'], current_point['y'], next_point['x'], next_point['y'])
        painter.drawLine(line)
