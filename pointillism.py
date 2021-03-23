import math, random, sys
from PIL import Image, ImageDraw

# PDS Constants:
# MAX_RADIUS is the fixed exclusion radius when VARY_DOT_DENSITY = False
MAX_RADIUS = 40
SAMPLE_LIMIT = 10
VARY_DOT_DENSITY = True
MIN_RADIUS = 20

# Computed Constants:
SQR_RADIUS = MAX_RADIUS ** 2
SAMPLE_RADIUS = (int((MIN_RADIUS + MAX_RADIUS) / 2) if VARY_DOT_DENSITY
  else int(MAX_RADIUS / 2))

SQR_SAMPLE_RADIUS = SAMPLE_RADIUS ** 2
CELL_SIZE = MAX_RADIUS / math.sqrt(2)
if VARY_DOT_DENSITY:
  RADIUS_DIFF = MAX_RADIUS - MIN_RADIUS

RENDER_CONSTANTS = {
  'Max Draw Radius': 10,
  'Vary Dot Radius': False,
  'Vary Dot Intensity': False,
  'White Dots on Black Background': True,
  # Best to leave this as False as it ruins the contrast
  'Moderate Brightness': False
}

class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.r = MAX_RADIUS
    self.l = None

  def getCellPos(self):
    return Point(int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))

  def computeL(self, sourceImage):
    totLuminosity = 0
    pixelsSampled = 1
    #print(self.x, self.y)
    sx = None
    sy = None
    for x in range(self.x - SAMPLE_RADIUS, self.x + SAMPLE_RADIUS):
        for y in range(self.y - SAMPLE_RADIUS, self.y + SAMPLE_RADIUS):
          sx, sy = x, y
          if (0 <= x < sourceImage.width and 0 <= y < sourceImage.height and
             (self.x - x) ** 2 + (self.y - y) ** 2 <= SQR_SAMPLE_RADIUS):
            totLuminosity += sourceImage.pixels[x, y]
            pixelsSampled += 1

    try:
      self.l = int(totLuminosity / pixelsSampled)
    except:
      print(self.x, self.y)
      print(sx, sy)
    if VARY_DOT_DENSITY:
      self.r = (255 - self.l) / 255 * RADIUS_DIFF + MIN_RADIUS


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
    self._activePointsCount = 0
    self._cells = [[[] for x in range(sourceImage.widthInCells)]
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
    self._activePointsCount += 1
    cellPos = point.getCellPos()
    self._cells[cellPos.y][cellPos.x].append(point)

  def removeActivePoint(self, point):
    self._activePoints.remove(point)
    self._activePointsCount -= 1

  def getCell(self, row, col):
    return self._cells[row][col]

  def hasActivePoints(self):
    return self._activePointsCount > 0

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
  if VARY_DOT_DENSITY:
    candidatePoint.computeL(sourceImage)
  if (RENDER_CONSTANTS['Max Draw Radius'] <= candidatePoint.x <=
      sourceImage.width - RENDER_CONSTANTS['Max Draw Radius'] and
      RENDER_CONSTANTS['Max Draw Radius'] <= candidatePoint.y <=
      sourceImage.height - RENDER_CONSTANTS['Max Draw Radius']):
    for y in range(-2,3):
      extentMagForRow = SCANPATTERN[y + 2]
      for x in range(-extentMagForRow, extentMagForRow + 1):
        examinedRow, examinedCol = cellPos.y + y, cellPos.x + x
        if (0 <= examinedRow < sourceImage.heightInCells and
            0 <= examinedCol < sourceImage.widthInCells):
          examinedCell = state.getCell(examinedRow, examinedCol)
          for point in examinedCell:
            sqr_distance = ((candidatePoint.x - point.x) ** 2 +
            (candidatePoint.y - point.y) ** 2)
            if VARY_DOT_DENSITY:
             if sqr_distance < min(candidatePoint.r, point.r) ** 2:
              return False
            elif sqr_distance < SQR_RADIUS:
               return False
    return True
  return False


def getPointNear(state, sourceImage, spawnPoint):
  for i in range(SAMPLE_LIMIT):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(spawnPoint.r, 2 * spawnPoint.r)
    candidatePoint = Point(int(spawnPoint.x + (dist * math.cos(angle))),
                           int(spawnPoint.y + (dist * math.sin(angle))))
    if pointIsValid(state, sourceImage, candidatePoint):
      return candidatePoint
  return False

def drawDot(draw, point, l, backgroundIntensity, lExponenent):

  dotRadius = (RENDER_CONSTANTS['Max Draw Radius']
     * ((abs(l - backgroundIntensity) / 255)**lExponenent) if RENDER_CONSTANTS['Vary Dot Radius']
     else RENDER_CONSTANTS['Max Draw Radius'])

  dotIntensity = (int(l**lExponenent)
    if RENDER_CONSTANTS['Vary Dot Intensity'] else 255 - backgroundIntensity)

  draw.ellipse([(point.x - dotRadius, point.y - dotRadius),
                (point.x + dotRadius, point.y + dotRadius)], fill=dotIntensity)


def render(sourceImage, points):
  backgroundIntensity = (0 if RENDER_CONSTANTS['White Dots on Black Background']
                         else 255)

  art = Image.new('L', (sourceImage.width, sourceImage.height),
                  color=backgroundIntensity)
  draw = ImageDraw.Draw(art)

  lExponenent = (1 / ((RENDER_CONSTANTS['Vary Dot Intensity'] * 1)
      + (RENDER_CONSTANTS['Vary Dot Radius']* 2))
      if RENDER_CONSTANTS['Moderate Brightness'] else 1)

  for point in points:
    drawDot(draw, point, point.l, backgroundIntensity, lExponenent)

  art.save("output/art.png")
  art.show()


def isInt(val):
  try:
    num = int(val)
  except ValueError:
    return False
  return True


def renderMenu():
  print("\n\nRENDER OPTIONS:\n")
  index = 0
  for key, value in RENDER_CONSTANTS.items():
    print("[%i] Change: %s (currently %r)" % (index, key, value))
    index += 1
  print("[R] Rerender!")
  print("[Q] Quit")


def main():
  sourceFilename = "input/portrait.jpg"
  if len(sys.argv) > 1:
    sourceFilename = sys.argv[1]

  print("Source file: %s" % sourceFilename)

  sourceImage = SourceImage(sourceFilename)
  state = State(sourceImage)

  n = 0
  while state.hasActivePoints():
    spawnPoint = state.getRandomActivePoint()
    newPoint = getPointNear(state, sourceImage, spawnPoint)
    if newPoint:
      if not VARY_DOT_DENSITY:
        newPoint.computeL(sourceImage)
      state.addNewPoint(newPoint)
    else:
      state.removeActivePoint(spawnPoint)
    n += 1

  print("Number of points: %d" % state.pointsCount())
  render(sourceImage, state.getPoints())

  while True:
    renderMenu()
    code = input("\nEnter the code in [] to select an option: ")
    if code.upper() == 'R':
      render(sourceImage, state.getPoints())
    elif code.upper() == 'Q':
      break
    elif isInt(code) and int(code) < len(RENDER_CONSTANTS.keys()):
      renderConstantName = list(RENDER_CONSTANTS.keys())[int(code)]
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
        if isInt(newVal):
          intNewVal = int(newVal)
          RENDER_CONSTANTS[renderConstantName] = intNewVal
          print(renderConstantName, "has been changed to", newVal + ".")
        else:
          print(renderConstantName, "must be an Integer!")
    else:
      print("Invalid code entered!")

if __name__ == "__main__":
  main()







