import math, random
from PIL import Image, ImageDraw

RADIUS = 10
SQR_RADIUS = RADIUS ** 2
HALF_RADIUS = int(RADIUS / 2)

DRAW_RADIUS = 5
SAMPLE_LIMIT = 200
CELL_SIZE = RADIUS / math.sqrt(2)


class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.diffBetweenAvgLAndRandomNumber = None

  def getCellPos(self):
    return Point(int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))


def addNewPoint(points, activePoints, cells, point):
  points.append(point)
  activePoints.append(point)
  cellPos = point.getCellPos()
  cells[cellPos.y][cellPos.x] = point


def pointIsValid(cells, width, widthInCells, height, heightInCells, candidatePoint):
  SCANPATTERN = [1, 2, 2, 2, 1]
  cellPos = candidatePoint.getCellPos()
  if (DRAW_RADIUS <= candidatePoint.x <= width - DRAW_RADIUS) and (DRAW_RADIUS <= candidatePoint.y <= height - DRAW_RADIUS):
    for y in range(-2,3):
      extentMagForRow = SCANPATTERN[y + 2]
      for x in range(-extentMagForRow, extentMagForRow + 1):
        examinedRow, examinedCol = cellPos.y + y, cellPos.x + x
        if 0 <= examinedRow < heightInCells and 0 <= examinedCol < widthInCells:
          examinedCell = cells[examinedRow][examinedCol]
          if examinedCell is not None and (candidatePoint.x - examinedCell.x) ** 2 + (candidatePoint.y - examinedCell.y) ** 2 < SQR_RADIUS:
            return False
    return True
  return False


def getPointNear(cells, width, widthInCells, height, heightInCells, spawnPoint):
  for i in range(SAMPLE_LIMIT):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(RADIUS, 2 * RADIUS)
    candidatePoint = Point(int(spawnPoint.x + (dist * math.cos(angle))), int(spawnPoint.y + (dist * math.sin(angle))))
    if pointIsValid(cells, width, widthInCells, height, heightInCells, candidatePoint):
      return candidatePoint
  return False


def getAvgLWithinAHalfRadOf(width, height, pixels, point):
  totLuminosity = 0
  pixelsSampled = 0
  for x in range(point.x - HALF_RADIUS, point.x + HALF_RADIUS):
      for y in range(point.y - HALF_RADIUS, point.y + HALF_RADIUS):
        if 0 <= x < width and 0 <= y < height and (point.x - x) ** 2 + (point.y - y) ** 2 <= SQR_RADIUS / 4:
          totLuminosity += pixels[x, y]
          pixelsSampled += 1
  return int(totLuminosity / pixelsSampled)


def drawCircle(draw, point, l):
  draw.ellipse([(point.x - DRAW_RADIUS, point.y - DRAW_RADIUS), (point.x + DRAW_RADIUS, point.y + DRAW_RADIUS)], fill=l)


def main():
  im = Image.open("cat.jpeg").convert("L")
  pixels = im.load()
  width, height = im.size
  widthInCells, heightInCells = math.ceil(width / CELL_SIZE), math.ceil(height / CELL_SIZE)

  points = []
  activePoints = []
  cells = [[None for x in range(widthInCells)] for y in range(heightInCells)]

  initialPoint = Point(random.randint(DRAW_RADIUS, width - DRAW_RADIUS), random.randint(DRAW_RADIUS, height - DRAW_RADIUS))
  addNewPoint(points, activePoints, cells, initialPoint)

  while activePoints:
    spawnPoint = random.choice(activePoints)
    newPoint = getPointNear(cells, width, widthInCells, height, heightInCells, spawnPoint)
    if newPoint:
      addNewPoint(points, activePoints, cells, newPoint)
    else:
      activePoints.remove(spawnPoint)

  art = Image.new('L', (width, height))
  draw = ImageDraw.Draw(art)

  print("Number of points: ", len(points))
  for point in points:
    l = getAvgLWithinAHalfRadOf(width, height, pixels, point)
    drawCircle(draw, point, l)

  art.save("art.png")
  art.show()


if __name__ == "__main__":
  main()
