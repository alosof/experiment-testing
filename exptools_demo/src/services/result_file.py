import json
from pathlib import Path


class ResultFile:

    def __init__(self, output_folder: Path):
        self.output_folder = output_folder

    def save(self, circuit_id: int, freq: float):
        self.output_folder.mkdir(parents=True, exist_ok=True)
        out_filepath = self.output_folder / f"result_{str(circuit_id)}.json"
        with open(out_filepath, "w") as out:
            out.write(
                json.dumps({"circuit_id": circuit_id, "qbit_freq": freq})
            )
