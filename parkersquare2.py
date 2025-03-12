#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   Parker Square 2

   Copyright (C) 2025 Gien van den Enden - swvandenenden@gmail.com
   License EUPL-1.2, see LICENSE file

   Try to find a magic square of squares (optimized)

   https://www.bradyharanblog.com/the-parker-square
   https://proofwiki.org/wiki/Definition:Parker_Square
   https://en.wikipedia.org/wiki/Magic_square

   https://www.mathpages.com/home/kmath417/kmath417.htm

   https://en.wikipedia.org/wiki/Legendre%27s_three-square_theorem

   x1 x2 x3
   x4 x5 x6
   x7 x8 x9

   row1 = x1 + x2 + x3
   row2 = x4 + x5 + x6
   row3 = x7 + x8 + x9

   col1 = x1 + x4 + x7
   col2 = x2 + x5 + x8
   col3 = x3 + x6 + x9

   d1   = x1 + x5 + x9
   d2   = x3 + x5 + x9

   magic number = m
   x1 + x5 + x9 = m
   x3 + x5 + x7 = m
   x2 + x5 + x8 = m
   x4 + x5 + x6 = m

   x1 + x9 = m - x5
   x3 + x7 = m - x5
   x2 + x8 = m - x5
   x4 + x6 = m - x5

   x1 < x2 < x3 < x4 < x5
   x9 > x1
   x8 > x2
   x7 > x3
   x6 > x4

   x9 > x8 > x7 > x6 > x5

   x5 = 1 .. ( m - 1^2 - 2^2 - 3^2 - 4^2) -> step ^2
   x2 = 2 .. m -> step ^2
   x9 = m - x5 - x1


   Édouard Lucas : structure of a 3x3 magic square
      c − b    | c + (a + b) |   c − a
   ------------+-------------+------------
   c − (a − b) |      c      | c + (a − b)
   ------------+-------------+------------
      c + a    | c − (a + b) |   c + b

   x5 = magic number / 3 ( = c )


   check square is the difficult part...
   https://stackoverflow.com/questions/2489435/check-if-a-number-is-a-perfect-square


   Some magic numbers that give 8 or more square numbers:
     10000000028072187
     76333334111688603
    275333333696786028
    275333335514476875 ->  46 found
   1734666668769321027 -> 136 found


