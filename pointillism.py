import math, random, sys
from PIL import Image, ImageDraw

# PDS Constants:
RADIUS = 10
SAMPLE_LIMIT = 100

# Computed Constants:
SQR_RADIUS = RADIUS ** 2
HALF_RADIUS = int(RADIUS / 2)
CELL_SIZE = RADIUS / math.sqrt(2)

RENDER_CONSTANTS = {
  'Max Draw Radius': 5,
  'Vary Dot Radius': True,
  'Vary Dot Intensity': True,
  'White Dots on Black Background': True,
  #Best to leave this as False as it ruins the contrast
  'Moderate Brightness': False
}

class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.l = None
    self.diffBetweenAvgLAndRandomNumber = None

  def getCellPos(self):
    return Point(int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))

  def computeL(self, sourceImage):
    self.l = getAvgLWithinAHalfRadOf(sourceImage, self)


class SourceImage:
  def __init__(self, filename):
    im = Image.open(filename).convert("L")
    self.pixels = pixels = im.load()
    self.width, self.height = im.size
    self.widthInCells = math.ceil(self.width / CELL_SIZE)
    self.heightInCells = math.ceil(self.height / CELL_SIZE)


class State:
  def __init__(self, sourceImage):
    self._points = []
    self._activePoints = []
    self._cells = [[None for x in range(sourceImage.widthInCells)]
                   for y in range(sourceImage.heightInCells)]
    initialPoint = Point(
        random.randint(RENDER_CONSTANTS['Max Draw Radius'], sourceImage.width 
          - RENDER_CONSTANTS['Max Draw Radius']),
        random.randint(RENDER_CONSTANTS['Max Draw Radius'], sourceImage.height 
          - RENDER_CONSTANTS['Max Draw Radius']))
    initialPoint.computeL(sourceImage)

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
  if (RENDER_CONSTANTS['Max Draw Radius'] <= candidatePoint.x <= sourceImage.width - RENDER_CONSTANTS['Max Draw Radius'] and
      RENDER_CONSTANTS['Max Draw Radius'] <= candidatePoint.y <= sourceImage.height - RENDER_CONSTANTS['Max Draw Radius']):
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


def drawDot(draw, point, l, backgroundIntensity):
  lExponenent = (1 / ((RENDER_CONSTANTS['Vary Dot Intensity'] * 1)
    + (RENDER_CONSTANTS['Vary Dot Radius']* 2))
    if RENDER_CONSTANTS['Moderate Brightness'] else 1)

  dotRadius = (RENDER_CONSTANTS['Max Draw Radius']
     * ((l / 255)**lExponenent) if RENDER_CONSTANTS['Vary Dot Radius']
     else RENDER_CONSTANTS['Max Draw Radius'])

  dotIntensity = (int(l**lExponenent)
    if RENDER_CONSTANTS['Vary Dot Intensity'] else 255 - backgroundIntensity)

  draw.ellipse([(point.x - dotRadius, point.y - dotRadius),
                (point.x + dotRadius, point.y + dotRadius)], fill=dotIntensity)


def render(sourceImage, points):
  backgroundIntensity = 0 if RENDER_CONSTANTS['White Dots on Black Background'] else 255

  art = Image.new('L', (sourceImage.width, sourceImage.height),
                  color=backgroundIntensity)
  draw = ImageDraw.Draw(art)

  for point in points:
    drawDot(draw, point, abs(backgroundIntensity - point.l), backgroundIntensity)

  art.save("art.png")
  art.show()


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
      newPoint.computeL(sourceImage)
      state.addNewPoint(newPoint)
    else:
      state.removeActivePoint(spawnPoint)

  print("Number of points: %d" % state.pointsCount())
  render(sourceImage, state.getPoints())

  RENDER_CONSTANT_ORDER = ['Max Draw Radius', 'Vary Dot Radius', 
    'Vary Dot Intensity', 'White Dots on Black Background',
     'Moderate Brightness']

  
  print("\n\nRENDER OPTIONS:\n")
  for i in range(0, len(RENDER_CONSTANT_ORDER)):
    print("[%i] Change: %s" % (i, RENDER_CONSTANT_ORDER[i]))
  print("[R] Rerender!")

  while True:
    code = input("\nEnter the code in [] to select an option: ")
    try: 
      if code.upper() == 'R':
        render(sourceImage, state.getPoints())
      else:
        renderConstantName = RENDER_CONSTANT_ORDER[int(code)]
        newVal = input("Change " + renderConstantName + " from " + 
          str(RENDER_CONSTANTS[renderConstantName]) + " to: ")
        renderConstantType = type(RENDER_CONSTANTS[renderConstantName])
        if renderConstantType is bool:
          if newVal.lower() in {'true', 't'}:
            RENDER_CONSTANTS[renderConstantName] = True
            print(renderConstantName, "has been set to True")
          elif newVal.lower() in {'false', 'f'}:
            RENDER_CONSTANTS[renderConstantName] = False
            print(renderConstantName, "has been set to False")
          else:
            print(renderConstantName, "must be a Boolean!")
        elif renderConstantType is int:
          try:
            intNewVal = int(newVal)
            RENDER_CONSTANTS[renderConstantName] = intNewVal
            print(renderConstantName, "has been changed to", newVal + ".")
          except:
            print(renderConstantName, "must be an Integer!")
    except:
      print("Invalid code entered!")

if __name__ == "__main__":
  main()







