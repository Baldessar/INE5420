import pathlib
import sys
import re
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtUiTools import QUiLoader

from draws import Line, Point, Wireframe

def create_shape(name, text):
  points = [point.split(',') for point in text.split(';')][:-1]
  print(points)

  if len(points) == 1:
    [[x, y]] = points
    return Point(name, float(x), float(y))
  elif len(points) == 2:
    [[x1, y1], [x2, y2]] = points
    return Line(name, float(x1), float(y1), float(x2), float(y2))
  else:
    return Wireframe(name, [[float(x), float(y)] for [x, y] in points])

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

    self.step = 20

    self.gui.drawArea.installEventFilter(self)

    self.gui.buttonUp.clicked.connect(self.moveUp)
    self.gui.buttonDown.clicked.connect(self.moveDown)
    self.gui.buttonLeft.clicked.connect(self.moveLeft)
    self.gui.buttonRight.clicked.connect(self.moveRight)
    self.gui.buttonAddShape.clicked.connect(self.addShape)
    self.gui.buttonClean.clicked.connect(self.cleanShapes)
    self.gui.buttonZoomOut.clicked.connect(self.zoomOut)
    self.gui.buttonZoomIn.clicked.connect(self.zoomIn)

    self.gui.spinBoxXMin.valueChanged.connect(self.setXMin)
    self.gui.spinBoxXMax.valueChanged.connect(self.setXMax)
    self.gui.spinBoxYMin.valueChanged.connect(self.setYMin)
    self.gui.spinBoxYMax.valueChanged.connect(self.setYMax)

    self.gui.spinBoxStep.valueChanged.connect(self.setStep)

    self.shapes = []

    self.gui.show()

  def eventFilter(self, child, e):
    if self.gui.drawArea is child and e.type() == QtCore.QEvent.Paint:
      painter = QtGui.QPainter(child)

      for shape in self.shapes:
        print(f"drawing {type(shape).__name__}")
        shape.draw(painter, self.transformX, self.transformY)

      painter.end()

      return True
    return False

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
    self.ywMin += self.step
    self.ywMax += self.step
    self.gui.drawArea.update()

  def moveDown(self):
    self.ywMin -= self.step
    self.ywMax -= self.step
    self.gui.drawArea.update()

  def moveLeft(self):
    self.xwMin -= self.step
    self.xwMax -= self.step
    self.gui.drawArea.update()

  def moveRight(self):
    self.xwMin += self.step
    self.xwMax += self.step
    self.gui.drawArea.update()

  def setStep(self, value):
    self.step = value

  def transformX(self, xw):
    return ((xw - self.xwMin) / (self.xwMax - self.xwMin)) * (self.xvpMax - self.yvpMin)

  def transformY(self, yw):
    return (1 - ((yw - self.ywMin) / (self.ywMax - self.ywMin))) * (self.yvpMax - self.yvpMin)

  def addShape(self, shape):
    name = self.gui.shapeNameInput.toPlainText().strip()
    points = self.gui.shapePointsInput.toPlainText().strip()

    if re.fullmatch(r"(\d+,\d+;)+", points):
      shape = create_shape(name, points)
      self.shapes.append(shape)
      self.gui.listWidget.addItem(f"{name} - {type(shape).__name__}")
      self.gui.drawArea.update()
    else:
      print("Invalid coordinates format.")

  def cleanShapes(self):
    self.shapes = []
    self.gui.listWidget.clear()
    self.gui.drawArea.update()


if __name__ == "__main__":
  QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
  app = QtWidgets.QApplication(sys.argv)

  window = Window()

  sys.exit(app.exec_())
