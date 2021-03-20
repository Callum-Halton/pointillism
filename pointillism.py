# This is a test comment from Duncan

import math, random
from PIL import Image, ImageDraw
im = Image.open("bros.png").convert("L")
width, height = im.size
pixels = im.load()

RADIUS = 10
SQR_RADIUS = RADIUS ** 2
HALF_RADIUS = int(RADIUS / 2)

DRAW_RADIUS = 50
SAMPLE_LIMIT = 200
CELL_SIZE = RADIUS / math.sqrt(2)


class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.diffBetweenAvgLAndRandomNumber = None

  def getCellPos(self):
    return Point(int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))


points = []
activePoints = []
widthInCells, heightInCells = math.ceil(width / CELL_SIZE), math.ceil(height / CELL_SIZE)
cells = [[None for x in range(widthInCells)] for y in range(heightInCells)]

def addNewPoint(point):
  points.append(point)
  activePoints.append(point)
  cellPos = point.getCellPos()
  cells[cellPos.y][cellPos.x] = point


SCANPATTERN = [1, 2, 2, 2, 1]
def pointIsValid(candidatePoint):
  cellPos = candidatePoint.getCellPos()
  if (DRAW_RADIUS <= candidatePoint.x <= width - DRAW_RADIUS) and (DRAW_RADIUS <= candidatePoint.y <= height - DRAW_RADIUS):
    for y in range(-2,3):
      extentMagForRow = SCANPATTERN[y + 2]
      for x in range(-extentMagForRow, extentMagForRow + 1):
        examinedCol, examinedRow = cellPos.x + x, cellPos.y + y
        if 0 <= examinedCol < widthInCells and 0 <= examinedRow < heightInCells:
          examinedCell = cells[examinedRow][examinedCol]
          if examinedCell is not None and (candidatePoint.x - examinedCell.x) ** 2 + (candidatePoint.y - examinedCell.y) ** 2 < SQR_RADIUS:
            return False
    return True
  return False


initialPoint = Point(random.randint(DRAW_RADIUS, width - DRAW_RADIUS), random.randint(DRAW_RADIUS, height - DRAW_RADIUS))
addNewPoint(initialPoint)


def getPointNear(spawnPoint):
  for i in range(SAMPLE_LIMIT):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(RADIUS, 2 * RADIUS)
    candidatePoint = Point(int(spawnPoint.x + (dist * math.cos(angle))), int(spawnPoint.y + (dist * math.sin(angle))))
    if pointIsValid(candidatePoint):
      return candidatePoint
  return False


while activePoints:
  spawnPoint = random.choice(activePoints)
  newPoint = getPointNear(spawnPoint)
  if newPoint:
    addNewPoint(newPoint)
  else:
    activePoints.remove(spawnPoint)


art = Image.new('L', (width, height))
draw = ImageDraw.Draw(art)


def getAvgLWithinAHalfRadOf(point):
  totLuminosity = 0
  pixelsSampled = 0
  for x in range(point.x - HALF_RADIUS, point.x + HALF_RADIUS):
      for y in range(point.y - HALF_RADIUS, point.y + HALF_RADIUS):
        if 0 <= x < width and 0 <= y < height and (point.x - x) ** 2 + (point.y - y) ** 2 <= SQR_RADIUS / 4:
          totLuminosity += pixels[x, y]
          pixelsSampled += 1
  return int(totLuminosity / pixelsSampled)


def drawCircle(point, l):
  draw.ellipse([(point.x - DRAW_RADIUS, point.y - DRAW_RADIUS), (point.x + DRAW_RADIUS, point.y + DRAW_RADIUS)], fill=l)


print(len(points))
for point in points:
  l = getAvgLWithinAHalfRadOf(point)
  drawCircle(point, l)

art.save("art.png")
art.show()
