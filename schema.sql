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

-- caregiverId: The ID of the caregiver from the `accounts` table
-- patientId: The ID of the patient from the `accounts` table
CREATE TABLE careRelations (
    caregiverId INTEGER NOT NULL,
    patientId INTEGER NOT NULL,
    FOREIGN KEY(caregiverId) REFERENCES (accounts),
    FOREIGN KEY(patientId) REFERENCES (accounts)
);

-- Each patient has one or more prescriptions that must be adhered to.
DROP TABLE IF EXISTS prescriptions;

-- id: Automatic primary key
-- patient: The ID of the patient from the `accounts` table
-- start: The unix timestamp when the prescription begins
-- end: The unix timestamp when the prescription ends (if not specified, the prescription is considered indefinite)
-- schedule: How often the dosage needs to happen (in unix time intervals from the time specified by `start`)
CREATE TABLE prescriptions (
    id INTEGER PRIMARY KEY,
    patient INTEGER NOT NULL,
    start INTEGER NOT NULL,
    end INTEGER,
    schedule INTEGER NOT NULL,
    FOREIGN KEY(patient) REFERENCES (accounts)
);

