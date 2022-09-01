import random

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from data_generators import generate_peaks, Peak

app = FastAPI()

instrument_params = {}


class InstrumentConfig(BaseModel):
    freq_min: float
    freq_max: float
    n_freq: int


@app.get("/")
async def root():
    return "Welcome to the instrument server."


@app.get("/config")
async def get_config():
    global instrument_params
    return instrument_params


@app.post("/config")
async def set_config(config: InstrumentConfig):
    global instrument_params
    instrument_params["freq_min"] = config.freq_min
    instrument_params["freq_max"] = config.freq_max
    instrument_params["n_freq"] = config.n_freq


@app.delete("/config")
async def reset_config():
    global instrument_params
    instrument_params = {}


@app.get("/data")
async def get_data():
    global instrument_params
    if instrument_params == {}:
        raise HTTPException(status_code=400, detail="Instrument is not configured. Set the configuration first!")

    freq_min = instrument_params["freq_min"]
    freq_max = instrument_params["freq_max"]
    n_freq = instrument_params["n_freq"]

    seed = 10
    random.seed(seed)
    np.random.seed(seed)

    peaks = [
        Peak(freq=random.uniform(freq_min * 1.2, freq_max * 0.8),
             height=random.uniform(20., 120.),
             width=random.uniform(0.001, 0.025))
        for _ in range(random.randint(1, 2))
    ]
    frequencies, data = generate_peaks(
        peaks=peaks,
        freq_min=freq_min,
        freq_max=freq_max,
        n_freq=n_freq,
        seed=seed
    )
    return data.tolist()
