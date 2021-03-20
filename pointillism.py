# This is a test comment from Duncan

import math, random
from PIL import Image, ImageDraw
im = Image.open("bros.png").convert("L")
width, height = im.size
pixels = im.load()

RADIUS = 3
SQR_RADIUS = RADIUS ** 2
DRAW_RADIUS = 1
SAMPLE_LIMIT = 300
cellSize = RADIUS / math.sqrt(2)


class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.diffBetweenAvgLAndRandomNum = None

  def getCellPos(self):
    return Point(int(self.x // cellSize), int(self.y // cellSize))


points = []
activePoints = []
widthInCells, heightInCells = math.ceil(width / cellSize), math.ceil(height / cellSize)
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
        examinedRow, examinedCol = cellPos.x + x, cellPos.y + y
        if 0 <= examinedRow < widthInCells and 0 <= examinedCol < heightInCells:
          examinedCell = cells[cellPossExamined.y][cellPossExamined.x]
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
def drawCircle(point):
  draw.ellipse([(point.x - DRAW_RADIUS, point.y - DRAW_RADIUS), (point.x + DRAW_RADIUS, point.y + DRAW_RADIUS)], fill=255)


print(len(points))
for point in points:
  drawCircle(point)

art.save("art.png")
art.show()
