# BQ REPL
REPL for BigQuery

![](screenshots/screenshot01.png)

![](screenshots/screenshot02.png)

![](screenshots/screenshot03.png)

# Commands
```
Commands:
\d, \datasets [PROJECT]               list datasets in current project (or another project)
\p, \projects [PROJECT]               list projects (will switch projects when provided as parameter)
\t, \tables [PROJECT.]DATASET         list tables in a dataset
\c, \columns [PROJECT.]DATASET.TABLE  list columns in a table
\x, \expanded                         toggle expanded view on/off

Options:
\set VARIABLE VALUE                   set option:
Available options:
    - project PROJECT_ID              set current project to PROJECT_ID
    - maxrows 100                     maximum rows displayed (default=100)
    - maxwidth 50                     maxium column width in non-expanded view (default=50)
    - max_expanded_width 100          maximum column width in expanded view (default=100)
    - expanded False                  expanded view (default=False)
    - format_integer ,d               integer display format (default=",d")
    - format_float ,.4f               float display format (default=",.4f")
```

# Command line arguments
```
$ bqrepl --help
Usage: bqrepl [OPTIONS]

  REPL for BigQuery

Options:
  -c, --credentials-file TEXT  path to credentials .json
  -p, --project TEXT           Use specific project instead of inferring from
                               credentials

  --help                       Show this message and exit.
```

# Installation
```bash
$ pip install bqrepl
```

## Dependencies
Python dependencies:
- google-cloud-bigquery
- pytz
- click
- prompt-toolkit
- logzero

# Tasks
Stuff to implement, in no particular order:

- [ ] Essentials
    - [x] nice looking results
    - [x] query execution
    - [x] toggle numbers formatting on/off
    - [x] string truncation (aka max column width)
    - [x] expanded output
    - [x] switch GCP projects during session
    - [ ] nicer looking errors/warnings
    - [ ] multiline queries
    - [ ] multiline results
    - [ ] better authentication
    - [ ] persist query history in local database
    - [ ] query result pagination or whatever is required to keep # results sane

- [ ] Command line arguments:
    - [x] service-account
    - [x] project
    - [ ] execute SQL from command line

- [ ] code completion:
    - [ ] BQ-specific SQL syntax
    - [ ] projects/datasets/tables/columns available in the query context
    - [ ] BQ commands

- [ ] BQ commands
    - [x] list projects
    - [x] list datasets
    - [x] list tables
    - [x] list datasets in a specific project
    - [x] list columns
    - [ ] show info about dataset/table/view/model
    - [ ] filter list
    - [ ] copy tables
    - [ ] extract (table to bucket)
    - [ ] insert rows to table (from local file)
    - [ ] create dataset
    - [ ] create table

- [ ] Extras
    - [x] colour-coding nulls
    - [ ] colour-coding floats/integers/strings/dates (do I even need this?)
    - [ ] recall cached query results instead of running them again
    - [ ] view results in a horizontally scrollable table (like pgcli)
    - [ ] project/dataset tree
    - [ ] use tabs for query results?
    - [ ] async queries
    - [ ] clear screen
    - [ ] integrate ptpython?
