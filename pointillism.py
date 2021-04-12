import math, random, sys, copy
from PIL import Image, ImageDraw

class Options:
  def __init__(self):
    # Constants
    self._maxRadius = 12 # maximum Poisson disc radius
    # maxRadius is the fixed exlusion radius when varyDotIntensity is False
    self._sampleLimit = 30 # number of times we'll try to find a new point
    self._varyDotDensity = True
    self._minRadius = 6 # minimum Poisson disc radius
    self._useSQRSampling = False

    # Computed Constants
    self._sqrRadius = self._maxRadius ** 2
    if self._varyDotDensity:
      self._sampleRadius = int((self._minRadius + self._maxRadius) / 2)
    else:
      self._sampleRadius = int(self._maxRadius / 2)
    self._sqrSampleRadius = self._sampleRadius ** 2
    self._cellSize = int(self._maxRadius / math.sqrt(2))
    if self._varyDotDensity:
      self._radiusDiff = self._maxRadius - self._minRadius

    # Interface-Controllable Options
    self._renderConstants = {
      'Max Draw Diameter': 6,
      'Min Draw Diameter': 2,
      'Vary Dot Radius': True,
      'Vary Dot Intensity': True,
      'White Dots on Black Background': True,
      # set to 0 for no culling
      # only used if 'Draw Specific Number of Dots' is False.
      'Minimum Difference in Intensity from Background to Draw': 0,
      'Draw Specific Number of Dots': False,
      'Total Number of Dots to Draw': 0
    }

    # should NOT be used in render stage!!!
    if self._renderConstants['White Dots on Black Background']:
      self._stdDotIntensityForSampling = 255
    else:
      self._stdDotIntensityForSampling = 0

  def getStdDotIntensityForSampling(self):
    return self._stdDotIntensityForSampling

  def getDrawSpecificNumOfDots(self):
    return self._renderConstants['Draw Specific Number of Dots']

  def getTotDotsToDraw(self):
    return self._renderConstants['Total Number of Dots to Draw']

  def getMinLDiffTwixDotnBackgroundToDraw(self):
    return self._renderConstants[
      'Minimum Difference in Intensity from Background to Draw']

  def getUseSQRSampling(self):
    return self._useSQRSampling

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
    return self._renderConstants['Max Draw Diameter'] / 2

  def getMinDrawRadius(self):
    return self._renderConstants['Min Draw Diameter'] / 2

  def getVaryDotRadius(self):
    return self._renderConstants['Vary Dot Radius']

  def getVaryDotIntensity(self):
    return self._renderConstants['Vary Dot Intensity']

  def getWhiteDotsOnBlackBackground(self):
    return self._renderConstants['White Dots on Black Background']

  def renderMenu(self):
    print("\n\nRENDER OPTIONS:\n")
    index = 0
    for key, value in self._renderConstants.items():
      print("[%i] Change: %s (currently %r)" % (index, key, value))
      index += 1
    print("\n[R] Rerender!")
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

  def computeL(self, sourceImage, squareSample):
    totLuminosity = 0
    pixelsSampled = 0
    sampleRadius = self._options.getSampleRadius()
    sqrSampleRadius = self._options.getSqrSampleRadius()
    for x in range(self.x - sampleRadius, self.x + sampleRadius):
        for y in range(self.y - sampleRadius, self.y + sampleRadius):
          if ((0 <= x < sourceImage.width and 0 <= y < sourceImage.height)
              and (squareSample
              or (self.x - x) ** 2 + (self.y - y) ** 2 <= sqrSampleRadius)):
            totLuminosity += sourceImage.pixels[x, y]
            pixelsSampled += 1

    self.l = int(totLuminosity / pixelsSampled)
    if self._options.getVaryDotDensity():
      self.r = (self._options.getMinRadius()
        + int(abs(self._options.getStdDotIntensityForSampling() - self.l) / 255
        * self._options.getRadiusDiff()))


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
    self._orderedPoints = None
    self._activePoints = []
    self._activePointsCount = 0
    self._cells = [[[] for x in range(sourceImage.widthInCells)]
                   for y in range(sourceImage.heightInCells)]

    maxDrawRadius = math.ceil(options.getMaxDrawRadius())

    initialPoint = Point(
        random.randint(maxDrawRadius, sourceImage.width - maxDrawRadius),
        random.randint(maxDrawRadius, sourceImage.height - maxDrawRadius),
        options)
    initialPoint.computeL(sourceImage, options.getUseSQRSampling())
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
    return copy.deepcopy(self._points) # return a copy to protect hidden state

  def pickNPoints(self, n, pickFromTop):
    if self._orderedPoints is None:
      self._orderedPoints = [[] for i in range(256)]
      for point in self.getPoints():
        self._orderedPoints[point.l].append(point)

    processedOrderedPoints = copy.deepcopy(self._orderedPoints)
    if pickFromTop:
      processedOrderedPoints = reversed(processedOrderedPoints)

    pickedPoints = []
    for lBucket in processedOrderedPoints:
      while lBucket:
        if len(pickedPoints) == n:
          return(pickedPoints)
        else:
          pickedPoint = random.choice(lBucket)
          pickedPoints.append(pickedPoint)
          lBucket.remove(pickedPoint)

    print("The number of dots you want to draw is larger than the number of" +
      " points sampled.\nTo sample more points, decrease the maxRadius.")
    return pickedPoints

