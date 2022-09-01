from dataclasses import dataclass

import numpy as np


@dataclass
class Peak:
    freq: float
    height: float
    width: float


def gaussian(peak: Peak, freqs: np.ndarray) -> np.ndarray:
    return peak.height * np.exp(-(freqs - peak.freq) ** 2 / (2 * peak.width ** 2))


def generate_peaks(peaks: list[Peak],
                   freq_min: float,
                   freq_max: float,
                   n_freq: int,
                   seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    frequencies = np.linspace(freq_min, freq_max, n_freq)
    np.random.seed(seed)
    signal = np.array([gaussian(peak, frequencies) for peak in peaks]).sum(axis=0)
    signal = np.array([signal * i for i in [1.00, 0.95, 0.90, 0.85, 0.80]])
    max_height = 100
    noise = np.random.normal(loc=max_height / 100, scale=max_height / 25, size=signal.shape)
    return frequencies, signal + noise
