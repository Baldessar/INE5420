import numpy as np
import statistics
import math

# def transform(shape, matrix):
#   coords = [np.array([x, y, 1]).dot(matrix).tolist() for [x, y] in shape.coords]
#   shape.coords = [[x, y] for [x, y, _] in coords]

def transform_shape(shape, matrix):
  shape.points = transform_points(shape.points, matrix)

def transform_points(points, matrix):
  points = [np.array([x, y, 1]).dot(matrix).tolist() for [x, y] in points]
  return [[x, y] for [x, y, _] in points]

def center(shape):
  cx = statistics.mean([x for [x, y] in shape.points])
  cy = statistics.mean([y for [x, y] in shape.points])

  return (cx, cy)

def get_composite_rotation_matrix(angle, cx, cy):
  translate_to_origin = get_translation_matrix(-cx, -cy)
  rotate = get_rotation_matrix(angle)
  translate_back = get_translation_matrix(cx, cy)

  return translate_to_origin.dot(rotate).dot(translate_back)

def get_rotation_matrix(angle):
  radians = angle * (math.pi/180)
  sine = math.sin(radians)
  cosine = math.cos(radians)
  return np.array([
    [cosine, -sine, 0],
    [sine, cosine, 0],
    [0, 0, 1]
  ])

def get_translation_matrix(dx, dy):
  return np.array([
    [1, 0, 0],
    [0, 1, 0],
    [dx, dy, 1]
  ])

def get_scale_matrix(sx, sy):
  return np.array([
    [sx, 0, 0],
    [0, sy, 0],
    [0, 0, 1]
  ])

def rotate_shape(shape, angle, x = None, y = None):
  [cx, cy] = [x, y]
  if cx == None or cy == None:
    [cx, cy] = center(shape)

  rotate_matrix = get_composite_rotation_matrix(angle, cx, cy)


  transform_shape(shape, rotate_matrix)

def scale_shape(shape, sx, sy):
  [cx, cy] = center(shape)

  translate_to_origin = get_translation_matrix(-cx, -cy)
  translate_back = get_translation_matrix(cx, cy)
  scale_matrix = get_scale_matrix(sx, sy)

  scale_relative_origin_matrix = translate_to_origin.dot(scale_matrix).dot(translate_back)

  transform_shape(shape, scale_relative_origin_matrix)

def translate_shape(shape, dx, dy):
  transform_shape(shape, get_translation_matrix(dx, dy))