# Move to State
def pointIsValid(state, sourceImage, candidatePoint, options):
  maxDrawRadius = options.getMaxDrawRadius()
  if (maxDrawRadius <= candidatePoint.x <= sourceImage.width - maxDrawRadius and
      maxDrawRadius <= candidatePoint.y <= sourceImage.height - maxDrawRadius):

    cellPos = candidatePoint.getCellPos()
    if options.getVaryDotDensity():
      candidatePoint.computeL(sourceImage, True)

    SCANPATTERN = [1, 2, 2, 2, 1]
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
              if sqrDistance < max(candidatePoint.r, point.r) ** 2:
                return False
            elif sqrDistance < options.getSqrRadius():
              return False
    return True
  return False


# Problably move to state class
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


# Probably move to point class
# Condense constans in render!!!!
def drawDot(draw, point, backgroundIntensity, options):
  lDiffTwixDotnBackground = abs(point.l - backgroundIntensity)
  if (options.getDrawSpecificNumOfDots() or
      lDiffTwixDotnBackground >= options.getMinLDiffTwixDotnBackgroundToDraw()):

    # This first dot radius assignment can be thoroughly optimized by condensing
    # constants in render
    if options.getVaryDotRadius():
      dotRadius = ((options.getMaxDrawRadius() - options.getMinDrawRadius())
       * lDiffTwixDotnBackground / 255 + options.getMinDrawRadius())
    else:
      dotRadius = options.getMaxDrawRadius()

    if options.getVaryDotIntensity():
      dotIntensity = point.l
    else:
      dotIntensity = 255 - backgroundIntensity

    draw.ellipse([(point.x - dotRadius, point.y - dotRadius),
                  (point.x + dotRadius - 1, point.y + dotRadius - 1)],
                  fill=dotIntensity)
    return True
  return False


# For now leave as a function
def render(sourceImage, state, options):
  if options.getWhiteDotsOnBlackBackground():
    backgroundIntensity = 0
  else:
    backgroundIntensity = 255

  art = Image.new('L', (sourceImage.width, sourceImage.height),
                  color=backgroundIntensity)
  draw = ImageDraw.Draw(art)

  if options.getDrawSpecificNumOfDots():
    pointsToRender = state.pickNPoints(
      options.getTotDotsToDraw(),
      options.getWhiteDotsOnBlackBackground())
  else:
    pointsToRender = state.getPoints()

  dotsRendered = 0
  for point in pointsToRender:
    dotsRendered += drawDot(draw, point, backgroundIntensity, options)

  print("Number of dots rendered: %d" % dotsRendered)
  art.save("output/art.png")
  art.show()


def main():
  sourceFilename = "input/smile.png"
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
      if not (options.getVaryDotDensity() and options.getUseSQRSampling()):
        newPoint.computeL(sourceImage, options.getUseSQRSampling())
      state.addNewPoint(newPoint)
    else:
      state.removeActivePoint(spawnPoint)
    n += 1

  print("Number of points sampled: %d" % state.pointsCount())
  render(sourceImage, state, options)

  while True:
    options.renderMenu()
    code = options.prompt()
    if code.upper() == 'R':
      render(sourceImage, state, options)
    elif code.upper() == 'Q':
      break
    else:
      options.parseInput(code)


if __name__ == "__main__":
  main()

'''
GRAVEYARD OF BAD CODE:
=====================

# Best to leave this as False because it ruins the contrast
'Moderate Brightness': False

def getModerateBrightness(self):
  return self._renderConstants['Moderate Brightness']

lExponenent = 1
if options.getModerateBrightness():
  lExponenent /= (options.getVaryDotIntensity() * 1 +
                  options.getVaryDotRadius() * 2)


'''