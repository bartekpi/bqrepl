from prompt_toolkit.formatted_text import to_formatted_text

from bqrepl.main import BQREPL


def test_output_values():
    bqrepl = BQREPL()
    data = [
        {"col1": 1000, "col2": "a", "col3longname": 1023.2},
        {"col1": 900, "col2": "b", "col3longname": 123.1},
        {
            "col1": None,
            "col2": "this is a long column that will get truncated",
            "col3longname": 1,
        },
    ]

    columns = [("col1", "INTEGER"), ("col2", "STRING"), ("col3longname", "FLOAT")]

    widths = {
        "columns": {"col1": 7, "col2": 6, "col3longname": 12},
        "values": {"col1": 4, "col2": 4, "col3longname": 4},
    }
    total_rows = 2
    settings = {
        "format_integer": ",d",
        "format_float": ",.2f",
        "maxwidth": 10,
        "maxrows": 100,
    }
    result, widths = bqrepl.format_values(data, columns, widths, total_rows, settings)
    expected_result = [
        ["1,000", "a", "1,023.20"],
        ["900", "b", "123.10"],
        [None, "this is a ...", "1.00"],
    ]
    expected_widths = {
        "columns": {"col1": 7, "col2": 6, "col3longname": 12},
        "values": {"col1": 5, "col2": 13, "col3longname": 8},
    }

    assert result == expected_result
    assert widths == expected_widths


def test_output_formatted():
    bqrepl = BQREPL()
    settings = {
        "format_integer": ",d",
        "format_float": ",.2f",
        "maxwidth": 10,
        "maxrows": 100,
    }
    values = [
        ["1,000", "a", "1,023.20"],
        ["900", "b", "123.10"],
        [None, "this is a ...", "1.00"],
    ]

    columns = [("col1", "INTEGER"), ("col2", "STRING"), ("col3longname", "FLOAT")]

    widths = {
        "columns": {"col1": 7, "col2": 6, "col3longname": 12},
        "values": {"col1": 5, "col2": 13, "col3longname": 8},
    }

    formatted_rows = bqrepl.format_rows(values, columns, widths, settings)
    fr = [to_formatted_text(x) for x in formatted_rows]
    result = ["".join(map(lambda x: x[1], f)) for f in fr]

    expected_result = [
        " row | col1    | col2          | col3longname |",
        "     | INTEGER | STRING        | FLOAT        |",
        "-----|---------+---------------+--------------|",
        "   0 |   1,000 | a             |     1,023.20 |",
        "   1 |     900 | b             |       123.10 |",
        "   2 |    null | this is a ... |         1.00 |",
        "-----------------------------------------------",
    ]

    assert result == expected_result


def test_formmated_output_expanded():
    bqrepl = BQREPL()
    settings = {
        "format_integer": ",d",
        "format_float": ",.2f",
        "maxwidth": 25,
        "maxrows": 100,
    }
    values = [
        ["1,000", "a", "1,023.20"],
        ["900", "b", "123.10"],
        [None, "this is a longer output!", "1.00"],
    ]

    columns = [("col1", "INTEGER"), ("col2", "STRING"), ("col3longname", "FLOAT")]

    widths = {
        "columns": {"col1": 7, "col2": 6, "col3longname": 12},
        "values": {"col1": 5, "col2": 24, "col3longname": 8},
    }

    formatted_rows = bqrepl.format_rows_expanded(values, columns, widths, settings)
    fr = [to_formatted_text(x) for x in formatted_rows]
    result = ["".join(map(lambda x: x[1], f)) for f in fr]

    expected_result = [
        "-[ row 0 ]-----------------------------",
        "col1         | 1,000                   ",
        "col2         | a                       ",
        "col3longname | 1,023.20                ",
        "-[ row 1 ]-----------------------------",
        "col1         | 900                     ",
        "col2         | b                       ",
        "col3longname | 123.10                  ",
        "-[ row 2 ]-----------------------------",
        "col1         | null                    ",
        "col2         | this is a longer output!",
        "col3longname | 1.00                    ",
    ]

    assert result == expected_result
