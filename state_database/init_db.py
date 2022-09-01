import sqlite3


def init_db(db_name: str, data: list[tuple[int, int, str, float]]):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS states;")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS states 
        (
            id INTEGER PRIMARY KEY,
            circuit_id INTEGER,
            last_changed TEXT, 
            freq_qbit REAL
        );
        """
    )
    cursor.executemany("INSERT INTO states VALUES (?, ?, ?, ?)", data)
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    data_to_insert = [
        (1, 123, "2022-08-30 10:00:00", 5.92),
        (2, 422, "2022-08-30 17:45:00", 6.21),
        (3, 123, "2022-09-01 09:00:00", 6.00)
    ]
    init_db("states.db", data_to_insert)
