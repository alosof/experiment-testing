import sqlite3
from pathlib import Path


class StateDatabase:

    def __init__(self, db_path: Path | str):
        self.db_path = db_path

    def get_state(self, circuit_id: int) -> tuple[int, float]:
        """Get the latest known state of a given circuit as a tuple (freq_qbit, decay_qbit)."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        query = """
            SELECT circuit_id, freq_qbit
            FROM states 
            WHERE circuit_id=? 
            ORDER BY DATETIME(last_changed) DESC 
            LIMIT 1;
        """
        resultset = cursor.execute(query, (circuit_id,)).fetchone()
        if resultset is None:
            raise ValueError(f"Circuit ID {circuit_id} does not exist in DB !")
        freq_qbit, decay_qbit = cursor.execute(query, (circuit_id,)).fetchone()
        cursor.close()
        connection.close()
        return freq_qbit, decay_qbit
