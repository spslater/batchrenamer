# Batch Rename Program
The Batch Rename Program allows for renaming of multiple files from the command line.

## Usage
```
usage: brp [-h] [-a [FILE ...]] filename [filename ...]

positional arguments:
  filename              list of files to rename

optional arguments:
  -h, --help            show this help message and exit
  -a [FILE ...], --auto [FILE ...]
                        automated file to run (default: None)
```

## Operations
### automate
Command: `automate`, `a`, `auto`  
Usage: `auto [filename ...]`  
Takes a file with commands on each line and run them in sequence.

Example file:
```
list
replace foo bar
insert "foo - " 0
write
```
Any commands that are missing arguments (like only passing in `find` and not `replace`
to the `replace` command) will ask for manual user input. The `-c` command does not need
to be passed if all other arguments are passed as well.

### episodes
Command: `episodes`, `e`, `ep`  
Usage: `ep [filename ...]`  
Load file with one episode number and episode title per line.
Episode sould match end of files being matched, accepted filename patterns:
```
Show name - {episode} -
Show name - {episode}
```
Multiple files can be specified to load names from.

Example files:
```
0101 Pilot
0102 Cool Episode
```
```
s01e01 Pilot
s02e02 Different show
```

### extension
Command: `extension`, `x`, `ext`
Usage: `ext [new] [pattern]`
Change the file extensions of the files, a pattern can be provided to match against filename or current extension.

Examples:
```
filename.txt
> ext csv txt
filename.csv
> ext tsv txt
filename.csv
```

### help
Command: `help`, `h`, `?`  
Usage: `help`  
Print the help message to the console

### insert
Command: `insert`, `i`  
Usage: `insert [value] [index]`
Insert given value at index (0 being the begining of the word). Negative values count from the end of the word.
Numbers that are longer than the word get added to the end or beginning of the word (positive or negative value respectivly).

Examples:
```
filename.txt
> insert _ 4
file_name.txt
> insert s -1
file_names.txt
> insert _hello 100
file_names_hello.txt
> insert begin_ -100
begin_file_names_hello.txt
```

### list
Command: `list`, `l`  
Usage: `list`
List all files and the current state of their changes

Example:
```
filename.txt
begin_file_names_hello.csv

other name.txt
begin_other_names_hello.tsv
```

### quit
Command: `quit`, `q`  
Usage: `quit [-c|--confirm]`
Exit the program without saving any changes

### replace
Command: `replace`, `r`, `re`  
Usage: `re [find] [replace]`
Find and replace given values in files that match

Examples:
```
filename.txt
other_file.txt
third file.txt
> re _ -
filename.txt
other-file.txt
third file.txt
> re "third " "first~"
filename.txt
other-file.txt
first~file.txt
```

### save
Command: `save`, `s`  
Usage: `save [-c|--confirm]`
Rename files with their current changes

### tracks
Command: `tracks`, `t`, `tr`  
Usage: `tr [filename ...]`  
Load file with one track number and track title per line. Example file:
```
01 Foo Song
02 Bar Song
```
Would make following changes:
```
Foo Song.mp3
01 Foo Song.mp3

Bar Song.flac
02 Bar Song.flac
```

### undo
Command: `undo`, `u`  
Usage: `undo [number]`
Reverts last N changes (1 if none provided when asked). Trying to undo when no changes are present doesn't change anything.
Examples:
```
filename.txt
> insert _ 4
file_name.txt
> re file song
song_name.txt
> ext txt csv
song_name.csv
> undo
song_name.txt
> undo 2
filename.txt
> undo
filename.txt
```

### write
Command: `write`, `w`  
Usage: `write [-c|--confirm]`  
Rename files and exit program

## Links
* [PyPi Project](https://pypi.org/project/batchrenamer)
* [Github](https://github.com/spslater/batchrenamer)

## Contributing
Help is greatly appreciated. First check if there are any issues open that relate to what you want
to help with. Also feel free to make a pull request with changes / fixes you make.

## License
[MIT License](https://opensource.org/licenses/MIT)