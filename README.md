# Python RSS reader

*RSS reader is a command-line utility which receives RSS URL and prints the results in a human-readable
format.*


### Installation
from project root folder run:

```bash
pip install -e .
```


### Usage:
```bash
rss_reader.py "https://news.yahoo.com/rss/" --limit 5
```

or

```bash
python rss_reader.py "https://news.yahoo.com/rss/" --json --limit 11
```


### Output:
```
Date:   <publication date>
Title:  <publication title>
Link:   <publication link>
        
        <contents>
Links:
[1]:    <link 1>
[2]:    <link 2>
...
```

### Utility provides the following interface: 
```
$ rss_reader.py [-h] [–version] [–json] [–verbose] [--limit LIMIT] source
```
```
positional arguments:
  source           RSS URL

optional arguments:
  -h, --help       Show this help message and exit
  --version        Print version info
  --json           Print result as JSON in stdout
  --verbose        Outputs verbose status messages
  --limit [LIMIT]  Limit news topics if this parameter is provided
```