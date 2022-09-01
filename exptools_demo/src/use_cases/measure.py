import numpy as np
from scipy.optimize import curve_fit

from exptools_demo.src.services.instrument import Instrument
from exptools_demo.src.services.result_file import ResultFile
from exptools_demo.src.services.state_database import StateDatabase


class Measure:

    def __init__(self,
                 state_database: StateDatabase,
                 instrument: Instrument,
                 result_file: ResultFile):
        self.state_database = state_database
        self.instrument = instrument
        self.result_file = result_file

    def execute(self, circuit_id: int, instrument_config: dict) -> None:
        data, frequencies = self.collect_data(circuit_id, instrument_config)
        self.process(data, frequencies, circuit_id)

    def collect_data(self, circuit_id: int, instrument_config: dict) -> tuple[np.ndarray, np.ndarray]:
        self.instrument.reset_config()
        if "freq_min" in instrument_config and "freq_max" in instrument_config:
            freq_min, freq_max = instrument_config["freq_min"], instrument_config["freq_max"]
        else:
            _, freq_qbit = self.state_database.get_state(circuit_id)
            freq_min, freq_max = freq_qbit * 0.95, freq_qbit * 1.05
        n_freq = instrument_config.get("n_freq", 501)
        frequencies = np.linspace(freq_min, freq_max, n_freq)
        self.instrument.set_config(freq_min=freq_min,
                                   freq_max=freq_max,
                                   n_freq=n_freq)
        return self.instrument.get_data(), frequencies

    def process(self, data: np.ndarray, frequencies: np.ndarray, circuit_id: int) -> None:
        peak_freq = self.analyze(data, frequencies)
        self.result_file.save(circuit_id, peak_freq)

    @staticmethod
    def analyze(data: np.ndarray, frequencies: np.ndarray) -> float:
        if data.ndim > 1:
            relevant_channel = data[0]
        else:
            relevant_channel = data
        try:
            popt = curve_fit(
                lambda x, a, b, c: a * np.exp(-(x - b) ** 2 / (2 * c ** 2)),
                frequencies,
                relevant_channel
            )
            peak_freq = popt[0][1]
        except RuntimeError:
            peak_freq = frequencies[relevant_channel.argmax()]
        return peak_freq
