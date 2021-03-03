import pathlib
import sys
import re

import numpy as np

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtUiTools import QUiLoader
import transforms as tr


from draws import Line, Point, Wireframe
import loader

def create_shape(name, text, color='#ff0000'):
  points = [point.split(',') for point in text.split(';')][:-1]
  print(points)

  return Wireframe(name, [[float(x), float(y)] for [x, y] in points], color)


class Window(QtWidgets.QWidget):
  def __init__(self):
    QtWidgets.QWidget.__init__(self)
    path = pathlib.Path(__file__).parent.absolute()
    ui_file = QtCore.QFile(str(path) + "/template.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    loader = QUiLoader()
    self.gui = loader.load(ui_file)

    self.xwMin = 0
    self.xwMax = 200
    self.ywMin = 0
    self.ywMax = 200

    self.xvpMin = 0
    self.xvpMax = self.gui.drawArea.width()
    self.yvpMin = 0
    self.yvpMax = self.gui.drawArea.height()

    self.rotation = 0
    self.translation = None

    self.step = 20

    self.gui.drawArea.installEventFilter(self)

    # Move
    self.gui.buttonUp.clicked.connect(self.moveUp)
    self.gui.buttonDown.clicked.connect(self.moveDown)
    self.gui.buttonLeft.clicked.connect(self.moveLeft)
    self.gui.buttonRight.clicked.connect(self.moveRight)

    # Add and clean shapes
    self.gui.buttonAddShape.clicked.connect(self.addShape)
    self.gui.buttonClean.clicked.connect(self.cleanShapes)
    self.gui.exportOBJButton.clicked.connect(self.export_obj)

    # Zoom
    self.gui.buttonZoomOut.clicked.connect(self.zoomOut)
    self.gui.buttonZoomIn.clicked.connect(self.zoomIn)

    # Measure
    self.gui.spinBoxXMin.valueChanged.connect(self.setXMin)
    self.gui.spinBoxXMax.valueChanged.connect(self.setXMax)
    self.gui.spinBoxYMin.valueChanged.connect(self.setYMin)
    self.gui.spinBoxYMax.valueChanged.connect(self.setYMax)
    self.gui.spinBoxStep.valueChanged.connect(self.setStep)

    # Rotation
    self.gui.rotateButton.clicked.connect(self.rotate)
    self.gui.scaleButton.clicked.connect(self.scale)
    # self.gui.translateButton.clicked.connect(self.translate)
    self.gui.rotateWindowLeftButton.clicked.connect(self.rotateWindowLeft)
    self.gui.rotateWindowRightButton.clicked.connect(self.rotateWindowRight)

    self.shapes_map = {}
    self.shapes = []

    self.gui.show()

  def eventFilter(self, child, e):
    if self.gui.drawArea is child and e.type() == QtCore.QEvent.Paint:
      painter = QtGui.QPainter(self.gui.drawArea)
      self.generate_normalized()

      for shape in self.shapes:
        print(f"drawing {type(shape).__name__}")
        shape.draw(painter, self.transformX, self.transformY)

      painter.end()

      return True
    return False


  def rotateWindowLeft(self):
    self.rotation -= float(self.gui.rotateWindowAngleInput.text())
    self.gui.drawArea.update()


  def rotateWindowRight(self):
    self.rotation += float(self.gui.rotateWindowAngleInput.text())
    self.gui.drawArea.update()


  def rotateWindow(self):
    self.transformations = self.transformations.dot(tr.get_rotation_matrix(0.5, 0, 0))

  def zoomIn(self):
    self.ywMin *= (1 - self.step/100)
    self.ywMax *= (1 - self.step/100)
    self.xwMin *= (1 - self.step/100)
    self.xwMax *= (1 - self.step/100)
    self.gui.drawArea.update()

  def zoomOut(self):
    self.ywMin *= (1 + self.step/100)
    self.ywMax *= (1 + self.step/100)
    self.xwMin *= (1 + self.step/100)
    self.xwMax *= (1 + self.step/100)
    self.gui.drawArea.update()

  def setXMin(self, value):
    self.xwMin = value
    self.gui.drawArea.update()

  def setXMax(self, value):
    self.xwMax = value
    self.gui.drawArea.update()

  def setYMin(self, value):
    self.ywMin = value
    self.gui.drawArea.update()

  def setYMax(self, value):
    self.ywMax = value
    self.gui.drawArea.update()

  def moveUp(self):
    transformation = tr.get_translation_matrix(0, -self.step)
    if self.translation is None:
      self.translation = transformation
    else:
      self.translation = self.translation.dot(transformation)
    # self.ywMin += self.step
    # self.ywMax += self.step
    self.gui.drawArea.update()

  def moveDown(self):
    # self.ywMin -= self.step
    # self.ywMax -= self.step
    transformation = tr.get_translation_matrix(0, self.step)
    if self.translation is None:
      self.translation = transformation
    else:
      self.translation = self.translation.dot(transformation)
    self.gui.drawArea.update()

  def moveLeft(self):
    # self.xwMin -= self.step
    # self.xwMax -= self.step
    transformation = tr.get_translation_matrix(self.step, 0)
    if self.translation is None:
      self.translation = transformation
    else:
      self.translation = self.translation.dot(transformation)
    self.gui.drawArea.update()

  def moveRight(self):
    # self.xwMin += self.step
    # self.xwMax += self.step
    transformation = tr.get_translation_matrix(-self.step, 0)
    if self.translation is None:
      self.translation = transformation
    else:
      self.translation = self.translation.dot(transformation)
    self.gui.drawArea.update()

  def setStep(self, value):
    self.step = value

  def generate_normalized(self):
    size_x = (self.xwMax - self.xwMin) / 2
    size_y = (self.ywMax - self.ywMin) / 2
    wxc = self.xwMin + size_x
    wyc = self.ywMin + size_y

    translate_to_center = tr.get_translation_matrix(-wxc, -wyc)
    rotate = tr.get_rotation_matrix(-self.rotation)
    normalize = tr.get_scale_matrix(1/size_x, 1/size_y)

    transformation = translate_to_center.dot(rotate)

    if self.translation is not None:
      transformation = transformation.dot(self.translation)

    transformation = transformation.dot(normalize)

    for shape in self.shapes:
      shape.set_normalized_points(transformation)

  def transformX(self, xw):
    # return ((xw - self.xwMin) / (self.xwMax - self.xwMin)) * (self.xvpMax - self.yvpMin)
    return ((xw + 1) / 2) * (self.xvpMax - self.yvpMin)

  def transformY(self, yw):
    # return (1 - ((yw - self.ywMin) / (self.ywMax - self.ywMin))) * (self.yvpMax - self.yvpMin)
    return (1 - ((yw + 1) / 2)) * (self.yvpMax - self.yvpMin)

  def addShape(self, shape):
    name = self.gui.shapeNameInput.text().strip()
    points = self.gui.shapePointsInput.text().strip()
    color = self.gui.shapeColorInput.text().strip()

    if name in self.shapes_map:
      print("This name is already taken!")
    elif re.fullmatch(r"(\d+,\d+;)+", points):
      new_shape = create_shape(name, points, color)
      self.shapes.append(new_shape)
      self.shapes_map[name] = new_shape
      self.gui.listWidget.addItem(f"{name} - {type(new_shape).__name__}")
      self.gui.drawArea.update()
    else:
      print("Invalid coordinates format.")

  def cleanShapes(self):
    self.shapes = []
    self.shapes_map = {}
    self.gui.listWidget.clear()
    self.gui.drawArea.update()

  def rotate(self):
    angle = float(self.gui.rotateAngleInput.text())
    selected = self.gui.listWidget.currentItem()

    if selected is not None:
      selected_name = selected.text().split('-')[0].strip()
      shape = self.shapes_map[selected_name]

      if self.gui.radioButtonRotateCenter.isChecked():
        tr.rotate_shape(shape, angle)
      elif self.gui.radioBradioButtonRotateOrigin.isChecked():
        tr.rotate_shape(shape, angle, 0, 0)
      else:
        point = self.gui.rotatePointInput.text().strip()
        if re.fullmatch(r"\d+,\d+", point):
          [x, y] = point.split(',')
          tr.rotate_shape(shape, angle, float(x), float(y))
        else:
          print("Invalid point provided.")
    else:
      print("No object selected!")
    self.gui.drawArea.update()

  def scale(self):
    sx = float(self.gui.scaleInputX.text())
    sy = float(self.gui.scaleInputY.text())
    selected = self.gui.listWidget.currentItem()

    if selected is not None:
      selected_name = selected.text().split('-')[0].strip()
      shape = self.shapes_map[selected_name]

      tr.scale_shape(shape, sx, sy)
      self.gui.drawArea.update()
    else:
      print("No object selected!")

  def translate(self):
    dx = float(self.gui.translateInputX.text())
    dy = float(self.gui.translateInputY.text())
    selected = self.gui.listWidget.currentItem()

    if selected is not None:
      selected_name = selected.text().split('-')[0].strip()
      shape = self.shapes_map[selected_name]

      tr.translate_shape(shape, dx, dy)
      self.gui.drawArea.update()
    else:
      print("No object selected!")

  def export_obj(self):
    loader.save(self)

if __name__ == "__main__":
  QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
  app = QtWidgets.QApplication(sys.argv)

  window = Window()

  sys.exit(app.exec_())
