# scraper

A simple webscraper to gather book data from http://books.toscrape.com

## setup

First clone the repo :
```console
git clone https://github.com/BNNJ/Project2.git
```
or with gh CLI:
```
gh repo clone BNNJ/Project2
```

Then go into the directory and source the environment script:
```
cd Project2
source bin/activate
```

now install required modules:
```
pip install -r requirement.txt
```

## usage

```console 
foo@bar:~$ ./scraper.py [-h] [-d | -q] [--nosave] [file]
```

## arguments
| argument      | effect |
|-|-|
|file           | The csv file to write to (default 'books.csv') |
|-h, --help     | show this help message and exit |
|-d, --debug    | Enables debug logs |
|-q, --quiet    | Silences the info logs |
|--nosave       | Don't save to csv |

## TODO

huh