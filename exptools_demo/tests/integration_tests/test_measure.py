import os
import shutil
from pathlib import Path
from unittest import TestCase

import numpy as np

from exptools_demo.src.services.instrument import Instrument
from exptools_demo.src.services.result_file import ResultFile
from exptools_demo.src.services.state_database import StateDatabase
from exptools_demo.src.use_cases.measure import Measure
from state_database.init_db import init_db


class TestMeasure(TestCase):

    def setUp(self) -> None:
        # Database
        self.db_path = str(Path(__file__).parent / "test.db")
        self.state_db = StateDatabase(self.db_path)
        init_db(self.state_db.db_path, [(1, 123, "2022-09-01 09:00:00", 6.00)])

        # Instrument
        self.instrument_server = Instrument("localhost", 8001)

        # Result file
        self.out_file_path = Path(__file__).parent / "out"
        self.result_file = ResultFile(output_folder=self.out_file_path)

    def tearDown(self) -> None:
        os.remove(self.db_path)
        if self.out_file_path.exists():
            shutil.rmtree(self.out_file_path)

    def test_collect_data_when_circuit_id_exists_and_provided_config_is_empty(self):
        # Given
        measure = Measure(self.state_db, self.instrument_server, self.result_file)
        given_config = {}
        circuit_id = 123

        # When
        data, frequencies = measure.collect_data(circuit_id, given_config)

        # Then
        instrument_config = self.instrument_server.get_config()
        expected_config = {
            'freq_min': 6.00 * 0.95,
            'freq_max': 6.00 * 1.05,
            'n_freq': 501
        }
        self.assertDictEqual(expected_config, instrument_config)

        self.assertTupleEqual((5, 501), data.shape)

    def test_collect_data_when_circuit_id_exists_and_provided_config_is_not_empty(self):
        # Given
        measure = Measure(self.state_db, self.instrument_server, self.result_file)
        given_config = {
            'freq_min': 0.,
            'freq_max': 10.,
            'n_freq': 201
        }
        circuit_id = 123

        # When
        data, frequencies = measure.collect_data(circuit_id, given_config)

        # Then
        instrument_config = self.instrument_server.get_config()
        self.assertDictEqual(given_config, instrument_config)

        self.assertTupleEqual((5, 201), data.shape)

    def test_collect_data_when_circuit_id_doesnt_exist_and_config_is_empty(self):
        # Given
        measure = Measure(self.state_db, self.instrument_server, self.result_file)
        given_config = {}
        circuit_id = 555

        # When
        with self.assertRaises(ValueError) as error:
            measure.collect_data(circuit_id, given_config)

        # Then
        self.assertEqual("Circuit ID 555 does not exist in DB !", str(error.exception))

    def test_collect_data_when_circuit_id_doesnt_exist_and_config_is_not_empty(self):
        # Given
        measure = Measure(self.state_db, self.instrument_server, self.result_file)
        given_config = {
            'freq_min': 0.,
            'freq_max': 10.,
            'n_freq': 201
        }
        circuit_id = 555

        # When
        data, frequencies = measure.collect_data(circuit_id, given_config)

        # Then
        expected_frequencies = np.linspace(0., 10., 201)
        np.testing.assert_array_equal(expected_frequencies, frequencies)

        actual_config = self.instrument_server.get_config()
        self.assertDictEqual(given_config, actual_config)

        self.assertTupleEqual((5, 201), data.shape)
