# scraper

A simple webscraper to gather book data from http://books.toscrape.com

## setup

First clone the repo :
```console
foo@bar:~$ git clone https://github.com/BNNJ/Project2.git
```
or with gh CLI:
```console
foo@bar:~$ gh repo clone BNNJ/Project2
```

Then go into the directory and source the environment script:
(for Linux/mac)
```console
foo@bar:~$ cd Project2
foo@bar:~$ source bin/activate
```
(for windows)
```console
env\Scripts\activate.bat
````

now install required modules:
```console
foo@bar:~$ pip install -r requirement.txt
```

## usage

```console 
foo@bar:~$ ./scraper.py [-h] [-d | -q] [--nosave] [file]
```

## arguments

| argument      | effect |
|-|-|
|file           | the csv file to write to (default 'books.csv') |
|-h, --help     | show help message and exit |
|-d, --debug    | enable debug logs |
|-q, --quiet    | silence the info logs |
|--nosave       | don't save to csv |
|-i, --images   | save images |
