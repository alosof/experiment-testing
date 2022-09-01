Feature: Measure circuit frequency using instrument

  Scenario: Determine a frequency based on an initial state from a database and the default instrument configuration
    Given a table "states" in the database "test_states.db" containing the history of known states of two circuits
      | id | circuit_id | last_changed        | freq_qbit |
      | 1  | 123        | 2022-08-30 10:00:00 | 5.92      |
      | 2  | 422        | 2022-08-30 17:45:00 | 6.21      |
      | 3  | 123        | 2022-09-01 09:00:00 | 6.00      |
    And a remote configurable instrument on "127.0.0.1" exposed at port "8000"
    And an output folder "test_result_files"
    When a measure is executed for circuit_id "123" with an empty configuration
    Then the instrument is configured with freq_min = "5.7", freq_max = "6.3" and n_freq = "501"
    And a JSON file "test_result_files/result_123.json" is created with a freq value around "6.0672"
