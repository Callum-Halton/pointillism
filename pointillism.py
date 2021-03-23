import math, random, sys
from PIL import Image, ImageDraw

class Options:
  def __init__(self):
    # Constants
    self._maxRadius = 40 # maximum Poisson disc radius
    # maxRadius is the fixed exlusion radius when varyDotIntensity is False
    self._sampleLimit = 10 # number of times we'll try to find a new point
    self._varyDotDensity = True
    self._minRadius = 20 # minimum Poisson disc radius

    # Computed Constants
    self._sqrRadius = self._maxRadius ** 2
    if self._varyDotDensity:
      self._sampleRadius = int((self._minRadius + self._maxRadius) / 2)
    else:
      self._sampleRadius = int(self._maxRadius / 2)
    self._sqrSampleRadius = self._sampleRadius ** 2
    self._cellSize = self._maxRadius / math.sqrt(2) # Should this be an integer?
    if self._varyDotDensity:
      self._radiusDiff = self._maxRadius - self._minRadius

    # Interface-Controllable Options
    self._renderConstants = {
      'Max Draw Radius': 10,
      'Vary Dot Radius': False,
      'Vary Dot Intensity': False,
      'White Dots on Black Background': True,
      # Best to leave this as False because it ruins the contrast
      'Moderate Brightness': False
    }

  def getMaxRadius(self):
    return self._maxRadius

  def getSampleLimit(self):
    return self._sampleLimit

  def getVaryDotDensity(self):
    return self._varyDotDensity

  def getMinRadius(self):
    return self._minRadius

  def getSqrRadius(self):
    return self._sqrRadius

  def getSampleRadius(self):
    return self._sampleRadius

  def getSqrSampleRadius(self):
    return self._sqrSampleRadius

  def getCellSize(self):
    return self._cellSize

  def getRadiusDiff(self):
    return self._radiusDiff

  def getMaxDrawRadius(self):
    return self._renderConstants['Max Draw Radius']

  def getVaryDotRadius(self):
    return self._renderConstants['Vary Dot Radius']

  def getVaryDotIntensity(self):
    return self._renderConstants['Vary Dot Intensity']

  def getWhiteDotsOnBlackBackground(self):
    return self._renderConstants['White Dots on Black Background']

  def getModerateBrightness(self):
    return self._renderConstants['Moderate Brightness']

  def renderMenu(self):
    print("\n\nRENDER OPTIONS:\n")
    index = 0
    for key, value in self._renderConstants.items():
      print("[%i] Change: %s (currently %r)" % (index, key, value))
      index += 1
    print("[R] Rerender!")
    print("[Q] Quit")

  def prompt(self):
    return input("\nEnter the code in [] to select an option: ")

  def _isInt(self, val):
    try:
      num = int(val)
    except ValueError:
      return False
    return True

  def parseInput(self, code):
    if self._isInt(code) and int(code) < len(self._renderConstants.keys()):
      renderConstantName = list(self._renderConstants.keys())[int(code)]
      newVal = input("Change " + renderConstantName + " from " +
        str(self._renderConstants[renderConstantName]) + " to: ")
      renderConstantType = type(self._renderConstants[renderConstantName])
      if renderConstantType is bool:
        if newVal.lower() in {'true', 't'}:
          self._renderConstants[renderConstantName] = True
          print(renderConstantName, "has been set to True")
        elif newVal.lower() in {'false', 'f'}:
          self._renderConstants[renderConstantName] = False
          print(renderConstantName, "has been set to False")
        else:
          print(renderConstantName, "must be a Boolean!")
      elif renderConstantType is int:
        if self._isInt(newVal):
          intNewVal = int(newVal)
          self._renderConstants[renderConstantName] = intNewVal
          print(renderConstantName, "has been changed to", newVal + ".")
        else:
          print(renderConstantName, "must be an Integer!")
    else:
      print("Invalid code entered!")


