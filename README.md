# Batch Rename CLI
- Hello World

## Operations
### u, undo
Undo last regex applied

### k, keep
Keep regex just applied

### s, save
Save files with current regex

### q, quit
Quit program

### h, help
Print help message

### r, regex
Find and replace based on a regex

### l, list
Lists current files being modified

### e, ext
Change the file extensions

### To Add
#### i, insert
Inserts string at index

#### n, names
Appends episode names from list in file (tsv?)
	Open file, read line by line, and search thru Files list for regex match on episode

## Data Structure
### Action
``` json
{
	"names": ["r", "regex"]
}
```