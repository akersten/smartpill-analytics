SELECT_ACCOUNT_BY_EMAIL = """
    SELECT * FROM accounts WHERE email = ?
"""

SELECT_PATIENT_NAME_BY_ID = """
    SELECT name FROM accounts WHERE id = ?
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

SELECT_DOSES_BY_TIME_BETWEEN = """
    SELECT * FROM doses WHERE patientName = ? AND time > ? AND time < ?
"""

SELECT_DOSE_TAKEN_GROUP_BY_PRESCRIPTION_ID = """
    SELECT COUNT(id), taken, prescriptionId FROM doses GROUP BY prescriptionId, taken
"""

SELECT_DOSE_TAKEN_GROUP_BY_PRESCRIPTION_ID_BETWEEN = """
    SELECT COUNT(id), taken, prescriptionId FROM doses WHERE time > ? and TIME < ? GROUP BY prescriptionId, taken
"""

SELECT_PRESCRIPTION_ID_BY_PATIENT_ID_AND_PRESCRIPTION_NAME = """
    SELECT id FROM prescriptions
    WHERE patient = ? AND prescriptionName = ?
"""

INSERT_ACCOUNT = """
  INSERT INTO accounts(name, email, password, type)
  VALUES (?, ?, ?, ?)
"""

INSERT_PRESCRIPTION = """
    INSERT INTO prescriptions(prescriptionName, patient, start, end, schedule)
    VALUES (?, ?, ?, ?, ?)
"""

INSERT_DOSE = """
    INSERT INTO doses(prescriptionId, prescriptionName, time, taken, patientName)
    VALUES (?, ?, ?, ?, ?)
"""

DELETE_PRESCRIPTION = """
    DELETE FROM prescriptions
    WHERE id=?
"""

DELETE_DOSES = """
    DELETE FROM doses
    WHERE prescriptionId = ?
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