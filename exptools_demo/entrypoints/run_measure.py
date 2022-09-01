from config import PROJECT_ROOT
from exptools_demo.src.services.instrument import Instrument
from exptools_demo.src.services.result_file import ResultFile
from exptools_demo.src.services.state_database import StateDatabase
from exptools_demo.src.use_cases.measure import Measure

if __name__ == '__main__':
    state_database = StateDatabase(db_path=PROJECT_ROOT / "state_database" / "states.db")
    instrument = Instrument(host="localhost", port=8000)
    result_file = ResultFile(output_folder=PROJECT_ROOT / "result_files")

    measure = Measure(state_database=state_database, instrument=instrument, result_file=result_file)

    instrument_config = {}

    measure.execute(circuit_id=123, instrument_config=instrument_config)
