SELECT_ACCOUNT_BY_EMAIL = """
    SELECT * FROM accounts WHERE email = ?
"""

SELECT_PATIENTS_BY_CAREGIVER_EMAIL = """
    SELECT * FROM accounts WHERE id=(SELECT patientId FROM careRelations WHERE caregiverId = (SELECT id FROM accounts WHERE email=?))
"""

SELECT_OTHER_PATIENTS_BY_CAREGIVER_EMAIL = """
    SELECT * FROM accounts WHERE id=(SELECT patientId FROM careRelations WHERE caregiverId<>(SELECT id FROM accounts WHERE email=?))
"""

INSERT_ACCOUNT = """
  INSERT INTO accounts(name, email, password, type)
  VALUES (?, ?, ?, ?)
"""

SELECT_DOSES_BY_TIME_BETWEEN = """
    SELECT * FROM doses WHERE patientName = ? AND time > ? AND time < ?
"""

INSERT_DOSE = """
    INSERT INTO doses(prescriptionId, prescriptionName, time, taken, patientName)
    VALUES (?, ?, ?, ?, ?)
"""

UPDATE_ACTUAL_TIME_AND_TAKEN_BY_DOSE_TIME = """
    UPDATE doses
    SET actualTime=?, taken=?
    WHERE time=?
"""

SELECT_PRESCRIPTIONS_BY_PATIENT_EMAIL = """
    SELECT * FROM prescriptions
    WHERE patient = (SELECT id FROM accounts WHERE email = ?)
"""