import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import numpy as np

from exptools_demo.src.use_cases.measure import Measure
from instrument_server.data_generators import gaussian, Peak


class TestMeasure(TestCase):

    def setUp(self) -> None:
        self.resources_path = Path(__file__).parent.parent / "resources"

    def test_analyze_when_data_has_only_one_channel(self):
        # Given
        frequencies = np.array([5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3])
        data = np.array([[20., 30., 50., 100., 50., 30., 20.]])

        # When
        calculated_frequency = Measure.analyze(data, frequencies)

        # Then
        expected_frequency = 6.0
        self.assertAlmostEqual(expected_frequency, calculated_frequency, 2)

    def test_analyze_when_data_has_two_channels_and_peaks_coincide(self):
        # Given
        frequencies = np.array([5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3])
        data = np.array([
            [20., 30., 50., 120., 50., 30., 20.],
            [15., 25., 40., 100., 40., 25., 15.],
        ])

        # When
        calculated_frequency = Measure.analyze(data, frequencies)

        # Then
        expected_frequency = 6.0
        self.assertAlmostEqual(expected_frequency, calculated_frequency, 2)

    def test_analyze_when_data_has_two_channels_and_peaks_dont_coincide_and_amp0_is_larger(self):
        # Given
        frequencies = np.array([5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3])
        data = np.array([
            [20., 30., 50., 120., 50., 30., 20.],
            [25., 40., 100., 40., 25., 15., 10.],
        ])

        # When
        calculated_frequency = Measure.analyze(data, frequencies)

        # Then
        expected_frequency = 6.0
        self.assertAlmostEqual(expected_frequency, calculated_frequency, 2)

    def test_analyze_when_data_has_two_channels_and_peaks_dont_coincide_amp1_is_larger(self):
        # Given
        frequencies = np.array([5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3])
        data = np.array([
            [25., 40., 100., 40., 25., 15., 10.],
            [20., 30., 50., 120., 50., 30., 20.],
        ])

        # When
        calculated_frequency = Measure.analyze(data, frequencies)

        # Then
        expected_frequency = 5.9
        self.assertAlmostEqual(expected_frequency, calculated_frequency, 2)

    def test_analyze_when_data_has_a_lot_of_samples(self):
        # Given
        frequencies = np.linspace(5.7, 6.3, 1000)
        data = gaussian(peak=Peak(freq=6.2, height=110., width=0.05),
                        freqs=frequencies)

        # When
        calculated_frequency = Measure.analyze(data, frequencies)

        # Then
        expected_frequency = 6.2
        self.assertAlmostEqual(expected_frequency, calculated_frequency, 2)

    def test_analyze_on_realistic_data_that_has_one_peak(self):
        # Given
        with open(self.resources_path / "one_true_peak.json") as config_file:
            conf = json.loads(config_file.read())
        frequencies = np.linspace(conf["freq_min"], conf["freq_max"], conf["n_freq"])
        data = np.load(str(self.resources_path / "one_true_peak.npy"))

        # When
        calculated_frequency = Measure.analyze(data, frequencies)

        # Then
        expected_frequency = 6.1
        self.assertAlmostEqual(expected_frequency, calculated_frequency, 2)

    def test_analyze_on_realistic_data_that_has_two_unequal_peaks(self):
        # Given
        with open(self.resources_path / "two_unequal_peaks.json") as config_file:
            conf = json.loads(config_file.read())
        frequencies = np.linspace(conf["freq_min"], conf["freq_max"], conf["n_freq"])
        data = np.load(str(self.resources_path / "two_unequal_peaks.npy"))

        # When
        calculated_frequency = Measure.analyze(data, frequencies)

        # Then
        expected_frequency = 6.05
        self.assertAlmostEqual(expected_frequency, calculated_frequency, 2)

    def test_analyze_on_realistic_data_that_has_two_equal_peaks(self):
        # Given
        with open(self.resources_path / "two_equal_peaks.json") as config_file:
            conf = json.loads(config_file.read())
        frequencies = np.linspace(conf["freq_min"], conf["freq_max"], conf["n_freq"])
        data = np.load(str(self.resources_path / "two_equal_peaks.npy"))

        # When
        calculated_frequency = Measure.analyze(data, frequencies)

        # Then
        expected_frequency = 6.00
        self.assertAlmostEqual(expected_frequency, calculated_frequency, 2)

    @patch('exptools_demo.src.use_cases.measure.ResultFile')
    @patch('exptools_demo.src.use_cases.measure.Instrument')
    @patch('exptools_demo.src.use_cases.measure.StateDatabase')
    def test_collect_data_when_no_config_is_provided(self,
                                                     mocked_state_database,
                                                     mocked_instrument,
                                                     mocked_result_file):
        # Given
        circuit_id = 345
        freq_qbit = 5.00
        config = {}

        mocked_state_database.get_state.return_value = (circuit_id, freq_qbit)
        mocked_instrument.get_data.return_value = np.array([1, 2, 3, 4])

        measure = Measure(mocked_state_database, mocked_instrument, mocked_result_file)

        # When
        collected_data, collected_frequencies = measure.collect_data(circuit_id, config)

        # Then
        mocked_instrument.reset_config.assert_called_once()
        mocked_state_database.get_state.assert_called_once_with(circuit_id)
        mocked_instrument.set_config.assert_called_once_with(freq_min=4.75,
                                                             freq_max=5.25,
                                                             n_freq=501)
        mocked_instrument.get_data.assert_called_once()

        expected_data = np.array([1, 2, 3, 4])
        np.testing.assert_array_equal(expected_data, collected_data)

        expected_frequencies = np.linspace(4.75, 5.25, 501)
        np.testing.assert_array_equal(expected_frequencies, collected_frequencies)

    @patch('exptools_demo.src.use_cases.measure.ResultFile')
    @patch('exptools_demo.src.use_cases.measure.Instrument')
    @patch('exptools_demo.src.use_cases.measure.StateDatabase')
    def test_collect_data_when_a_config_is_provided(self,
                                                    mocked_state_database,
                                                    mocked_instrument,
                                                    mocked_result_file):
        # Given
        circuit_id = 345
        config = {
            "freq_min": 4.00,
            "freq_max": 5.00,
            "n_freq": 5
        }

        mocked_instrument.get_data.return_value = np.array([1, 2, 3, 4, 5])

        measure = Measure(mocked_state_database, mocked_instrument, mocked_result_file)

        # When
        collected_data, collected_frequencies = measure.collect_data(circuit_id, config)

        # Then
        mocked_state_database.get_state.assert_not_called()
        mocked_instrument.reset_config.assert_called_once()
        mocked_instrument.set_config.assert_called_once_with(**config)
        mocked_instrument.get_data.assert_called_once()

        expected_data = np.array([1, 2, 3, 4, 5])
        np.testing.assert_array_equal(expected_data, collected_data)

        expected_frequencies = np.array([4.00, 4.25, 4.50, 4.75, 5.00])
        np.testing.assert_array_equal(expected_frequencies, collected_frequencies)

    @patch('exptools_demo.src.use_cases.measure.ResultFile')
    @patch('exptools_demo.src.use_cases.measure.Instrument')
    @patch('exptools_demo.src.use_cases.measure.StateDatabase')
    def test_process(self,
                     mocked_state_database,
                     mocked_instrument,
                     mocked_result_file):
        # Given
        circuit_id = 345
        data = np.array([[1., 2., 3., 10., 3., 2., 1.],
                         [5., 10., 100., 10., 5., 3., 1.]])
        frequencies = np.array([5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3])
        measure = Measure(mocked_state_database, mocked_instrument, mocked_result_file)

        # When
        measure.process(data, frequencies, circuit_id)

        # Then
        expected_freq = 6.0
        mocked_result_file.save.assert_called_once_with(circuit_id, expected_freq)