"""
import sys
import os
import time
import shutil
import json
import math
import datetime
import configparser
import multiprocessing

# ---------- Version information ---------------
__version__     = "0.1.2"

__author__      = "Gien van den Enden"
__copyright__   = "Copyright 2025, Gien van den Enden"
__credits__     = [ ]
__license__     = "EUPL-1.2"

__maintainer__  = "Gien van den Enden"
__email__       = "swvandenenden@gmail.com"
__status__      = "Production"


def ParkerIntegerSqrt(n):
  """Compute the integer square root of n, or None if n is not a perfect square.
  https://cs.stackexchange.com/questions/97272/which-is-the-fastest-method-for-calculating-exact-square-root-of-a-integer-of-20

  unfortunately this is not working with 176923366583288836, it gives 420622595 but the answer must be 420622594

  """
  if n == 0:
    return 0

  x = n // 2
  while True:
    y = (x + n // x) // 2
    if abs(x - y) < 2:
      break
    x = y
  if x * x == n:
    return x

  if  (x - 1) * (x - 1) == n:
    return x - 1

  if  (x + 1) * (x + 1) == n:
    return x + 1

  print( f"{n} is not a perfect square x={x}" )
  return None


def ParkerIsSquare(n):
  """
  Check if integer is a perfect square
  https://stackoverflow.com/questions/2489435/check-if-a-number-is-a-perfect-square
  """
  ## Trivial checks
  # if type(n) != int:  ## integer
  #   return False
  if n < 0:      ## positivity
    return False
  if n == 0:      ## 0 pass
    return True

  ## Reduction by powers of 4 with bit-logic
  while n&3 == 0:
    n=n>>2

  ## Simple bit-logic test. All perfect squares, in binary,
  ## end in 001, when powers of 4 are factored out.
  if n&7 != 1:
    return False

  if n==1:
    return True  ## is power of 4, or even power of 2


  ## Simple modulo equivalency test
  c = n%10
  if c in {3, 7}:
    return False  ## Not 1,4,5,6,9 in mod 10
  if n % 7 in {3, 5, 6}:
    return False  ## Not 1,2,4 mod 7
  if n % 9 in {2,3,5,6,8}:
    return False
  if n % 13 in {2,5,6,7,8,11}:
    return False

  ## Other patterns
  if c == 5:  ## if it ends in a 5
    if (n//10)%10 != 2:
      return False    ## then it must end in 25
    if (n//100)%10 not in {0,2,6}:
      return False    ## and in 025, 225, or 625
    if (n//100)%10 == 6:
      if (n//1000)%10 not in {0,5}:
        return False    ## that is, 0625 or 5625
  else:
    if (n//10)%4 != 0:
      return False    ## (4k)*10 + (1,9)


  ## Babylonian Algorithm. Finding the integer square root.
  ## Root extraction.
  s = (len(str(n))-1) // 2
  x = (10**s) * 4

  a = {x, n}
  while x * x != n:
    x = (x + (n // x)) >> 1
    if x in a:
      return False
    a.add(x)
  return True


def ParkerThreeSquareCheck( number ):
  """
  Check if a number can be build with 3 squares
  https://en.wikipedia.org/wiki/Legendre%27s_three-square_theorem
  """
  result = False

  while number % 4 == 0:
    number //= 4

  if number % 8 != 7:
    result = True

  return result


def ParkerSquare( inMagicNumber, inConfig ):
  """
  Search for the magic square of squares
  """
  glbMagicNumber = inMagicNumber
  glbLog         = True
  glbOutputMode  = ""
  glbFileName    = ""
  glbArrNumbers  = []
  glbMatrixSize  = 9                       # matrix is 3x3 = 9
  glbMatrix      = [0] * (glbMatrixSize+1) # hold all the numbers, array is 0-bases we use 1 based
  glbSearchArr   = [0] * (glbMatrixSize+1) # order of search and the way of handling each field
  glbCntSearch   = 0
  glbDirectory   = ""


  def _parkerPrint( line = "" ):
    """
    Print info to file and/or console
    """
    nonlocal glbOutputMode
    nonlocal glbFileName
    nonlocal glbDirectory

    if glbOutputMode == "":
      glbOutputMode  = inConfig[ "Parker" ][ "outputmode"     ]
      glbDirectory   = inConfig[ "Parker" ][ "datadirectory"  ]

    if glbOutputMode in [ "b", "s" ]:
      print( line )

    if glbOutputMode in [ "b", "f" ]:
      if len( glbFileName ) == 0:
        glbFileName = os.path.join( glbDirectory, f"parker_{glbMagicNumber}.txt" )

      line += '\n'
      with open( glbFileName, "a" , encoding="utf-8" ) as fileHandle:
        fileHandle.write( line )

  def _parkerPrintMatrix():
    nonlocal glbArrNumbers
    nonlocal glbMatrix
    nonlocal glbMagicNumber

    result = False

    row1 = glbArrNumbers[ glbMatrix[1] ] + glbArrNumbers[ glbMatrix[2] ] + glbArrNumbers[ glbMatrix[3] ]
    row2 = glbArrNumbers[ glbMatrix[4] ] + glbArrNumbers[ glbMatrix[5] ] + glbArrNumbers[ glbMatrix[6] ]
    row3 = glbArrNumbers[ glbMatrix[7] ] + glbArrNumbers[ glbMatrix[8] ] + glbArrNumbers[ glbMatrix[9] ]

    col1 = glbArrNumbers[ glbMatrix[1] ] + glbArrNumbers[ glbMatrix[4] ] + glbArrNumbers[ glbMatrix[7] ]
    col2 = glbArrNumbers[ glbMatrix[2] ] + glbArrNumbers[ glbMatrix[5] ] + glbArrNumbers[ glbMatrix[8] ]
    col3 = glbArrNumbers[ glbMatrix[3] ] + glbArrNumbers[ glbMatrix[6] ] + glbArrNumbers[ glbMatrix[9] ]

    d1   = glbArrNumbers[ glbMatrix[1] ] + glbArrNumbers[ glbMatrix[5] ] + glbArrNumbers[ glbMatrix[9] ]
    d2   = glbArrNumbers[ glbMatrix[3] ] + glbArrNumbers[ glbMatrix[5] ] + glbArrNumbers[ glbMatrix[7] ]

    if ( row1 != glbMagicNumber or
         row2 != glbMagicNumber or
         row3 != glbMagicNumber or
         col1 != glbMagicNumber or
         col2 != glbMagicNumber or
         col3 != glbMagicNumber or
         d1   != glbMagicNumber or
         d2   != glbMagicNumber    ) :
      result = False
    else:
      result = True

    # print the square with numbers
    powerStr = ''
    width    = math.log10( glbMagicNumber )
    width    = math.ceil(  width          )
    width   += 1
    withP    = 0

    line = " " * ( (width + withP) * 3 + 1 )
    _parkerPrint( f"{line}/{d2:>{width}}" )

    _parkerPrint( f"{glbArrNumbers[glbMatrix[1]]:>{width}}{powerStr}{glbArrNumbers[glbMatrix[2]]:>{width}}{powerStr}{glbArrNumbers[glbMatrix[3]]:>{width}}{powerStr} |{row1:>{width}}" )
    _parkerPrint( f"{glbArrNumbers[glbMatrix[4]]:>{width}}{powerStr}{glbArrNumbers[glbMatrix[5]]:>{width}}{powerStr}{glbArrNumbers[glbMatrix[6]]:>{width}}{powerStr} |{row2:>{width}}" )
    _parkerPrint( f"{glbArrNumbers[glbMatrix[7]]:>{width}}{powerStr}{glbArrNumbers[glbMatrix[8]]:>{width}}{powerStr}{glbArrNumbers[glbMatrix[9]]:>{width}}{powerStr} |{row3:>{width}}" )

    line = '-' * ( (width + withP) * 3 + 1)
    _parkerPrint( line + "\\")

    le = ' ' * withP
    _parkerPrint( f"{col1:>{width}}{le}{col2:>{width}}{le}{col3:>{width}}{le}  {d1:>{width}}" )
    _parkerPrint()

    # print the square in squares ( ^2 format )
    powerStr = '^' + str(  "2"       )
    width    = math.log10( glbMagicNumber )
    width    = math.ceil(  width          )
    width   += 1
    withP    = len( powerStr )

    line = " " * ( (width) * 3 + 1 )
    _parkerPrint( f"{line}/{d2:>{width}}" )

    _parkerPrint( f"{ParkerIntegerSqrt( glbArrNumbers[glbMatrix[1]] ):>{width - withP}}{powerStr}{ParkerIntegerSqrt( glbArrNumbers[glbMatrix[2]] ):>{width - withP}}{powerStr}{ParkerIntegerSqrt( glbArrNumbers[glbMatrix[3]] ):>{width - withP}}{powerStr} |{row1:>{width}}" )
    _parkerPrint( f"{ParkerIntegerSqrt( glbArrNumbers[glbMatrix[4]] ):>{width - withP}}{powerStr}{ParkerIntegerSqrt( glbArrNumbers[glbMatrix[5]] ):>{width - withP}}{powerStr}{ParkerIntegerSqrt( glbArrNumbers[glbMatrix[6]] ):>{width - withP}}{powerStr} |{row2:>{width}}" )
    _parkerPrint( f"{ParkerIntegerSqrt( glbArrNumbers[glbMatrix[7]] ):>{width - withP}}{powerStr}{ParkerIntegerSqrt( glbArrNumbers[glbMatrix[8]] ):>{width - withP}}{powerStr}{ParkerIntegerSqrt( glbArrNumbers[glbMatrix[9]] ):>{width - withP}}{powerStr} |{row3:>{width}}" )

    line = '-' * ( (width) * 3 + 1)
    _parkerPrint( line + "\\")

    le = ''
    _parkerPrint( f"{col1:>{width}}{le}{col2:>{width}}{le}{col3:>{width}}{le}  {d1:>{width}}" )
    _parkerPrint()

    return result

  def _parkerInit():
    nonlocal glbMagicNumber
    nonlocal glbLog

    glbMagicNumber = inMagicNumber                                   # The magic number for the horizontal, vertical and diagonal
    glbLog         = inConfig[ "Parker" ][ "loginformation" ].startswith('t')

    if glbLog == True:
      _parkerPrint( f"Start {datetime.datetime.now():%Y-%m-%d %H:%M:%S}" )

    if glbMagicNumber % 3 != 0:
      if glbLog == True:
        _parkerPrint( f"Magicnumber {glbMagicNumber} is not divisble by 3" )
      return False

    if ParkerThreeSquareCheck( glbMagicNumber ) != True:
      if glbLog == True:
        _parkerPrint( f"Magic number {glbMagicNumber} cannot be written as the sum of 3 squares." )
      return False

    x5 = glbMagicNumber // 3
    if ParkerIsSquare( x5 ) != True:
      if glbLog == True:
        _parkerPrint( f"Magic number {glbMagicNumber} divided by 3 ({x5}) is not a perfect square" )
      return False

    return True

  def _parkerDualSquares():
    """
    Get all the dual squares from x5
    """
    nonlocal glbMagicNumber
    nonlocal glbArrNumbers
    nonlocal glbMatrix

    x5 = glbMagicNumber // 3

    # collect all the dual squares
    glbArrNumbers  = []
    xCount         = 0
    xSquare        = 0
    xCounterSquare = 0
    xMiddleNumber  = glbMagicNumber - x5

    glbArrNumbers.append( 0 ) # 1-based, 0 = zero

    while xSquare < x5 :
      xCount        += 1
      xSquare        = xCount * xCount
      xCounterSquare = xMiddleNumber - xSquare
      if not ParkerIsSquare( xCounterSquare ):
        continue

      if xSquare == xCounterSquare:
        continue

      glbArrNumbers.append( xSquare        )
      glbArrNumbers.append( xCounterSquare )

    if len( glbArrNumbers ) < 8:
      return False

    # at last, at the center = x5
    glbArrNumbers.append( x5 )

    _parkerPrint( f"Magic number: {glbMagicNumber}" )
    _parkerPrint( f"x5: {x5}" )
    _parkerPrint( f"Found square numbers ({len(glbArrNumbers)}): {glbArrNumbers}" )

    # print square for the first 8 squares found
    glbMatrix[ 5 ] = len(glbArrNumbers) - 1 # x5
    glbMatrix[ 1 ] = 1 # glbArrNumbers[ 1 ]
    glbMatrix[ 9 ] = 2 # glbArrNumbers[ 2 ]
    glbMatrix[ 3 ] = 3 # glbArrNumbers[ 3 ]
    glbMatrix[ 7 ] = 4 # glbArrNumbers[ 4 ]
    glbMatrix[ 8 ] = 5 # glbArrNumbers[ 5 ]
    glbMatrix[ 2 ] = 6 # glbArrNumbers[ 6 ]
    glbMatrix[ 6 ] = 7 # glbArrNumbers[ 7 ]
    glbMatrix[ 4 ] = 8 # glbArrNumbers[ 8 ]

    _parkerPrint()
    _parkerPrintMatrix()
    _parkerPrint()

    return True

  def _parkerSearch():
    """
    Fill the 3x3 matrix with all the numbers from glbArrNumbers and
    look if it is a magic square
    """
    nonlocal glbMagicNumber
    nonlocal glbLog
    nonlocal glbArrNumbers
    nonlocal glbSearchArr
    nonlocal glbCntSearch

    # use brute for for the given numbers
    glbSearchArr[ 0 ] = {}
    glbSearchArr[ 1 ] = { "field":1, "calc": None    , "start": None  }
    glbSearchArr[ 2 ] = { "field":3, "calc": None    , "start": None  }
    glbSearchArr[ 3 ] = { "field":2, "calc": [ 1, 3] , "start": None  }
    glbSearchArr[ 4 ] = { "field":5, "calc": None    , "start": None  }
    glbSearchArr[ 5 ] = { "field":7, "calc": [ 3, 5] , "start": None  }
    glbSearchArr[ 6 ] = { "field":4, "calc": [ 1, 7] , "start": None  }
    glbSearchArr[ 7 ] = { "field":6, "calc": [ 4, 5] , "start": None  }
    glbSearchArr[ 8 ] = { "field":8, "calc": [ 2, 5] , "start": None  }
    glbSearchArr[ 9 ] = { "field":9, "calc": [ 3, 6] , "start": None  }

    # reset matrix
    for iKey, _ in enumerate( glbMatrix ):
      glbMatrix[ iKey ] = 0

    checkSearch  = 0
    maxSearch    = len( glbArrNumbers ) - 1
    found        = False              # found a magic square
    glbCntSearch = checkSearch + 1    # current search position in the matrix

    while checkSearch < glbCntSearch <= glbMatrixSize:
      # pylint: disable=unsubscriptable-object
      currSearch = glbSearchArr[ glbCntSearch ]
      currField  = currSearch[ "field" ]
      currCalc   = currSearch[ "calc"  ]

      # debug
      # _parkerPrintMatrix()

      if currCalc == None: # cannot calculate the field value, so iterate it

        if glbMatrix[ currField ] == 0:
          currStart = currSearch[ "start" ]
          if currStart != None:
            newValue = 0
            for iVal in currStart:
              newValue = max( newValue, glbMatrix[ iVal ] )
            glbMatrix[ currField ] = newValue

        # next value
        newValue = glbMatrix[ currField ] + 1

        while newValue in glbMatrix:
          newValue += 1

        glbMatrix[ currField ] = newValue

        if glbMatrix[ currField ] > maxSearch:
          # end of current field reached, go 1 step back
          glbMatrix[ currField ] = 0
          glbCntSearch -= 1
          continue

        # next field in matrix
        glbCntSearch += 1
        continue

      # calculated field, if filled, go 1 back (back-tracking)
      if glbMatrix[ currField ] != 0:
        glbMatrix[ currField ] = 0
        glbCntSearch -= 1
        continue

      # the matrix fields
      fldPos1 = glbMatrix[ currCalc[ 0 ] ]
      fldPos2 = glbMatrix[ currCalc[ 1 ] ]

      fldValue = glbMagicNumber - glbArrNumbers[ fldPos1 ] - glbArrNumbers[ fldPos2 ]
      if fldValue <= 0:
        glbCntSearch -= 1
        continue

      if fldValue not in glbArrNumbers: # check if it is a valid value
        glbCntSearch -= 1
        continue

      # convert to matrix number
      keyFound = False
      for iCntKey, iCntVal in enumerate( glbArrNumbers ):
        if iCntVal == fldValue:
          fldValue = iCntKey
          keyFound = True
          break

      if keyFound != True:
        print( f"fldValue not found: {fldValue}" )

      # must have unique values
      if fldValue in glbMatrix:
        glbCntSearch -= 1
        continue

      # found valid value
      glbMatrix[ currField ] = fldValue
      glbCntSearch += 1

      if glbCntSearch > glbMatrixSize:
        if _parkerPrintMatrix() != True: # check if it is a magic square
          glbCntSearch -= 1
        else:
          found = True # Finally, found a magic square...
          # glbCntSearch -= 1 # search all the solutions
      else:
        # if 5 fields are correct then show the square
        if glbCntSearch > 5:
          _parkerPrintMatrix()

    if glbLog == True:
      if found == True:
        _parkerPrint( "Found a solutions" )
      else:
        _parkerPrint( "No solution found" )

    if found == True and glbOutputMode in [ "b", "f" ]:
      # copy file from 'parker' into 'square'
      fileFound = os.path.join( glbDirectory, f"square_{glbMagicNumber}.txt" )
      shutil.copyfile( glbFileName, fileFound)

    if glbLog == True:
      _parkerPrint( f"End {datetime.datetime.now():%Y-%m-%d %H:%M:%S}" )
      _parkerPrint()

    return found

  # -----------------
  # main ParkerSquare
  # -----------------
  if _parkerInit() != True:
    return False

  if _parkerDualSquares() != True:
    return False

  return _parkerSearch()

# ---------- Configuration ---------------

def DisplayHelp():
  """
  Display help
  """
  print()
  print( "usage: python parkersquare2.py [options] <magicnumber> <magicnumber> <start-end>" )
  print( "options: " )
  print( "  -h               : Help" )
  print( "  -d <directory>   : Directory to place the output, default is current working directory/'parker2'" )
  print( "  -o <outputmode>  : Output mode, f=file, s=screen, b=both. Screen is the default" )
  print( "  -l <True/False>  : Extra log information, default is false" )
  print( "  -c <filename>    : Configuration file" )
  print( "  -n <number>      : Number of concurrent processes. 1 is the default. By 'auto' number of CPU's minus 2 will be used" )
  print( "  -w <number>      : Number of seconds to wait before to try to span a new process, default is 3 seconds" )
  print( "  -s <True/False>  : Load and save the state of the process. Default is false" )
  print( " " )
  print( "Examples:" )
  print( "python parkersquare2.py 21609 -l true" )
  print( "python parkersquare2.py 10000000000000000-2000000000000000000 -o b -n auto -w 10 -s true" )
  print()


# https://docs.python.org/3/library/configparser.html
def ReadConfiguration( argv, magicNumbers, magicRanges ):
  """
  Read the configuration file and set the defaults
  """
  def _checkInteger( cArg, sName, iMin, iMax ):
    if cArg.isdigit() != True:
      print( f"Option {sName}, '{cArg}' is not a positief integer")
      return None

    cArg = int( cArg )
    if cArg < iMin or cArg > iMax:
      print( f"Option {sName}, {cArg} must be between {iMin} and {iMax}")
      return None

    cArg = str( cArg )
    return cArg

  def _checkBoolean( cArg, sName ):
    cArg = cArg.upper()
    if cArg not in [ 'TRUE', 'FALSE', 'T', 'F' ]:
      print( f"Option {sName}, '{cArg}' is not a valid value, expected true or false")
      return None

    if cArg.startswith( 'T' ):
      cArg = 'true'
    else:
      cArg = 'false'

    return cArg

  config = configparser.ConfigParser()

  dirRoot = os.path.dirname(os.path.realpath(__file__))

  # initials
  config[ "Parker" ] = {}
  config[ "Parker" ][ "datadirectory"  ] = ""      # empty is current directory
  config[ "Parker" ][ "outputmode"     ] = "s"     # f=file,s=screen,b=both
  config[ "Parker" ][ "loginformation" ] = "false" # log information
  config[ "Parker" ][ "processes"      ] = "1"     # number of processes parallel, 1 = single thread
  config[ "Parker" ][ "waittime"       ] = "3"     # Wait time in seconds before to try a new process of all process are used
  config[ "Parker" ][ "state"          ] = "false" # Save and load state of current process

  # Process argv
  hashArg = {}
  if argv != None:
    mode = ""
    cArg = ""
    for iCnt in range( 1, len( argv ) ) :
      cArg = argv[ iCnt ]

      if mode != "":

        if mode == "processes":
          if cArg == "auto":
            cArg = max( 1, multiprocessing.cpu_count() - 2 )
            cArg = str( cArg )

          cArg = _checkInteger( cArg, "-n", 1, 32767 )
          if cArg == None:
            return None

        if mode == "waittime":
          cArg = _checkInteger( cArg, "-w", 1, 3600 )
          if cArg == None:
            return None

        if mode == "datadirectory":
          # check directory exist
          if len( cArg ) > 0:
            if os.path.isdir( cArg ) != True:
              print( f"Option -d, {cArg} is not a directory" )
              return None

        if mode == "loginformation":
          cArg = _checkBoolean( cArg, '-l' )
          if cArg == None:
            return None

        if mode == "state":
          cArg = _checkBoolean( cArg, '-s' )
          if cArg == None:
            return None

        if mode == "outputmode":
          if cArg not in [ 'f', 's', 'b' ]:
            print( f"Option -o, {cArg} is not valid, expected 'f', 's' or 'b'" )
            return None

        hashArg[ mode ] = cArg
        mode = ""
        continue

      if cArg == "-s":  # state
        mode = "state"
        continue

      if cArg == "-n":  # processes
        mode = "processes"
        continue

      if cArg == "-w":
        mode = "waittime"
        continue

      if cArg == "-d": # directory
        mode = "datadirectory"
        continue

      if cArg == "-l": # log information
        mode = "loginformation"
        continue

      if cArg == '-o': # output mode
        mode = 'outputmode'
        continue

      if cArg == "-c":  # name ini file`
        mode = "initfilename"
        continue

      if cArg == "-h":
        DisplayHelp()
        return None

      if not cArg.startswith( '-' ):
        # fill number or range
        if '-' in cArg:
          # range
          cNumbers = cArg.split( '-', 2)
          if cNumbers[0].isdigit() != True:
            print( f"{cNumbers[0]} is not a number" )
            return None
          if cNumbers[1].isdigit() != True:
            print( f"{cNumbers[1]} is not a number" )
            return None

          iNum1 = int( cNumbers[0] )
          iNum2 = int( cNumbers[1] )
          if iNum2 < iNum1:
            print( f"{cArg} end number is lesser then start number" )
            return None

          elem = {}
          elem[ 'start' ] = iNum1
          elem[ 'end'   ] = iNum2

          magicRanges.append( elem )
        else:
          if cArg.isdigit() != True:
            print( f"{cArg} is not a number" )
            return None
          magicNumbers.append( int( cArg ))
        continue

      raise NameError( f"Unknown option {cArg}, use -h for help" )

    if mode != '':
      print( f"Missing argument by option {cArg}" )
      return None

  # read configuration
  if "initfilename" in hashArg:
    configFileName = hashArg[ "initfilename" ]
    if not os.path.isfile(configFileName):
      raise NameError( f"Configuration file {configFileName} not found" )
  else:
    configFileName = os.path.join( dirRoot, "parkersquare.ini" )

  print( f"Configuration file: {configFileName}" )
  config.read( configFileName )

  for key, value in hashArg.items():
    config[ "Parker" ][ key ] = value

  # debug
  # with open( configFileName, 'w') as configfile:
  #   config.write(configfile)

  # user/ini-file cannot set this
  config[ "Version" ] = {}
  config[ "Version" ][ "version" ] = __version__

  return config


def CheckConfiguration( config ):
  """
  Check configuration file
  """
  # fill default directory
  if config[ "Parker" ][ "datadirectory"  ] == "":
    glbDirectory = os.path.join( os.getcwd(), "parker2" )
    if config[ "Parker" ][ "outputmode" ] in [ 'b', 'f' ]:
      if not os.path.exists(glbDirectory):
        os.makedirs(glbDirectory)
    config[ "Parker" ][ "datadirectory"  ] = glbDirectory

  # make the path absolute
  config[ "Parker" ][ "datadirectory"  ] = os.path.abspath( config[ "Parker" ][ "datadirectory"  ] )

  # only check by file output
  if config[ "Parker" ][ "outputmode" ]  in [ 'b', 'f' ]:
    if not os.path.exists(config[ "Parker" ][ "datadirectory"  ]):
      print( f'Directory {config[ "Parker" ][ "datadirectory"  ]} not found' )
      return False

  return True

# ---------- Multiprocessing ---------------

def WalkRanges( iRangeNo, startNum, endNum, iConfig ):
  """
  Walk all the magic numbers in the given range
  """
  glbStateFile = None   # filename for state file, none = no state file
  iRangeWalk   = 0

  def _parkerStateSave():
    nonlocal glbStateFile
    nonlocal iRangeWalk

    if glbStateFile == None:
      return

    state = {}
    state[ "startNum"   ] = startNum
    state[ "endNum"     ] = endNum
    state[ "iRangeWalk" ] = iRangeWalk

    jsonObject = json.dumps(state, indent=4)

    with open( glbStateFile, "w", encoding="utf-8" ) as fileHandle:
      fileHandle.write( jsonObject )

  def _parkerStateRead():
    nonlocal glbStateFile
    nonlocal iRangeWalk

    if glbStateFile == None:
      return

    # print( f"State file: {glbStateFile}" )

    if not os.path.isfile( glbStateFile ) :
      return

    state = {}
    with open( glbStateFile, encoding="utf-8" ) as fileHandle:
      state = json.load( fileHandle )

    # print( f"State readed: {state}" )
    if "iRangeWalk" in state:
      iRangeWalk = state[ "iRangeWalk"    ]
      print( f"State restored by range {iRangeNo} width {iRangeWalk}" )

  try:

    if iConfig[ "Parker" ][ "state" ].startswith('t'):
      glbStateFile = os.path.join( iConfig[ "Parker" ][ "datadirectory" ], f"state_{iRangeNo}.json" )

    # Load State
    _parkerStateRead()

    while startNum % 3 != 0:
      startNum += 1

    iRangeWalk = max( startNum, iRangeWalk )
    iIteration = 0
    while iRangeWalk < endNum:

      iIteration += 1
      if iIteration > 10000000: # 10 million
        if glbStateFile != None:
          print( f"Save range: {iRangeNo} -> {iRangeWalk}")
          _parkerStateSave()
        iIteration = 1

      ParkerSquare(iRangeWalk,iConfig )
      iRangeWalk += 3

    # delete state
    if glbStateFile != None:
      if os.path.isfile( glbStateFile):
        os.remove( glbStateFile )

  except KeyboardInterrupt as keyExcept:
    if iConfig[ "Parker" ][ "processes" ] == "1": # by single thread throw exception
      raise keyExcept


def StartThread( iRangeNo, iStart, iEnd, nrProcesses, config, procArr ):
  """
  Start a parker square process
  """

  # 1 is not to use multiprocessing
  if nrProcesses <= 1 :
    WalkRanges( iRangeNo, iStart, iEnd, config )
    return True

  # find process slot and cleanup old processes
  procNr = -1
  for count, value in enumerate(procArr):
    if value != None:
      if not value[ "proc" ].is_alive():
        procArr[ count ] = None

    if value == None:
      if procNr == -1:
        procNr = count

  # no process slot found
  if procNr == -1:
    return False

  # start a new process
  proc = multiprocessing.Process( target=WalkRanges, args=(iRangeNo,iStart,iEnd,config,) )
  proc.start()

  elem = {}
  elem[ "proc"    ] = proc
  elem[ "iRangeNo"] = iRangeNo
  elem[ "iStart"  ] = iStart
  elem[ "iEnd"    ] = iEnd

  procArr[ procNr ] = elem

  return True


def StateWrite( state ):
  """
  Write state to disk
  """
  jsonObject = json.dumps(state, indent=4)

  with open( state[ "statefilename" ], "w", encoding="utf-8") as fileHandle:
    fileHandle.write( jsonObject )


def StateRead( state, config ):
  """
  Read state from disk, it give the new state back.
  It do not change the given state.
  """
  if not os.path.isfile( state[ "statefilename" ]) :
    return None

  newState = None
  with open( state[ "statefilename" ], encoding="utf-8" ) as fileHandle:
    newState = json.load( fileHandle )

  # the state file cannot be restore, it is always in the datadirectory
  newState[ "statefilename" ] = os.path.join( config[ "Parker" ][ "datadirectory"  ], "state_main.json" )

  return newState


def StateCreateLoad( config, magicNumbers, magicRanges):
  """
  Read or create a state file.
  If state file exist if will override the current configuration
  """
  if not config[ "Parker" ][ "state" ].startswith('t'):
    return None

  # check state, if exist load it
  state = {}

  state[ "outputmode"      ] = config[ "Parker" ][ "outputmode"     ]
  state[ "loginformation"  ] = config[ "Parker" ][ "loginformation" ]
  state[ "processes"       ] = config[ "Parker" ][ "processes"      ]
  state[ "waittime"        ] = config[ "Parker" ][ "waittime"       ]

  state[ "magicNumbers"    ] = magicNumbers
  state[ "magicRanges"     ] = magicRanges

  state[ "currentRange"    ] = -1   # current range too processes

  state[ "currprocs"       ] = None # list of all the processes

  state[ "statefilename"   ] = os.path.join( config[ "Parker" ][ "datadirectory"  ], "state_main.json" )

  # already existing state preferred
  newState = StateRead( state, config )

  if newState != None:
    # change configuration with new state
    state = newState

    config[ "Parker" ][ "outputmode"     ] = state[ "outputmode"     ]
    config[ "Parker" ][ "loginformation" ] = state[ "loginformation" ]
    config[ "Parker" ][ "processes"      ] = state[ "processes"      ]
    config[ "Parker" ][ "waittime"       ] = state[ "waittime"       ]

    return state

  # new state file, save it
  StateWrite( state )
  return state

# ---------- Main Loop ---------------

def MainLoop( magicNumbers, magicRanges, config, state ):
  """
  Main loop over all the magic numbers and ranges
  """

  nrProcesses = int( config[ "Parker" ][ "processes" ] )
  waittime    = int( config[ "Parker" ][ "waittime"  ] )

  procArr     = [None] * nrProcesses # array of the processes

  iCurrMagic  = 0
  iCurrRange  = 0

  def _writeCurrentState():
    if state == None:
      return

    # list of current processes
    arrCurr = []
    for checkProc in procArr:
      if checkProc == None:
        continue
      arrCurr.append( checkProc[ "iRangeNo"] )

    state[ "currentRange"    ] = iCurrRange   # current range too processes
    state[ "currprocs"       ] = arrCurr

    StateWrite( state )

  try:
    # split range into ranges for each process 1
    if len( magicRanges ) == 1 and nrProcesses > 1:
      elem     = magicRanges[ 0 ]
      startNum = elem[ 'start' ]
      endNum   = elem[ 'end'   ]

      iRange = (endNum - startNum) // nrProcesses
      del magicRanges[0]
      for iCurrRange in range( 0, nrProcesses ):
        elem = {}
        elem[ 'start' ] = startNum
        elem[ 'end'   ] = startNum + iRange - 1
        magicRanges.append( elem )
        startNum += iRange
      magicRanges[ iCurrRange ][ 'end' ] = endNum

    if state != None and state[ "currprocs" ] != None:
      # restart current processes
      for number in state[ "currprocs" ]:
        elem     = magicRanges[ number ]
        startNum = elem[ 'start' ]
        endNum   = elem[ 'end'   ]
        while StartThread( number, startNum, endNum, nrProcesses, config, procArr ) == False:
          print( f"Wait range: {iCurrRange}")
          time.sleep( waittime )

    iCurrMagic = 0
    iCurrRange = 0

    # restore state if given
    if state != None:
      if state[ "currentRange" ] >= 0:
        iCurrRange = state[ "currentRange" ]

    # walk all the given magic numbers
    while iCurrMagic < len( magicNumbers ):
      number = magicNumbers[ iCurrMagic ]
      ParkerSquare(number,config )
      iCurrMagic += 1

    # walk all the given ranges
    while iCurrRange < len( magicRanges ):
      elem     = magicRanges[ iCurrRange ]
      startNum = elem[ 'start' ]
      endNum   = elem[ 'end'   ] + 1 # inclusive

      while StartThread( iCurrRange, startNum, endNum, nrProcesses, config, procArr ) == False:
        _writeCurrentState()
        print( f"Wait range: {iCurrRange}")
        time.sleep( waittime )

      iCurrRange += 1

    # wait for all the processes to complete
    if nrProcesses > 1:
      while len( multiprocessing.active_children() ) > 0:
        print( f"Wait for processes: {len(multiprocessing.active_children())}")
        _writeCurrentState()
        time.sleep( waittime )

    # delete state file, we are done
    if state != None:
      if os.path.isfile( state[ "statefilename" ] ):
        os.remove( state[ "statefilename" ] )

  except KeyboardInterrupt:
    print( "Keyboard interrupt" )

  except Exception as exceptAll: # pylint: disable=broad-exception-caught
    print( f"Exception: { type(exceptAll).__name__ } {exceptAll}" )


def MainStart():
  """
  Main
  """
  globalMagicNumbers = [] # single magic numbers
  globalMagicRanges  = [] # range magic numbers, elements { start:1, end:2}

  # command line parser
  globalConfig = ReadConfiguration( sys.argv, globalMagicNumbers, globalMagicRanges )
  if globalConfig == None:
    sys.exit()

  if CheckConfiguration( globalConfig ) != True:
    sys.exit()

  # is state is loaded then if will override the configuration and the magic numbers
  globalState = StateCreateLoad( globalConfig, globalMagicNumbers, globalMagicRanges)
  if globalState != None:
    globalMagicNumbers = globalState[ "magicNumbers"   ]
    globalMagicRanges  = globalState[ "magicRanges"    ]

    print( f'State restored: {globalState[ "statefilename" ]}' )

    if CheckConfiguration( globalConfig ) != True:
      print( "Incorrect state file" )
      sys.exit()

  if len( globalMagicNumbers ) == 0 and len( globalMagicRanges ) == 0:
    print( "No magic numbers given" )
    sys.exit()

  print()
  print( "Settings" )
  print( f'Output             : {globalConfig[ "Parker" ][ "outputmode"     ]}' )
  print( f'Extra logging      : {globalConfig[ "Parker" ][ "loginformation" ]}' )
  print( f'Output directory   : {globalConfig[ "Parker" ][ "datadirectory"  ]}' )
  print( f'Number of processes: {globalConfig[ "Parker" ][ "processes"      ]}' )
  print( f'Wait time          : {globalConfig[ "Parker" ][ "waittime"       ]} seconds' )
  print( f'State              : {globalConfig[ "Parker" ][ "state"          ]}' )
  print()
  print( "To stop the program, press ctrl-c" )
  print()

  MainLoop( globalMagicNumbers, globalMagicRanges, globalConfig, globalState )

# ================
# Main
# ================
if __name__ == '__main__': # this is needed otherwise multiprocessing don't work
  MainStart()

# the end
