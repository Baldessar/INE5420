from PySide6 import QtCore, QtWidgets, QtGui

import numpy as np
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


class Curve():
  def __init__(self, name, points, color):
    self.name = name
    self.points = points
    self.normalized_points = points
    self.bezier_matrix = np.array([
      [-1, 3, -3, 1],
      [3, -6, 3, 0],
      [-3, 3, 0, 0],
      [1, 0, 0, 0]
    ])
    self.color = color if color is not None and color != '' else '#000000'

  def set_normalized_points(self, transformations):
    self.normalized_points = tr.transform_points(self.points, transformations)

  def draw(self, painter, transformX, transformY):

    print(self.normalized_points)
    painter.setPen(self.color)

    resolution = 50

    array_x = np.array([pt[0] for pt in self.normalized_points])

    array_y = np.array([pt[1] for pt in self.normalized_points])

    points = []
    for section in range(0, len(self.normalized_points) - 1, 3):
      for delta in np.linspace(0, 1, resolution):
        T = np.array([delta**3, delta**2, delta, 1])
        TM = T @ self.bezier_matrix
        x = TM @ array_x[section:section + 4]
        y = TM @ array_y[section:section + 4]

        points.append((x, y))

    for line in zip(points, points[1:]):
      [p0, p1] = line
      clipped_p0 = clip.clipPoint(p0)
      clipped_p1 = clip.clipPoint(p1)

      if clipped_p0 is None or clipped_p1 is None:
        clipped = clip.cohenSutherland(line)
        if clipped is not None:
          [[x0, y0], [x1, y1]] = clipped
          painter.drawLine(
            transformX(x0),
            transformY(y0),
            transformX(x1),
            transformY(y1)
          )
      else:
        [[x0, y0], [x1, y1]] = line
        painter.drawLine(
          transformX(x0),
          transformY(y0),
          transformX(x1),
          transformY(y1)
        )
