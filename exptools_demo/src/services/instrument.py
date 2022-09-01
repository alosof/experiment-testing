import json
import logging

import numpy as np
import requests


class Instrument:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.url = f"http://{self.host}:{self.port}"
        self.config_endpoint = f"{self.url}/config"
        self.data_endpoint = f"{self.url}/data"

    def get_config(self) -> dict[str, float | int]:
        return json.loads(requests.get(self.config_endpoint).content)

    def set_config(self, freq_min: float, freq_max: float, n_freq: int):
        config = {
            "freq_min": freq_min,
            "freq_max": freq_max,
            "n_freq": n_freq
        }
        print(f"Configuration used: {config}")
        requests.post(self.config_endpoint, json=config)

    def reset_config(self):
        requests.delete(self.config_endpoint)

    def get_data(self) -> np.ndarray:
        response = requests.get(self.data_endpoint)
        if response.status_code == 200:
            return np.array(json.loads(response.content))
        else:
            response.raise_for_status()
