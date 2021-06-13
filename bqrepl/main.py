import os
import sys
from copy import deepcopy
from datetime import datetime
from collections import namedtuple

import pytz
import click
from logzero import logger
from google.oauth2 import service_account
from google.cloud import bigquery

from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.formatted_text import merge_formatted_text
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import clear, prompt
from prompt_toolkit.completion import WordCompleter

from bqrepl.completer import BQCompleter
from bqrepl.lexer import BQLexer
from bqrepl.config import help_commands, help_options, default_settings

style = Style.from_dict(
    {
        "completion-menu.completion": "bg:#008888 #ffffff",
        "completion-menu.completion.current": "bg:#00aaaa #000000",
        "scrollbar.background": "bg:#88aaaa",
        "scrollbar.button": "bg:#222222",
    }
)


class BQREPL:
    def __init__(self, credentials_file=None, project=None):

        self.settings = default_settings
        self.settings["project"] = project
        self.credentials_file = credentials_file
        self.session = None
        self.prompt = None
        self.client = None
        self.credentials = None

    def connect_client(self):
        """Connects to BQ"""
        if not self.credentials:
            self.set_credentials()

        client = bigquery.Client(
            project=self.settings.get("project"), credentials=self.credentials
        )
        self.client = client
        self.prompt = "[{}] ~> ".format(self.settings.get("project", ""))

    def start_session(self):
        sql_completer = BQCompleter()

        self.session = PromptSession(
            lexer=PygmentsLexer(BQLexer),
            completer=sql_completer,
            style=style
        )

    def set_credentials(self):
        """Retrieves credentials"""
        if not (self.credentials_file or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")):
            import pydata_google_auth
            self.credentials = pydata_google_auth.get_user_credentials(
                ["https://www.googleapis.com/auth/bigquery"]
            )
            if not self.settings.get("project"):
                available_projects = []
                while True:
                    project = prompt(
                        "Please provide project ID: ",
                        completer=WordCompleter(available_projects)
                        )
                    client_test = bigquery.Client(
                        project=project, credentials=self.credentials
                    )
                    available_projects = [
                        x.project_id for x in client_test.list_projects()
                    ]
                    if project not in available_projects:
                        message = (
                            "<ansibrightred>"
                            "Incorrect project ID provided."
                            "</ansibrightred>"
                            "\nAvailable projects:"
                        )
                        for i, p in enumerate(sorted(available_projects)):
                            message += (
                                f"\n{i+1}) <ansibrightblack>{p}</ansibrightblack>")
                        print_formatted_text(HTML(message))
                    else:
                        break

                self.set_project(project)
        else:
            if self.credentials_file:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_file

            self.credentials_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

            try:
                self.credentials = (
                    service_account.Credentials.from_service_account_file(
                        self.credentials_file,
                        scopes=["https://www.googleapis.com/auth/bigquery"],
                    ))
            except ValueError as e:
                logger.error(e)
                sys.exit(1)

            project = self.credentials.project_id

            if not self.settings.get("project"):
                self.set_project(project)

    def set_project(self, project):
        """Switches acitve project"""

        self.settings["project"] = project
        self.connect_client()

    def list_projects(self):
        """Lists all projects this service accounts has access to"""

        try:
            client_results = list(self.client.list_projects())
        except Exception as e:
            logger.error("Something went wrong fetching projects")
            for err_dict in e.errors:
                logger.error(err_dict)
            return

        Schema = namedtuple("Schema", ["name", "field_type"])

        schema = [Schema("project_id", "STRING"), Schema("friendly_name", "STRING")]
        data = [
            {k.name: x.__getattribute__(k.name) for k in schema} for x in client_results
        ]

        self.show_results(data, schema)

    def list_datasets(self, project=None):
        """Lists all datasets in the project."""

        try:
            client_results = list(self.client.list_datasets(project=project))
        except Exception as e:
            logger.error("Something went wrong fetching datasets")
            for err_dict in e.errors:
                logger.error(err_dict)
            return

        Schema = namedtuple("Schema", ["name", "field_type"])

        schema = [
            Schema("project", "STRING"),
            Schema("dataset_id", "STRING"),
            Schema("location", "STRING"),
            Schema("friendly_name", "STRING"),
        ]

        data = [
            dict(
                project=x.project,
                dataset_id=x.dataset_id,
                location=x._properties.get("location"),
                friendly_name=x.friendly_name,
            )
            for x in client_results
        ]

        self.show_results(data, schema)

    def list_tables(self, dataset):
        """Lists all tables in dataset"""

        if len(dataset.split(".")) > 2:
            logger.error("Too many parts in dataset reference. Expecting max 2")
            return
        try:
            client_results = list(self.client.list_tables(dataset))
        except Exception as e:
            logger.error("Something went wrong fetching tables")
            for err_dict in e.errors:
                logger.error(err_dict)
            return

        Schema = namedtuple("Schema", ["name", "field_type"])

        schema = [
            Schema("project", "STRING"),
            Schema("dataset_id", "STRING"),
            Schema("table_id", "STRING"),
            Schema("type", "STRING"),
            Schema("created", "DATETIME"),
            Schema("expires", "DATETIME"),
            Schema("friendly_name", "STRING"),
            Schema("labels", "STRING"),
        ]

        data = [
            dict(
                type=x._properties.get("type"),
                **{
                    k.name: x.__getattribute__(k.name)
                    for k in schema
                    if k.name != "type"
                },
            )
            for x in client_results
        ]

        self.show_results(data, schema)

    def list_columns(self, table):
        """List all columns in table"""

        try:
            client_results = self.client.get_table(table)
        except Exception as e:
            logger.error("Something went wrong fetching table")
            for err_dict in e.args:
                logger.error(err_dict)
            return

        Schema = namedtuple("Schema", ["name", "field_type"])

        schema = [
            Schema("project", "STRING"),
            Schema("dataset_id", "STRING"),
            Schema("table_id", "STRING"),
            Schema("name", "STRING"),
            Schema("field_type", "STRING"),
            Schema("mode", "STRING"),
            Schema("description", "STRING"),
            Schema("fields", "STRING"),
        ]

        data = [
            dict(
                project=client_results.project,
                dataset_id=client_results.dataset_id,
                table_id=client_results.table_id,
                name=t.name,
                field_type=t.field_type,
                mode=t.mode,
                description=t.description,
                fields=t.fields,
            )
            for t in client_results.schema
        ]

        self.show_results(data, schema)

    def print_help(self):
        Schema = namedtuple("Schema", ["name", "field_type"])

        schema = [
            Schema("command", "STRING"),
            Schema("description", "STRING"),
        ]

        data = [
            {"command": c, "description": d}
            for c, d in help_commands + help_options
        ]

        self.show_results(data, schema)

    def format_values(self, data, columns, widths, total_rows, settings):
        """Prepares formatted results"""

        # column widths will get updated as values are formatted
        widths_ = deepcopy(widths)

        values = []
        for row_i, row in enumerate(data):
            row_values = []
            for col_name, col_type in columns:
                v = row.get(col_name)
                if v is None:
                    formatted_value = None
                else:
                    if col_type == "INTEGER":
                        fmt = settings.get("format_integer")
                        formatted_value = f"{v:{fmt}}"
                    elif col_type == "FLOAT":
                        fmt = settings.get("format_float")
                        formatted_value = f"{v:{fmt}}"
                    else:
                        formatted_value = str(v)[: settings.get("maxwidth")]
                        if len(str(v)) > settings.get("maxwidth"):
                            formatted_value += "..."
                if formatted_value is None:
                    widths_["values"][col_name] = max(
                        4, widths_.get("values").get(col_name)
                    )
                elif len(formatted_value) > widths_.get("values").get(col_name):
                    widths_["values"][col_name] = len(formatted_value)
                row_values.append(formatted_value)
            values.append(row_values)
            if (row_i == settings.get("maxrows") - 1) & (row_i != total_rows - 1):
                break

        return values, widths_

    def format_rows(self, values, columns, widths, settings):
        """Prepare formatted rows, ready for printing"""

        formatted_rows = []

        formatted_row = " <b><ansiblue>row</ansiblue></b> |"
        formatted_row += "|".join(
            [
                " "
                + f"<b><ansigreen>{x}</ansigreen></b>"
                + " " * (max(widths["values"][x], widths["columns"][x]) - len(x) + 1)
                for x, y in columns
            ]
        )
        formatted_row += "|"
        formatted_rows.append(HTML(formatted_row))

        formatted_row = HTML("     |")
        for x, y in columns:
            formatted_value = HTML(" <ansicyan>{}</ansicyan>{}|").format(
                y, " " * (max(widths["values"][x], widths["columns"][x]) - len(y) + 1)
            )
            formatted_row = merge_formatted_text([formatted_row, formatted_value])
        formatted_rows.append(formatted_row)
        separator_row = "-----|"
        separator_row += "+".join(
            [
                "-" * (max(widths["values"][x], widths["columns"][x]) + 2)
                for x, y in columns
            ]
        )
        separator_row += "|"

        final_row = "-" * len(separator_row)

        for i, row in enumerate(values):
            if i == 0:
                formatted_rows.append(separator_row)
            formatted_row = HTML(" <ansiblue>{}</ansiblue>").format(f"{i:3,d}")
            for value, (col_name, col_type) in zip(row, columns):
                formatted_row = merge_formatted_text([formatted_row, HTML(" |" + " ")])
                if value is not None:
                    formatted_value = HTML("{}").format(value)
                    try:
                        len_value = len(value)
                    except TypeError:
                        len_value = 0
                else:
                    formatted_value = HTML("<ansibrightred>null</ansibrightred>")
                    len_value = 4
                whitespace = " " * (
                    max(widths["columns"][col_name], widths["values"][col_name])
                    - len_value
                )
                if col_type in ("INTEGER", "FLOAT"):
                    formatted_row = merge_formatted_text(
                        [formatted_row, HTML(whitespace), formatted_value]
                    )
                else:
                    formatted_row = merge_formatted_text(
                        [formatted_row, formatted_value, HTML(whitespace)]
                    )
            formatted_row = merge_formatted_text([formatted_row, HTML(" |")])
            formatted_rows.append(formatted_row)

        formatted_rows.append(final_row)

        return formatted_rows

    def format_rows_expanded(self, values, columns, widths, settings):
        """Prepare formatted rows in extended view, ready for printing"""

        formatted_rows = []

        row_delimiter_template = "-[ <b><ansiblue>row {}</ansiblue></b> ]-"
        max_col_name_width = max([len(x[0]) for x in columns])
        max_col_value_width = min(
            self.settings["max_expanded_width"], max(4, max(widths["values"].values()))
        )
        max_table_width = max_col_name_width + max_col_value_width + 3
        for i, row in enumerate(values):
            formatted_row = HTML(row_delimiter_template).format(f"{i:,d}")
            # calculate length of this header but substract what's inside tags
            row_len = sum([len(x[1]) for x in formatted_row.formatted_text])
            if max_table_width >= row_len:
                fills = max_table_width - row_len
                formatted_row = merge_formatted_text([formatted_row, HTML("-" * fills)])

            formatted_rows.append(formatted_row)

            for value, (col_name, col_type) in zip(row, columns):
                formatted_row = HTML("<ansibrightgreen>{}</ansibrightgreen>").format(
                    f"{col_name:{max_col_name_width}}"
                )
                if value is None:
                    value = HTML(
                        "<ansibrightred>null</ansibrightred>"
                        + " " * (max_col_value_width - 4)
                    )
                else:
                    value = HTML("{}").format(f"{value:{max_col_value_width}}")
                formatted_row = merge_formatted_text(
                    [formatted_row, HTML(" | "), value]
                )
                formatted_rows.append(formatted_row)

        return formatted_rows

    def show_results(self, data, schema, t0=None):
        """Prints formatted resutls"""

        columns = [(x.name, x.field_type) for x in schema]
        widths = {
            "columns": {x.name: max(len(x.field_type), len(x.name)) for x in schema},
            "values": {x.name: 4 for x in schema},
        }
        try:
            total_rows = data.total_rows
        except AttributeError:
            total_rows = len(data)

        values, widths = self.format_values(
            data, columns, widths, total_rows, self.settings
        )

        if not self.settings["expanded"]:
            formatted_rows = self.format_rows(values, columns, widths, self.settings)
        else:
            formatted_rows = self.format_rows_expanded(
                values, columns, widths, self.settings
            )

        for formatted_row in formatted_rows:
            print_formatted_text(formatted_row)

        footer_row = (
            "<ansibrightblack>"
            f"{len(values):,d}/{total_rows:,d}"
            "</ansibrightblack> results."
        )
        if t0:
            dt = datetime.now(tz=pytz.utc) - t0
            footer_row += f" Time: <ansibrightblack>{dt}</ansibrightblack>"
        print_formatted_text(HTML(footer_row))

    def execute_command(self, text):
        """Execute BQ command"""
        text = text.strip()

        if text == "\\?":
            self.print_help()

        if text.split(" ")[0] in ("\\d", "\\datasets"):
            if len(text.split(" ")) > 1:
                project = text.split(" ")[1]
            else:
                project = self.settings.get("project")

            self.list_datasets(project=project)

        if text.split(" ")[0] in ("\\p", "\\projects"):
            if len(text.split(" ")) > 1:
                project = text.split(" ")[1]
                message = (
                    "Switched project to <ansibrightblack>{}</ansibrightblack>".format(
                        project
                    )
                )
                self.set_project(project)
                print_formatted_text(HTML(message))
            else:
                self.list_projects()

        if text.split(" ")[0] in ("\\t", "\\tables"):
            try:
                dataset = text.split(" ")[1]
            except IndexError:
                print_formatted_text(HTML(r"<ansired>Missing dataset</ansired>"))
                return

            self.list_tables(dataset)

        if text.split(" ")[0] in ("\\c", "\\columns"):
            try:
                table = text.split(" ")[1]
            except IndexError:
                print_formatted_text(HTML(r"<ansired>Missing table</ansired>"))
                return

            self.list_columns(table)

        if text in ("\\x", "\\expanded"):
            text = "\\set expanded {}".format(not self.settings.get("expanded"))

        if text.split(" ")[0] == "\\set":
            try:
                cmd, variable, value = text.split(" ")
            except ValueError:
                print_formatted_text(
                    HTML(
                        r"<ansired>Ugh, I expected something like "
                        r"'<i>\set variable value</i>'"
                        ", got something weird instead...</ansired>"
                    )
                )
                return
            if variable not in self.settings.keys():
                print_formatted_text(
                    HTML(
                        r"<ansired>Unknown parameter '<i>{}</i>'...</ansired>".format(
                            variable
                        )
                    )
                )
                return

            if variable.startswith("format_"):
                self.settings[variable] = value
            elif variable == "expanded":
                if value.lower() in ["y", "yes", "on", "true", "t", "1"]:
                    newval = True
                elif value.lower() in ["n", "no", "off", "false", "f", "-1", "0"]:
                    newval = False
                else:
                    print_formatted_text(
                        HTML(
                            r"<ansired>Unknown value '<i>{}</i>'...</ansired>".format(
                                value
                            )
                        )
                    )
                    return
                self.settings["expanded"] = newval
                message = (
                    "Toggled expanded view <ansibrightblack>"
                    "{}</ansibrightblack>".format("ON" if newval else "OFF")
                )
                print_formatted_text(HTML(message))
            elif variable == "project":
                message = (
                    "Switched project to <ansibrightblack>" f"{value}</ansibrightblack>"
                )
                self.set_project(value)
                print_formatted_text(HTML(message))
            else:
                self.settings[variable] = int(value)

    def execute_query(self, text):
        """Executes query"""

        query_job = self.client.query(text)
        if query_job.errors:
            for err_dict in query_job.errors:
                logger.error(err_dict)
            return

        result = query_job.result()
        schema = result.schema

        self.show_results(result, schema, t0=query_job.started)

    def run(self):
        """Waits for commands"""

        if not self.client:
            self.connect_client()

        if not self.session:
            self.start_session()

        while True:
            try:
                text = self.session.prompt(
                    self.prompt, auto_suggest=AutoSuggestFromHistory()
                    )
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

            if not text:
                continue
            if not text.strip():
                continue
            if text.strip().lower() in ["clear", "\\clear"]:
                clear()
                continue

            if text.startswith("\\"):
                self.execute_command(text)
            else:
                self.execute_query(text)

        print_formatted_text(HTML("<ansibrightblack><b>bai!</b></ansibrightblack>"))


def main(**kwargs):
    bqrepl = BQREPL(
        credentials_file=kwargs.get("credentials_file"), project=kwargs.get("project")
    )

    bqrepl.run()


@click.command(help="REPL for BigQuery")
@click.option("-c", "--credentials-file", help="path to credentials .json")
@click.option(
    "-p", "--project", help="Use specific project instead of inferring from credentials"
)
def cli(**kwargs):
    main(**kwargs)
