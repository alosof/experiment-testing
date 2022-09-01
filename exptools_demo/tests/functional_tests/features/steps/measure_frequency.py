import json
import os
import sqlite3
from pathlib import Path

import requests
from behave import *

from exptools_demo.src.services.instrument import Instrument
from exptools_demo.src.services.result_file import ResultFile
from exptools_demo.src.services.state_database import StateDatabase
from exptools_demo.src.use_cases.measure import Measure


@given('a table "{table_name}" in the database "{db_name}" containing the history of known states of two circuits')
def given_a_database_of_states(context, table_name, db_name):
    context.resources_folder = Path(__file__).parent.parent.parent / "resources"
    context.db = context.resources_folder / db_name

    connection = sqlite3.connect(str(context.db))
    cursor = connection.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} 
        (
            id INTEGER PRIMARY KEY,
            circuit_id INTEGER,
            last_changed TEXT, 
            freq_qbit REAL
        );
        """
    )
    cursor.executemany(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?)", context.table)
    connection.commit()
    cursor.close()
    connection.close()

    context.state_database = StateDatabase(context.db)


@given('a remote configurable instrument on "{host}" exposed at port "{port}"')
def given_an_available_instrument_api(context, host, port):
    url = f"http://{host}:{port}/"
    response = requests.get(url)
    assert response.status_code == 200
    assert json.loads(response.text) == "Welcome to the instrument server."
    context.instrument = Instrument(host, port)


@given('an output folder "{output_folder}"')
def given_an_output_folder(context, output_folder):
    context.result_file = ResultFile(context.resources_folder / output_folder)


@when('a measure is executed for circuit_id "{circuit_id}" with an empty configuration')
def when_a_measure_is_executed_without_config(context, circuit_id):
    instrument_config = {}
    measure = Measure(context.state_database, context.instrument, context.result_file)
    measure.execute(circuit_id=circuit_id, instrument_config=instrument_config)


@then('the instrument is configured with freq_min = "{freq_min}", freq_max = "{freq_max}" and n_freq = "{n_freq}"')
def the_instrument_is_configured_by_default_based_on_known_state(context, freq_min, freq_max, n_freq):
    instrument_config = context.instrument.get_config()
    assert abs(instrument_config["freq_min"] - float(freq_min)) < 1e-10
    assert abs(instrument_config["freq_max"] - float(freq_max)) < 1e-10
    assert instrument_config["n_freq"] == int(n_freq)


@then('a JSON file "{filepath}" is created with a freq value around "{qbit_freq}"')
def a_json_file_with_the_right_content_is_created(context, filepath, qbit_freq):
    output_filepath = context.resources_folder / filepath
    with open(output_filepath) as out:
        result = json.loads(out.read())
    assert float(qbit_freq) - 0.005 <= result["qbit_freq"] <= float(qbit_freq) + 0.005
    os.remove(context.db)
