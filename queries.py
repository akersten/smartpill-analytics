SELECT_ACCOUNT_BY_EMAIL = """
    SELECT * FROM accounts WHERE email = ?
"""

INSERT_ACCOUNT = """
  INSERT INTO accounts(name, email, password, type)
  VALUES (?, ?, ?, ?)
"""