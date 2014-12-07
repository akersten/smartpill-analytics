SELECT_ACCOUNT_BY_EMAIL = """
    SELECT * FROM accounts WHERE email = ?
"""

SELECT_PATIENTS_BY_CAREGIVER_EMAIL = """
    SELECT * FROM accounts WHERE id IN (SELECT patientId FROM careRelations WHERE caregiverId = (SELECT id FROM accounts WHERE email=?))
"""

SELECT_OTHER_PATIENTS_BY_CAREGIVER_EMAIL = """
    SELECT * FROM accounts WHERE id IN (SELECT patientId FROM careRelations WHERE caregiverId<>(SELECT id FROM accounts WHERE email=?))
"""

SELECT_CAREGIVER_BY_PATIENT_EMAIL = """
    SELECT * FROM accounts WHERE id=(SELECT caregiverId FROM careRelations WHERE patientId = (SELECT id FROM accounts WHERE email=?))
"""

SELECT_UNCLAIMED_PATIENTS = """
    SELECT * FROM accounts WHERE id NOT IN (SELECT patientId FROM careRelations) AND type = 'patient'
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

SELECT_PRESCRIPTIONS_BY_CAREGIVER_EMAIL = """
    SELECT * FROM prescriptions
    WHERE patient IN (SELECT patientId FROM careRelations WHERE caregiverId = (SELECT id FROM accounts WHERE email = ?))
"""

ASSIGN_PATIENT_TO_CAREGIVER_BY_ID_EMAIL = """
    INSERT INTO careRelations(caregiverId, patientId)
    VALUES ((SELECT id FROM accounts WHERE email = ?), ?)
"""