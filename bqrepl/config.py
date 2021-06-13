default_settings = {
    "expanded": False,
    "format_integer": ",d",
    "format_float": ",.4f",
    "maxrows": 100,
    "maxwidth": 50,
    "max_expanded_width": 100,
}

help_commands = [
    (
        r"\?",
        "Print this stuff"
    ),
    (
        r"\d, \datasets [PROJECT]",
        "List datasets in current project (or another project)"
    ),
    (
        r"\p, \projects [PROJECT]",
        "List projects. Will switch projects when provided as parameter"
    ),
    (
        r"\t, \tables [PROJECT.]DATASET",
        "List tables in a dataset"
    ),
    (
        r"\c, \columns [PROJECT.]DATASET.TABLE",
        "List columns in a table"
    ),
    (
        r"\x, \expanded",
        "Toggle expanded view on/off. Shorthand for \\set expanded BOOL"
    ),
    (
        r"\clear, clear",
        "Clear screen"
    ),
]

help_options = [
    (
        r"\set project PROJECT_ID",
        "Set current project to PROJECT_ID"
    ),
    (
        r"\set maxrows INT",
        "Maximum rows displayed (default=100)"
    ),
    (
        r"\set maxwidth INT",
        "Maximum column width in non-expanded view (default=50)"
    ),
    (
        r"\set max_expanded_width INT",
        "Maximum column width in expanded view (default=100)"
    ),
    (
        r"\set expanded BOOL",
        "Expanded view (default=False)"
    ),
    (
        r"\set format_integer STR",
        "Integer display format (default=',d')"
    ),
    (
        r"\set format_float STR",
        "Float display format (default=',.4f')"
    ),
]
