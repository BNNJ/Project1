# scraper

A simple webscraper to gather book data from http://books.toscrape.com

## setup

First clone the repo :
```console
git clone https://github.com/BNNJ/Project2.git
```
or with gh CLI:
```console
gh repo clone BNNJ/Project2
```

Then go into the directory and source the environment script:
```console
cd Project2
source bin/activate
```

```console
env\Scripts\activate.bat
````

now install required modules:
```console
pip install -r requirement.txt
```

## usage

```console 
foo@bar:~$ ./scraper.py [-h] [-d | -q] [--nosave] [file]
```

## arguments
| argument      | effect |
|-|-|
|file           | the csv file to write to (default 'books.csv') |
|-h, --help     | show this help message and exit |
|-d, --debug    | enables debug logs |
|-q, --quiet    | silences the info logs |
|--nosave       | don't save to csv |

## TODO

images