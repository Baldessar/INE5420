import os

from draws import Line, Point, Wireframe

def encode_point(p):
  [x, y] = p
  return f'{x} {y} 1.0'

def encode(shapes, xwmin, ywmin, xwmax, ywmax):
  vertices_txt = ''
  objects_txt = ''
  idx = 1

  vertices_txt += f'v {encode_point([xwmin, ywmin])}\n'
  vertices_txt += f'v {encode_point([xwmax, ywmax])}\n'

  objects_txt += f'o window\n'
  objects_txt += f'w {idx} {idx + 1}\n'
  idx += 2

  for obj in shapes:
    objects_txt += f'o {obj.name}\n'

    if isinstance(obj, Point):
      [point] = obj.points
      vertices_txt += f'v {encode_point(point)}\n'

      objects_txt += f'p {idx}\n'
      idx += 1

    elif isinstance(obj, Line):
      [start, end] = obj.points
      vertices_txt += f'v {encode_point(start)}\n'
      vertices_txt += f'v {encode_point(end)}\n'

      objects_txt += f'l {idx} {idx + 1}\n'
      idx += 2

    elif isinstance(obj, Wireframe):
      n = len(obj.points)
      indexes = ''
      for i in range(n):
        vertices_txt += f'v {encode_point(obj.points[i])}\n'
        indexes += f'{idx + i} '
      indexes += f'{idx}'

      objects_txt += f'l {indexes}\n'
      idx += n
  return vertices_txt + objects_txt

def save(window):
  cwd = os.getcwd()
  with open(cwd + '/output.obj', 'w+') as file:
    contents = encode(
      window.shapes,
      window.xwMin,
      window.ywMin,
      window.xwMax,
      window.ywMax
    )
    file.write(contents)
