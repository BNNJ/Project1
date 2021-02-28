# scraper

A simple webscraper to gather book data from http://books.toscrape.com

## setup

First clone the repo :
```bash
git clone https://github.com/BNNJ/Project2.git
```
or with gh CLI:
```bash
gh repo clone BNNJ/Project2
```

Then go into the directory and source the environment script:
Platform    | Shell             | Command to activate virtual environment
------------|-------------------|----------------------------------------
POSIX       | bash/zsh          | `$ source <venv>/bin/activate`
            | fish              | `$ source <venv>/bin/activate.fish`
            | csh/tcsh          | `$ source <venv>/bin/activate.csh`
            | PowerShell Core   | `$ <venv>/bin/Activate.ps1`
Windows     | cmd.exe           | `C:\> <venv>\Scripts\activate.bat`
            | PowerShell        | `PS C:\> <venv>\Scripts\Activate.ps1`

now install required modules:
```bash
pip install -r requirement.txt
```

## usage

```bash 
./scraper.py [-h] [-d | -q] [--nosave] [file]
```

## arguments

argument       | effect
---------------|-------
file           | the csv file to write to (default 'books.csv')
-h, --help     | show help message and exit
-d, --debug    | enable debug logs
-q, --quiet    | silence the info logs
--nosave       | don't save to csv
-i, --images   | save images

## examples

Save scraped books information to books.csv:
```bash
./scraper books_data.csv
```

Save images but not the text data, in quiet mode
```bash
./scraper --images --nosave -q
```