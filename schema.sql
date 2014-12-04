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
    id INTEGER PRIMARY KEY,
    caregiverId INTEGER NOT NULL,
    patientId INTEGER NOT NULL,
    FOREIGN KEY(caregiverId) REFERENCES accounts(id),
    FOREIGN KEY(patientId) REFERENCES accounts(id)
);

-- Each patient has one or more prescriptions that must be adhered to.
DROP TABLE IF EXISTS prescriptions;

-- id: Automatic primary key
-- prescriptionName: The name of the medicine
-- patient: The ID of the patient from the `accounts` table
-- start: The unix timestamp when the prescription begins
-- end: The unix timestamp when the prescription ends (if not specified, the prescription is considered indefinite)
-- schedule: How often the dosage needs to happen (in unix time intervals from the time specified by `start`)
CREATE TABLE prescriptions (
    id INTEGER PRIMARY KEY,
    prescriptionName TEXT NOT NULL,
    patient INTEGER NOT NULL,
    start INTEGER NOT NULL,
    end INTEGER,
    schedule INTEGER NOT NULL,
    FOREIGN KEY(patient) REFERENCES accounts(id)
);

-- Keep track of when patients take dosages of the medication. Each dose event is a separate row in this table.
DROP TABLE IF EXISTS doses;

-- id: Automatic primary key
-- prescriptionId: The ID of the prescription from the `prescriptions` table
-- prescriptionName: The name of the medicine from the `prescriptions` table
-- time: What time (unix timestamp) the patient took the dose
-- taken: Whether the dose has been taken (1) or not (0)
CREATE TABLE doses (
    id INTEGER PRIMARY KEY,
    prescriptionId INTEGER NOT NULL,
    prescriptionName TEXT NOT NULL,
    time INTEGER NOT NULL,
    taken INTEGER NOT NULL,
    patientName TEXT NOT NULL,
    FOREIGN KEY(prescriptionName) REFERENCES prescriptions(prescriptionName),
    FOREIGN KEY(prescriptionId) REFERENCES prescriptions(id),
    FOREIGN KEY(patientName) REFERENCES accounts(name)
);


-- test data...
INSERT INTO accounts(name, email, password, type)
VALUES ("Tunnel Bob", "tunnel@bob.com", "steam tunnelz", "patient");

INSERT INTO prescriptions(id, prescriptionName, patient, start, end, schedule)
VALUES (1, "Little blue pill", "Tunnel Bob", 0, 400000, 200);

INSERT INTO doses(prescriptionId, prescriptionName, time, taken, patientName)
VALUES (1, "Little blue pill", 10, 0, "Tunnel Bob");
INSERT INTO doses(prescriptionId, prescriptionName, time, taken, patientName)
VALUES (1, "Little blue pill", 100, 0, "Tunnel Bob");
INSERT INTO doses(prescriptionId, prescriptionName, time, taken, patientName)
VALUES (1, "Little blue pill", 1000, 1, "Tunnel Bob");
INSERT INTO doses(prescriptionId, prescriptionName, time, taken, patientName)
VALUES (1, "Little blue pill", 10000, 1, "Tunnel Bob");
INSERT INTO doses(prescriptionId, prescriptionName, time, taken, patientName)
VALUES (1, "Little blue pill", 20000, 0, "Tunnel Bob");
INSERT INTO doses(prescriptionId, prescriptionName, time, taken, patientName)
VALUES (1, "Little blue pill", 30000, 0, "Tunnel Bob");
INSERT INTO doses(prescriptionId, prescriptionName, time, taken, patientName)
VALUES (1, "Little blue pill", 40000, 0, "Tunnel Bob");