-- An account can be either a caregiver or a patient. Caregivers can see statistics of many accounts, while patients can
-- only see themselves.
DROP TABLE IF EXISTS accounts;

-- id: Automatic primary key
-- name: The full name of the caregiver or patient
-- email: The email associated with the account
-- password: A hash of the password of the account TODO: What hashing algorithm?
-- type: The type of the account ('caregiver' or 'patient')
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    type TEXT NOT NULL
);

-- A caregiver may have multiple patients that they track - this table will associate their account with the appropriate
-- patient IDs.
DROP TABLE IF EXISTS careRelations;

