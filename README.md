# Parker Square

A Python program to find a magic square of squares

## Installation
Download or make a git clone of parkersquare
```
git clone https://github.com/SWVandenEnden/parkersquare.git
```

## Usage
```
python parkersquare.py <number>
```
This start the program and try to find a magic square for the given number

### Command line
```
python parkersquare.py <number> <number> <number>
```
Find the magic squares of the given numbers

```
python parkersquare.py <start number-end number> <start number-end number>
```
Find the magic squares in the given ranges

### Command line
| Option | Description |
| ------ | ----------- |
|-h|Display the command line help|
|-p <number>|Power of the numbers in the square. The default is 2. By using -p 1 you will get a normal magic square|
|-d <directory>|Directory to place the output, default is current working directory/'parker'|
|-o <outputmode>|Output mode, f=file, s=screen, b=both. Screen is the default|
|-l <True/False>|Extra log information, default is true|
|-c <filename>|Configuration file|
|-n <number>|Number of concurrent processes. 1 is the default. By 'auto' the number of CPU's minus 2 will be used. Only usable by large numbers because of the overhead of spanning a process.|
|-w <number>|Number of seconds to wait before to try to span a new process, default is 3 seconds|
|-s <True/False>|Load and save the state of process. Default is false. By load the process will continue where is was stopped.|
|-b <True/False>|Use brute force, check all the combinations and no optimizations|

### Output files
If the option '-o f' or '-o b' is used then in the output directory (-d) the following files will appear:
- square_&lt;number&gt;.txt : A magic square is found
- parker_&lt;number&gt;.txt : A parker square is found
- state_&lt;number&gt;.json / state_main.json: The state of the process if option '-s true' is used


### Examples:
```
python parkersquare.py 21609
python parkersquare.py 34344 -p 1 -l true -o s
python parkersquare.py 100-100000 -p 2 -l false -o b
python parkersquare.py 100000000000-200000000000 -p 2 -l false -o b -n auto -w 10 -s true
python parkersquare.py 194481 -b true
```