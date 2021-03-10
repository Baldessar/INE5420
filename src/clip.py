import numpy as np
import copy

INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8

xmin = -1
ymin = -1
xmax = 1
ymax = 1

def bound(value):
  return max(-1, min(1, value))

def computeCode(point, xmin, ymin, xmax, ymax):
  [x, y] = point
  code = INSIDE

  if (x < xmin):
    code |= LEFT
  elif (x > xmax):
    code |= RIGHT

  if (y < ymin):
    code |= BOTTOM
  elif (y > ymax):
    code |= TOP

  return code

def cohenSutherland(line):
  [p0, p1] = line

  codeLineStart = computeCode(p0, -1, -1, 1, 1)
  codeLineEnd = computeCode(p1, -1, -1, 1, 1)

  if not (codeLineStart | codeLineEnd):
    print(line, 'INSIDE WINDOW, DRAW COMPLETE')
    return line
  elif (codeLineStart & codeLineEnd):
    print(line, 'OUT OF WINDOW, DO NOT DRAW')
    return None
  else:
    print(line, 'PARTIAL INSIDE WINDOW, COMPUTE CLIPPING')
    [(x0, y0), (x1, y1)] = line
    x_new = None
    y_new = None

    outcodeOut = codeLineEnd if codeLineEnd > codeLineStart else codeLineStart

    if outcodeOut & TOP:
      x_new = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0)
      y_new = ymax
    elif outcodeOut & BOTTOM:
      x_new = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0)
      y_new = ymin
    elif outcodeOut & RIGHT:
      y_new = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0)
      x_new = xmax
    elif outcodeOut & LEFT:
      y_new = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0)
      x_new = xmin

    if (outcodeOut == codeLineStart):
      return [(bound(x_new), bound(y_new)), (bound(x1), bound(y1))]
    else:
      return [(bound(x0), bound(y0)), (bound(x_new), bound(y_new))]


def liangBarsky(line):
  [(x1, y1), (x2, y2)] = line
  t = [None, None, None, None]
  p = [-(x2 - x1), x2 - x1, -(y2 - y1), y2 - y1]
  q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
  t1 = 0
  t2 = 1
  for i in range(0, 4):
    if p[i] > 0:
      t[i] = q[i] / p[i]
      t2 = min(t2, t[i])
    elif p[i] < 0:
      t[i] = q[i] / p[i]
      t1 = max(t1, t[i])
    elif q[i] < 0:
      return None
  if t1 == 0 and t2 == 0:
    return line
  if t1 < t2:
    return [(x1 + t1 * p[1], y1 + t1 * p[3]), (x1 + t2 * p[1], y1 + t2 * p[3])]
  else:
    return None

def sutherlandHodgman(subject):
  clip = [(xmin, ymax), (xmin, ymin), (xmax, ymin), (xmax, ymax)]

  def inside(p, cp0, cp1):
    [x, y] = p
    [x0, y0] = cp0
    [x1, y1] = cp1

    return (x1 - x0) * (y - y0) > (y1 - y0) * (x - x0)

  def intersect(p1, p2, cp0, cp1):
    [x0, y0] = cp0
    [x1, y1] = cp1

    dc = (x0 - x1, y0 - y1)
    dp = (p1[0] - p2[0], p1[1] - p2[1])
    n1 = x0 * y1 - y0 * x1
    n2 = p1[0] * p2[1] - p1[1] * p2[0]
    n3 = 1.0 / (dc[0] * dp[1] - dc[1] * dp[0])
    return ((n1 * dp[0] - n2 * dc[0]) * n3, (n1 * dp[1] - n2 * dc[1]) * n3)

  output = subject.copy()

  cp0 = clip[-1]
  for clip_vertex in clip:
    cp1 = clip_vertex
    inputList = output
    output = []

    # Polygon out of window, do not draw
    if len(inputList) == 0:
      return None

    s = inputList[-1]
    for subjectVertex in inputList:
      e = subjectVertex
      if inside(e, cp0, cp1):
        if not inside(s, cp0, cp1):
          output.append(intersect(s, e, cp0, cp1))
        output.append(e)
      elif inside(s, cp0, cp1):
        output.append(intersect(s, e, cp0, cp1))
      s = e
    cp0 = cp1
  return output


def clipPoint(point):
  [x, y] = point
  if x >= -1 and x <= 1 and y >= -1 and y <= 1 :
    return point
  else:
    return None
