SELECT_ACCOUNT_BY_EMAIL = """
    SELECT * FROM accounts WHERE email = ?
"""

INSERT_ACCOUNT = """
  INSERT INTO accounts(name, email, password, type)
  VALUES (?, ?, ?, ?)
"""

SELECT_DOSES_BY_TIME_BETWEEN = """
    SELECT * FROM doses WHERE patientName = ? AND time > ? AND time < ?
"""