class Point:
  def __init__(self, x, y, options):
    self._options = options
    self.x = x
    self.y = y
    self.r = self._options.getMaxRadius()
    self.l = None

  def getCellPos(self):
    cellSize = self._options.getCellSize()
    return Point(int(self.x // cellSize), int(self.y // cellSize),
                 self._options)

  def computeL(self, sourceImage):
    totLuminosity = 0
    pixelsSampled = 1
    #print(self.x, self.y)
    sx = None
    sy = None
    sampleRadius = self._options.getSampleRadius()
    sqrSampleRadius = self._options.getSqrSampleRadius()
    for x in range(self.x - sampleRadius, self.x + sampleRadius):
        for y in range(self.y - sampleRadius, self.y + sampleRadius):
          sx, sy = x, y
          if (0 <= x < sourceImage.width and 0 <= y < sourceImage.height and
             (self.x - x) ** 2 + (self.y - y) ** 2 <= sqrSampleRadius):
            totLuminosity += sourceImage.pixels[x, y]
            pixelsSampled += 1

    try:
      self.l = int(totLuminosity / pixelsSampled)
    except:
      print(self.x, self.y)
      print(sx, sy)
    if self._options.getVaryDotDensity():
      self.r = ((255 - self.l) / 255 * self._options.getRadiusDiff() +
                self._options.getMinRadius())


class SourceImage:
  def __init__(self, filename, options):
    im = Image.open(filename).convert("L")
    self.pixels = pixels = im.load()
    self.width, self.height = im.size
    cellSize = options.getCellSize()
    self.widthInCells = math.ceil(self.width / cellSize)
    self.heightInCells = math.ceil(self.height / cellSize)


class State:
  def __init__(self, sourceImage, options):
    self._points = []
    self._activePoints = []
    self._activePointsCount = 0
    self._cells = [[[] for x in range(sourceImage.widthInCells)]
                   for y in range(sourceImage.heightInCells)]
    maxDrawRadius = options.getMaxDrawRadius()
    initialPoint = Point(
        random.randint(maxDrawRadius, sourceImage.width - maxDrawRadius),
        random.randint(maxDrawRadius, sourceImage.height - maxDrawRadius),
        options)
    initialPoint.computeL(sourceImage)
    self._options = options

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


def pointIsValid(state, sourceImage, candidatePoint, options):
  SCANPATTERN = [1, 2, 2, 2, 1]
  cellPos = candidatePoint.getCellPos()
  if options.getVaryDotDensity():
    candidatePoint.computeL(sourceImage)

  maxDrawRadius = options.getMaxDrawRadius()
  if (maxDrawRadius <= candidatePoint.x <= sourceImage.width - maxDrawRadius and
      maxDrawRadius <= candidatePoint.y <= sourceImage.height - maxDrawRadius):
    for y in range(-2,3):
      extentMagForRow = SCANPATTERN[y + 2]
      for x in range(-extentMagForRow, extentMagForRow + 1):
        examinedRow, examinedCol = cellPos.y + y, cellPos.x + x
        if (0 <= examinedRow < sourceImage.heightInCells and
            0 <= examinedCol < sourceImage.widthInCells):
          examinedCell = state.getCell(examinedRow, examinedCol)
          for point in examinedCell:
            sqrDistance = ((candidatePoint.x - point.x) ** 2 +
                           (candidatePoint.y - point.y) ** 2)
            if options.getVaryDotDensity():
              if sqrDistance < min(candidatePoint.r, point.r) ** 2:
                return False
            elif sqrDistance < options.getSqrRadius():
              return False
    return True
  return False


def getPointNear(state, sourceImage, spawnPoint, options):
  for i in range(options.getSampleLimit()):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(spawnPoint.r, 2 * spawnPoint.r)
    candidatePoint = Point(int(spawnPoint.x + (dist * math.cos(angle))),
                           int(spawnPoint.y + (dist * math.sin(angle))),
                           options)
    if pointIsValid(state, sourceImage, candidatePoint, options):
      return candidatePoint
  return False

def drawDot(draw, point, l, backgroundIntensity, lExponenent, options):
  dotRadius = options.getMaxDrawRadius()
  if options.getVaryDotRadius():
    dotRadius *= ((abs(l - backgroundIntensity) / 255)**lExponenent)

  if options.getVaryDotIntensity():
    dotIntensity = int(l ** lExponenent)
  else:
    dotIntensity = 255 - backgroundIntensity

  draw.ellipse([(point.x - dotRadius, point.y - dotRadius),
                (point.x + dotRadius, point.y + dotRadius)], fill=dotIntensity)


def render(sourceImage, points, options):
  backgroundIntensity = 255
  if options.getWhiteDotsOnBlackBackground():
    backgroundIntensity = 0

  art = Image.new('L', (sourceImage.width, sourceImage.height),
                  color=backgroundIntensity)
  draw = ImageDraw.Draw(art)

  lExponenent = 1
  if options.getModerateBrightness():
    lExponenent /= (options.getVaryDotIntensity() * 1 +
                    options.getVaryDotRadius() * 2)

  for point in points:
    drawDot(draw, point, point.l, backgroundIntensity, lExponenent, options)

  art.save("output/art.png")
  art.show()


def main():
  sourceFilename = "input/portrait.jpg"
  if len(sys.argv) > 1:
    sourceFilename = sys.argv[1]

  print("Source file: %s" % sourceFilename)

  options = Options()

  sourceImage = SourceImage(sourceFilename, options)
  state = State(sourceImage, options)

  n = 0
  while state.hasActivePoints():
    spawnPoint = state.getRandomActivePoint()
    newPoint = getPointNear(state, sourceImage, spawnPoint, options)
    if newPoint:
      if not options.getVaryDotDensity():
        newPoint.computeL(sourceImage)
      state.addNewPoint(newPoint)
    else:
      state.removeActivePoint(spawnPoint)
    n += 1

  print("Number of points: %d" % state.pointsCount())
  render(sourceImage, state.getPoints(), options)

  while True:
    options.renderMenu()
    code = options.prompt()
    if code.upper() == 'R':
      render(sourceImage, state.getPoints(), options)
    elif code.upper() == 'Q':
      break
    else:
      options.parseInput(code)


if __name__ == "__main__":
  main()
