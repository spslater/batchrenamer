# Batch Rename Program
The Batch Rename Program allows for renaming of multiple files from the command line.

## Usage
```
usage: brp [-h] [-V] [-a [FILE ...]] filename [filename ...]

rename batches of files at one time

positional arguments:
  filename              list of files to rename

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -a [FILE ...], --auto [FILE ...]
                        automated file to run
```

## Operations
### help
```
help (h, ?) [-s] [commands ...]
   display help message
   positional arguments:
     commands     name to get specific info on
   optional arguments:
     -s, --small  display just the usage messages
```


### save
```
save (s) [-c]
   save files with current changes
   optional arguments:
     -c, --confirm  automatically confirm action
```


### quit
```
quit (q, exit) [-c]
   quit program, don't apply unsaved changes
   optional arguments:
     -c, --confirm  automatically confirm action
```


### write
```
write (w) [-c]
   write changes and quit program, same as save then quit
   optional arguments:
     -c, --confirm  automatically confirm action
```


### list
```
list (ls, l)
   lists current files being modified
```

Example:
```
filename.txt
begin_file_names_hello.csv

other name.txt
begin_other_names_hello.tsv
```

### history
```
history (hist, past) [--peak]
   print history of changes for all files
   optional arguments:
     --peak, -p  just show single file history
```

Example:
```
filename.txt
begin_file_names_hello.csv
   5  filename.txt
   4  filename.csv
   3  file_name.csv
   2  file_names.csv
   1  file_names_hello.csv
```


### undo
```
undo (u) [number]
   undo last change made
   positional arguments:
     number  number of changes to undo
```

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


### reset
```
reset (over, o) [-c]
   reset changes to original inputs, no undoing
   optional arguments:
     -c, --confirm  automatically confirm action
```


### automate
```
automate (a, auto) [filenames ...]
   automate commands in order to speed up repetative tasks
   positional arguments:
     filenames
```

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


### replace
```
replace (r, re, reg, regex) [find] [replace]
   find and replace based on a regex
   positional arguments:
     find     pattern to find
     replace  pattern to insert
```


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


### append
```
append (ap) [-f FILENAMES [FILENAMES ...]] [-p PADDING] [find] [append]
   pattern and value to append to each file that matches,can be automated with a file
   positional arguments:
     find                  regex pattern to match against
     append                value to append to filename
   optional arguments:
     -f FILENAMES [FILENAMES ...], --filenames FILENAMES [FILENAMES ...]
                           file to load patterns from
     -p PADDING, --padding PADDING
                           string to insert between the end of the filename and the value being appended
```

Example files:
```
0101 Pilot
0102 "Cool Episode"
```
```
s01e01 Pilot
s02e02 "Different show"
```

Would make following changes:
```
Show - 0101 -.mp4
Show - 0101 - Pilot.mp4

Show - 0102 -.mp4
Show - 0102 - Cool Episdoe.mp4

Video - s01e01 -.mp4
Video - s01e01 - Pilot.mp4

Video - s02e02 -.mp4
Video - s02e02 - Different show.mp4
```


### prepend
```
prepend (p, pre) [-f FILENAMES [FILENAMES ...]] [-p PADDING] [find] [prepend]
   tsv with pattern and value to prepend to each file that matches
   positional arguments:
     find                  regex pattern to match against
     prepend               value to prepend to filename
   optional arguments:
     -f FILENAMES [FILENAMES ...], --filenames FILENAMES [FILENAMES ...]
                           file to load patterns from
     -p PADDING, --padding PADDING
                           string to insert between the value being prepended and the begining of the filename
```

Example file:
```
"Foo Song" 01
"Bar Song" 02
```
Would make following changes:
```
Foo Song.mp3
01 Foo Song.mp3

Bar Song.flac
02 Bar Song.flac
```


### insert
```
insert (i, in) [-c] [value] [index]
   insert string, positive from begining, negative from ending
   positional arguments:
     value          value to insert
     index          index (starting from 0) to insert at, negative numbers will insert counting from the end
   optional arguments:
     -c, --confirm  automatically confirm action
```

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


### case
```
case (c) [styles ...]
   change the case (title, upper, lower) of files
   positional arguments:
     styles  type of case style (lower, upper, title, camel, kebab, ect) to switch to
```

Example:
```
> list
file name.txt
other_file.txt
third file.txt
> case upper
FILE NAME.txt
OTHER_FILE.txt
THIRD FILE.txt
> case kebab
FILE-NAME.txt
OTHER_FILE.txt
THIRD-FILE.txt
```


### extension
```
extension (x, ext) [ext] [pattern]
   change the extension on all files or files that match pattern
   positional arguments:
     ext      new extension to change to
     pattern  pattern to match against old extensions
```

Examples:
```
filename.txt
> ext csv txt
filename.csv
> ext tsv txt
filename.csv
```

## Links
* [PyPi Project](https://pypi.org/project/batchrenamer)
* [Github](https://github.com/spslater/batchrenamer)

## Contributing
Help is greatly appreciated. First check if there are any issues open that relate to what you want
to help with. Also feel free to make a pull request with changes / fixes you make.

## License
[MIT License](https://opensource.org/licenses/MIT)
