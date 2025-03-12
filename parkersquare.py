#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   Parker Square

   Copyright (C) 2025 Gien van den Enden - swvandenenden@gmail.com
   License EUPL-1.2, see LICENSE file

   Try to find a Parker Square with brute force and some optimizations

   https://www.bradyharanblog.com/the-parker-square
   https://proofwiki.org/wiki/Definition:Parker_Square
   https://en.wikipedia.org/wiki/Magic_square

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

   Parker Square: 21609 give almost a solution (1 diagonal not)

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


# ---------- Magic Square check ---------------

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
  Search for the magic square
  """
  glbMatrixSize  = 9                       # matrix is 3x3 = 9
  glbMatrix      = [0] * (glbMatrixSize+1) # hold all the numbers, array is 0-bases we use 1 based
  glbSearchArr   = [0] * (glbMatrixSize+1) # order of search and the way of handling each field

  glbMagicNumber = 15                      # The magic number for the horizontal, vertical and diagonal

  glbArrNumbers  = [0]    # array of all the numbers, value is the calculate values
  glbArrValues   = {}     # reverse of glbArrNumbers, hash is the calculated value, the value is the array number
  glbArrSize     = 1      # size of glbArrNumbersdepending of magic number
  glbPower       = 2      # power, 1 = normal, 2 = power of 2, 3 = power of 3, etc.

  glbLog         = True   # extra logging
  glbFileName    = ""     # filename for the output
  glbDirectory   = ""
  glbOutputMode  = "b"    # f=file, s=screen, b=both
  glbBruteForce  = False  # use brute force

  glbCntSearch   = 0      # search index in glbMatrix

  glbStateFile   = None   # filename for state file, none = no state file


  def _parkerPrint( line = "" ):
    """
    Print info to file and/or console
    """
    nonlocal glbOutputMode
    nonlocal glbFileName

    if glbOutputMode in [ "b", "s" ]:
      print( line )

    if glbOutputMode in [ "b", "f" ]:
      line += '\n'
      with open( glbFileName, "a" , encoding="utf-8" ) as fileHandle:
        fileHandle.write( line )

  def _parkerInit():
    """
    Initialization of the global vars
    """
    nonlocal glbMagicNumber
    nonlocal glbArrSize
    nonlocal glbMatrix
    nonlocal glbArrNumbers
    nonlocal glbSearchArr
    nonlocal glbFileName
    nonlocal glbDirectory
    nonlocal glbStateFile
    nonlocal glbOutputMode
    nonlocal glbLog
    nonlocal glbMatrixSize
    nonlocal glbArrValues
    nonlocal glbBruteForce

    # no directory given, the use the current working directory with sub directory "parker"
    if glbDirectory == None or len( glbDirectory ) == 0:
      glbDirectory = os.path.join( os.getcwd(), "parker" )
      if glbOutputMode in [ 'b', 'f' ]:
        if not os.path.exists( glbDirectory ):
          os.makedirs( glbDirectory )

    if glbOutputMode in [ 'b', 'f' ]:
      if os.path.exists( glbDirectory ) != True:
        raise NameError( f"Directory {glbDirectory} does not exist" )

    glbFileName = os.path.join( glbDirectory, f"parker_{glbMagicNumber}.txt" )

    glbStateFile = None
    if inConfig[ "Parker" ][ "state" ].startswith('t'):
      glbStateFile = os.path.join( glbDirectory, f"state_{glbMagicNumber}.txt" )

    if glbLog == True:
      _parkerPrint( f"Start {datetime.datetime.now():%Y-%m-%d %H:%M:%S}" )

    # we use 1-based, but set the zero (0) value too
    # reset the matrix to zero
    for iCnt in range( glbMatrixSize + 1 ):
      glbMatrix[ iCnt ] = 0

    glbArrSize = int( ( glbMagicNumber - 1 - 2 ** glbPower ) ** ( 1 / glbPower ) )

    try:
      # TODO to big array, can this an other way?
      glbArrNumbers = [0] * ( glbArrSize + 1 )  # 1-based
    except MemoryError as memExcept:
      print( f"Memory error unable to locate array of size {glbArrSize}" )
      raise memExcept

    for iCnt in range( glbArrSize + 1 ):
      iValue                 = iCnt ** glbPower
      glbArrNumbers[ iCnt ]  = iValue
      glbArrValues[ iValue ] = iCnt

    # the glbSearchArr has order to calculate the values
    # field = number in glbMatrix
    # calc  = how the calc value, None = auto increment, array = field numbers to subtract of glbMagicNumber
    # start = value to start, None = 1, otherwise array of field numbers, max value will the start value

    if glbBruteForce == True:
      # this search start left upper, brute force, no optimizations, search all combinations
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
    elif glbPower == 1:
      glbSearchArr[ 0 ] = {}
      glbSearchArr[ 1 ] = { "field":5, "calc": None    , "start": None  } # fixed always magicnumber / 3
      glbSearchArr[ 2 ] = { "field":1, "calc": None    , "start": None  }
      glbSearchArr[ 3 ] = { "field":9, "calc": [ 1, 5] , "start": None  }
      glbSearchArr[ 4 ] = { "field":3, "calc": None    , "start": [1]   }
      glbSearchArr[ 5 ] = { "field":2, "calc": [1,3]   , "start": None  }
      glbSearchArr[ 6 ] = { "field":6, "calc": [ 3, 9] , "start": None  }
      glbSearchArr[ 7 ] = { "field":4, "calc": [ 5, 6] , "start": None  }
      glbSearchArr[ 8 ] = { "field":8, "calc": [ 2, 5] , "start": None  }
      glbSearchArr[ 9 ] = { "field":7, "calc": [ 1, 4] , "start": None  }
    else:
      # this search start left upper
      glbSearchArr[ 0 ] = {}
      glbSearchArr[ 1 ] = { "field":1, "calc": None    , "start": None  }
      glbSearchArr[ 2 ] = { "field":3, "calc": None    , "start": [1]   }
      glbSearchArr[ 3 ] = { "field":2, "calc": [ 1, 3] , "start": None  }
      glbSearchArr[ 4 ] = { "field":5, "calc": None    , "start": [3]   }
      glbSearchArr[ 5 ] = { "field":7, "calc": [ 3, 5] , "start": None  }
      glbSearchArr[ 6 ] = { "field":4, "calc": [ 1, 7] , "start": None  }
      glbSearchArr[ 7 ] = { "field":6, "calc": [ 4, 5] , "start": None  }
      glbSearchArr[ 8 ] = { "field":8, "calc": [ 2, 5] , "start": None  }
      glbSearchArr[ 9 ] = { "field":9, "calc": [ 3, 6] , "start": None  }

  def _parkerPrintMatrix():
    nonlocal glbArrNumbers
    nonlocal glbMatrix
    nonlocal glbPower
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

    if result == True or glbPower > 1:
      powerStr = '^' + str(  glbPower       )
      width    = math.log10( glbMagicNumber )
      width    = math.ceil(  width          )
      width   += 1
      withP    = len( powerStr )

      line = " " * ( (width + withP) * 3 + 1 )
      _parkerPrint( f"{line}/{d2:>{width}}" )

      _parkerPrint( f"{glbMatrix[1]:>{width}}{powerStr}{glbMatrix[2]:>{width}}{powerStr}{glbMatrix[3]:>{width}}{powerStr} |{row1:>{width}}" )
      _parkerPrint( f"{glbMatrix[4]:>{width}}{powerStr}{glbMatrix[5]:>{width}}{powerStr}{glbMatrix[6]:>{width}}{powerStr} |{row2:>{width}}" )
      _parkerPrint( f"{glbMatrix[7]:>{width}}{powerStr}{glbMatrix[8]:>{width}}{powerStr}{glbMatrix[9]:>{width}}{powerStr} |{row3:>{width}}" )

      line = '-' * ( (width + withP) * 3 + 1)
      _parkerPrint( line + "\\")

      le = ' ' * withP
      _parkerPrint( f"{col1:>{width}}{le}{col2:>{width}}{le}{col3:>{width}}{le}  {d1:>{width}}" )
      _parkerPrint()

    return result

  def _parkerStateSave():
    nonlocal glbCntSearch
    nonlocal glbMatrix
    nonlocal glbStateFile

    if glbStateFile == None:
      return

    state = {}
    state[ "glbCntSearch" ] = glbCntSearch
    state[ "glbMatrix"    ] = glbMatrix

    jsonObject = json.dumps(state, indent=4)

    with open( glbStateFile, "w", encoding="utf-8" ) as fileHandle:
      fileHandle.write( jsonObject )

  def _parkerStateRead():
    nonlocal glbCntSearch
    nonlocal glbMatrix
    nonlocal glbStateFile

    if glbStateFile == None:
      return

    if not os.path.isfile( glbStateFile ) :
      return

    state = {}
    with open( glbStateFile, encoding="utf-8" ) as fileHandle:
      state = json.load( fileHandle )

    if "glbCntSearch" in state:
      glbCntSearch = state[ "glbCntSearch" ]
      glbMatrix    = state[ "glbMatrix"    ]

  def _parkerSearch():
    """
    Search for a solution
    Iterative process so we can save and load the state
    """
    nonlocal glbCntSearch
    nonlocal glbLog
    nonlocal glbArrSize
    nonlocal glbMagicNumber
    nonlocal glbPower
    nonlocal glbMatrixSize
    nonlocal glbSearchArr
    nonlocal glbMatrix
    nonlocal glbArrNumbers
    nonlocal glbFileName
    nonlocal glbStateFile
    nonlocal glbBruteForce

    if glbLog == True:
      _parkerPrint( f"Array size: {glbArrSize}, magic number: {glbMagicNumber}, power: {glbPower}" )

    if glbMagicNumber % 3 != 0:
      if glbLog == True:
        _parkerPrint( f"Magicnumber {glbMagicNumber} not divisable by 3" )
      return False

    if glbBruteForce == True:
      maxSearch   = glbArrSize  # search all combinations, all rotations
      checkSearch = 0           # lower bound for the search, special if power is 1
    else:
      maxSearch = glbArrSize // 2 + 1

      if glbPower == 1:
        glbMatrix[ 5 ] = glbMagicNumber // 3
        checkSearch    = 1
        maxSearch      = glbMagicNumber // 3 + 1
      else:
        checkSearch = 0

    if glbPower == 2:
      if ParkerThreeSquareCheck( glbMagicNumber ) != True:
        if glbLog == True:
          _parkerPrint( f"Magic number {glbMagicNumber} cannot be written as the sum of 3 squares." )
        return False

    found        = False              # found a magic square
    glbCntSearch = checkSearch + 1    # current search position in the matrix
    iteration    = 0                  # iteration counter for save the state of the search

    _parkerStateRead() # read state if available

    while checkSearch < glbCntSearch <= glbMatrixSize:
      iteration += 1
      if iteration > 100000000 : # 100 million
        iteration = 0
        _parkerStateSave()

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

      if fldValue not in glbArrValues: # check if it is a valid value
        glbCntSearch -= 1
        continue

      # convert to matrix number
      fldValue = glbArrValues[ fldValue ]

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
          if glbBruteForce == True:
            glbCntSearch -= 1 # search all the solutions
      else:
        # if power greater or equal 2 and 8 fields are correct then show the square, but not for brute force
        if glbBruteForce == False and glbPower >= 2 and glbCntSearch > 8:
          _parkerPrintMatrix()

      continue

    if glbLog == True:
      if found == True:
        _parkerPrint( "Found a solutions" )
      else:
        _parkerPrint( "No solution found" )

    if found == True and glbOutputMode in [ "b", "f" ]:
      # copy file from 'parker' into 'square'
      fileFound = os.path.join( glbDirectory, f"square_{glbMagicNumber}.txt" )
      shutil.copyfile( glbFileName, fileFound)

    if glbStateFile != None:
      if os.path.isfile( glbStateFile):
        os.remove( glbStateFile )

    if glbLog == True:
      _parkerPrint( f"End {datetime.datetime.now():%Y-%m-%d %H:%M:%S}" )
      _parkerPrint()

    return found

  # --------------------
  # ParkerSquare main
  # --------------------
  glbMagicNumber = inMagicNumber                                   # The magic number for the horizontal, vertical and diagonal
  glbPower       = int( inConfig[ "Parker" ][ "power"          ] ) # power 1 = normal, 2 = power of 2, 3 = power of 3, etc.
  glbDirectory   =      inConfig[ "Parker" ][ "datadirectory"  ]
  glbOutputMode  =      inConfig[ "Parker" ][ "outputmode"     ]
  glbLog         =      inConfig[ "Parker" ][ "loginformation" ].startswith('t')
  glbBruteForce  =      inConfig[ "Parker" ][ "bruteforce"     ].startswith('t')

  # debug
  # print( f"glbMagicNumber: {glbMagicNumber}")
  # print( f"glbPower      : {glbPower}"      )
  # print( f"glbDirectory  : {glbDirectory}"  )
  # print( f"glbOutputMode : {glbOutputMode}" )
  # print( f"glbLog        : {glbLog}"        )

  try:
    _parkerInit()
    _parkerSearch()
  except KeyboardInterrupt as keyExcept:
    if inConfig[ "Parker" ][ "processes" ] == "1": # by single thread throw exception
      raise keyExcept


# ---------- Configuration ---------------

def DisplayHelp():
  """
  Display help
  """
  print()
  print( "usage: python parkersquare.py [options] <magicnumber> <magicnumber> <start-end>" )
  print( "options: " )
  print( "  -h               : Help" )
  print( "  -p <number>      : Power, default is 2" )
  print( "  -d <directory>   : Directory to place the output, default is current working directory/'parker'" )
  print( "  -o <outputmode>  : Output mode, f=file, s=screen, b=both. Screen is the default" )
  print( "  -l <True/False>  : Extra log information, default is true" )
  print( "  -c <filename>    : Configuration file" )
  print( "  -n <number>      : Number of concurrent processes. 1 is the default. By 'auto' number of CPU's minus 2 will be used" )
  print( "  -w <number>      : Number of seconds to wait before to try to span a new process, default is 3 seconds" )
  print( "  -s <True/False>  : Load and save the state of the process. Default is false" )
  print( "  -b <True/False>  : Use brute force, check all the combinations and no optimizations" )
  print( " " )
  print( "Examples:" )
  print( "python parkersquare.py 21609" )
  print( "python parkersquare.py 34344 -p 1 -l true -o s" )
  print( "python parkersquare.py 100-100000 -p 2 -l false -o b" )
  print( "python parkersquare.py 100000000000-200000000000 -p 2 -l false -o b -n auto -w 10 -s true" )
  print( "python parkersquare.py 194481 -b true" )
  # print( "python parkersquare.py 4691556 -b true" )
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
  config[ "Parker" ][ "power"          ] = "2"
  config[ "Parker" ][ "datadirectory"  ] = ""      # empty is current directory
  config[ "Parker" ][ "outputmode"     ] = "s"     # f=file,s=screen,b=both
  config[ "Parker" ][ "loginformation" ] = "true"  # log information
  config[ "Parker" ][ "processes"      ] = "1"     # number of processes parallel, 1 = single thread
  config[ "Parker" ][ "waittime"       ] = "3"     # Wait time in seconds before to try a new process of all process are used
  config[ "Parker" ][ "state"          ] = "false" # Save and load state of current process
  config[ "Parker" ][ "bruteforce"     ] = "false" # Save brute force, check all the combinations, no optimizations

  # Process argv
  hashArg = {}
  if argv != None:
    mode = ""
    cArg = ""
    for iCnt in range( 1, len( argv ) ) :
      cArg = argv[ iCnt ]

      if mode != "":
        if mode == "power":
          # check integer
          cArg = _checkInteger( cArg, "-p", 1, 100 )
          if cArg == None:
            return None

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

        if mode == "bruteforce":
          cArg = _checkBoolean( cArg, '-b' )
          if cArg == None:
            return None

        if mode == "outputmode":
          if cArg not in [ 'f', 's', 'b' ]:
            print( f"Option -o, {cArg} is not valid, expected 'f', 's' or 'b'" )
            return None

        hashArg[ mode ] = cArg
        mode = ""
        continue

      if cArg == "-b":
        mode = "bruteforce"
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

      if cArg == "-p":  # power
        mode = "power"
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
    glbDirectory = os.path.join( os.getcwd(), "parker" )
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

def StartThread( magicNumber, nrProcesses, config, procArr ):
  """
  Start a parker square process
  """

  # 1 is not to use multiprocessing, all in 1 thread
  if nrProcesses <= 1:
    ParkerSquare(magicNumber,config )
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
  proc = multiprocessing.Process( target=ParkerSquare, args=(magicNumber,config,) )
  proc.start()

  elem = {}
  elem[ "proc"  ] = proc
  elem[ "number"] = magicNumber

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

  state[ "power"           ] = config[ "Parker" ][ "power"          ]
  state[ "outputmode"      ] = config[ "Parker" ][ "outputmode"     ]
  state[ "loginformation"  ] = config[ "Parker" ][ "loginformation" ]
  state[ "processes"       ] = config[ "Parker" ][ "processes"      ]
  state[ "waittime"        ] = config[ "Parker" ][ "waittime"       ]
  state[ "bruteforce"      ] = config[ "Parker" ][ "bruteforce"     ]

  state[ "magicNumbers"    ] = magicNumbers
  state[ "magicRanges"     ] = magicRanges

  state[ "currentNumber"   ] = -1   # current magic number too processes
  state[ "currentRange"    ] = -1   # current range too processes
  state[ "currentCntRange" ] = -1   # current number in the current range

  state[ "currprocs"       ] = None # list of all the processes

  state[ "statefilename"   ] = os.path.join( config[ "Parker" ][ "datadirectory"  ], "state_main.json" )

  # already existing state preferred
  newState = StateRead( state, config )
  if newState != None:
    # change configuration with new state
    state = newState

    config[ "Parker" ][ "power"          ] = state[ "power"          ]
    config[ "Parker" ][ "outputmode"     ] = state[ "outputmode"     ]
    config[ "Parker" ][ "loginformation" ] = state[ "loginformation" ]
    config[ "Parker" ][ "processes"      ] = state[ "processes"      ]
    config[ "Parker" ][ "waittime"       ] = state[ "waittime"       ]
    config[ "Parker" ][ "bruteforce"     ] = state[ "bruteforce"     ]

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
  iRangeWalk  = 0

  def _writeCurrentState():
    if state == None:
      return

    # list of current processes
    arrCurr = []
    for checkProc in procArr:
      if checkProc == None:
        continue
      arrCurr.append( checkProc[ "number"] )

    state[ "currentNumber"   ] = iCurrMagic   # current magic number too processes
    state[ "currentRange"    ] = iCurrRange   # current range too processes
    state[ "currentCntRange" ] = iRangeWalk   # current number in the current range
    state[ "currprocs"       ] = arrCurr

    StateWrite( state )

  try:
    if state != None and state[ "currprocs" ] != None:
      # restart current processes
      for number in state[ "currprocs" ]:
        while StartThread( number, nrProcesses, config, procArr ) == False:
          _writeCurrentState()
          time.sleep( 3 )

    iCurrMagic = 0
    iCurrRange = 0
    iRangeWalk = 0

    # restore state if given
    if state != None:
      if state[ "currentNumber" ] >= 0:
        iCurrMagic = state[ "currentNumber" ]

      if state[ "currentRange" ] >= 0:
        iCurrRange = state[ "currentRange" ]

        if state[ "currentCntRange" ] > 0:
          iRangeWalk = state[ "currentCntRange" ]

    # walk all the given magic numbers
    while iCurrMagic < len( magicNumbers ):
      number = magicNumbers[ iCurrMagic ]
      while StartThread( number, nrProcesses, config, procArr ) == False:
        _writeCurrentState()
        print( f"Wait: {number}")
        time.sleep( 3 )
      iCurrMagic += 1

    # walk all the given ranges
    while iCurrRange < len( magicRanges ):
      elem     = magicRanges[ iCurrRange ]
      startNum = elem[ 'start' ]
      endNum   = elem[ 'end'   ] + 1 # inclusive
      while startNum % 3 != 0:
        startNum += 1

      iRangeWalk = max( startNum, iRangeWalk )
      while iRangeWalk < endNum:
        number = iRangeWalk
        while StartThread( number, nrProcesses, config, procArr ) == False:
          _writeCurrentState()
          print( f"Wait: {number}")
          time.sleep( waittime )
        iRangeWalk += 3

      iRangeWalk  = 0
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
    # print()
    # DisplayHelp()
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
      sys.exit()

  if len( globalMagicNumbers ) == 0 and len( globalMagicRanges ) == 0:
    DisplayHelp()
    sys.exit()

  print()
  print( "Settings" )
  print( f'Power              : {globalConfig[ "Parker" ][ "power"          ]}' )
  print( f'Output             : {globalConfig[ "Parker" ][ "outputmode"     ]}' )
  print( f'Extra logging      : {globalConfig[ "Parker" ][ "loginformation" ]}' )
  print( f'Output directory   : {globalConfig[ "Parker" ][ "datadirectory"  ]}' )
  print( f'Number of processes: {globalConfig[ "Parker" ][ "processes"      ]}' )
  print( f'Wait time          : {globalConfig[ "Parker" ][ "waittime"       ]} seconds' )
  print( f'State              : {globalConfig[ "Parker" ][ "state"          ]}' )
  print( f'Brute force        : {globalConfig[ "Parker" ][ "bruteforce"     ]}' )
  print()
  print( "To stop the program, press ctrl-c" )
  print()

  MainLoop( globalMagicNumbers, globalMagicRanges, globalConfig, globalState )


# =====================================
# main
# =====================================

if __name__ == '__main__': # this is needed otherwise multiprocessing don't work
  MainStart()

# the end
