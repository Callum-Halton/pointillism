import math, random, sys
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


class SourceImage:
  def __init__(self, filename):
    im = Image.open(filename).convert("L")
    self.pixels = pixels = im.load()
    self.width, self.height = im.size
    self.widthInCells = math.ceil(self.width / CELL_SIZE)
    self.heightInCells = math.ceil(self.height / CELL_SIZE)


class State:
  def __init__(self, image):
    self._points = []
    self._activePoints = []
    self._cells = [[None for x in range(image.widthInCells)]
                   for y in range(image.heightInCells)]
    initialPoint = Point(
        random.randint(DRAW_RADIUS, image.width - DRAW_RADIUS),
        random.randint(DRAW_RADIUS, image.height - DRAW_RADIUS))
    self.addNewPoint(initialPoint)

  def addNewPoint(self, point):
    self._points.append(point)
    self._activePoints.append(point)
    cellPos = point.getCellPos()
    self._cells[cellPos.y][cellPos.x] = point

  def removeActivePoint(self, point):
    self._activePoints.remove(point)

  def getCell(self, row, col):
    return self._cells[row][col]

  def hasActivePoints(self):
    # Accelerate program by using a counter for this?
    return len(self._activePoints) > 0

  def getRandomActivePoint(self):
    point = random.choice(self._activePoints)
    return point

  def pointsCount(self):
    return len(self._points)

  def getPoints(self):
    return self._points.copy() # return a copy to protect the hidden state


def pointIsValid(state, sourceImage, candidatePoint):
  SCANPATTERN = [1, 2, 2, 2, 1]
  cellPos = candidatePoint.getCellPos()
  if (DRAW_RADIUS <= candidatePoint.x <= sourceImage.width - DRAW_RADIUS and
      DRAW_RADIUS <= candidatePoint.y <= sourceImage.height - DRAW_RADIUS):
    for y in range(-2,3):
      extentMagForRow = SCANPATTERN[y + 2]
      for x in range(-extentMagForRow, extentMagForRow + 1):
        examinedRow, examinedCol = cellPos.y + y, cellPos.x + x
        if (0 <= examinedRow < sourceImage.heightInCells and
            0 <= examinedCol < sourceImage.widthInCells):
          examinedCell = state.getCell(examinedRow, examinedCol)
          if (examinedCell is not None and 
              (candidatePoint.x - examinedCell.x) ** 2 +
              (candidatePoint.y - examinedCell.y) ** 2 < SQR_RADIUS):
            return False
    return True
  return False


def getPointNear(state, sourceImage, spawnPoint):
  for i in range(SAMPLE_LIMIT):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(RADIUS, 2 * RADIUS)
    candidatePoint = Point(int(spawnPoint.x + (dist * math.cos(angle))),
                           int(spawnPoint.y + (dist * math.sin(angle))))
    if pointIsValid(state, sourceImage, candidatePoint):
      return candidatePoint
  return False


def getAvgLWithinAHalfRadOf(sourceImage, point):
  totLuminosity = 0
  pixelsSampled = 0
  for x in range(point.x - HALF_RADIUS, point.x + HALF_RADIUS):
      for y in range(point.y - HALF_RADIUS, point.y + HALF_RADIUS):
        if (0 <= x < sourceImage.width and 0 <= y < sourceImage.height and
           (point.x - x) ** 2 + (point.y - y) ** 2 <= SQR_RADIUS / 4):
          totLuminosity += sourceImage.pixels[x, y]
          pixelsSampled += 1
  return int(totLuminosity / pixelsSampled)


def drawDot(draw, point, l, backgroundBlack):
  if backgroundBlack:
    dotRadius = DRAW_RADIUS * l/128
    dotIntensity = 255
  else:
    dotRadius = DRAW_RADIUS * (255-l)/128
    dotIntensity = 0
  draw.ellipse([(point.x - dotRadius, point.y - dotRadius),
                (point.x + dotRadius, point.y + dotRadius)], fill=dotIntensity)


def main():
  sourceFilename = "bros.png"
  if len(sys.argv) > 1:
    sourceFilename = sys.argv[1]

  print("Source file: %s" % sourceFilename)

  sourceImage = SourceImage(sourceFilename)
  state = State(sourceImage)

  while state.hasActivePoints():
    spawnPoint = state.getRandomActivePoint()
    newPoint = getPointNear(state, sourceImage, spawnPoint)
    if newPoint:
      state.addNewPoint(newPoint)
    else:
      state.removeActivePoint(spawnPoint)

  backgroundBlack = True
  backgroundIntensity = 0 if backgroundBlack else 255

  art = Image.new('L', (sourceImage.width, sourceImage.height),
                  color=backgroundIntensity)
  draw = ImageDraw.Draw(art)

  print("Number of points: %d" % state.pointsCount())
  for point in state.getPoints():
    l = getAvgLWithinAHalfRadOf(sourceImage, point)
    drawDot(draw, point, l, backgroundBlack)

  art.save("art.png")
  art.show()


if __name__ == "__main__":
  main()
