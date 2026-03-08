-- Create the 'ods' schema if it does not already exist
CREATE SCHEMA IF NOT EXISTS ods;

-- Table: ods.subscriptions
CREATE TABLE IF NOT EXISTS ods.subscriptions (
    subscription_id SERIAL PRIMARY KEY, -- Primary Key, auto-incremented
    name TEXT,                          -- Subscription Plan Name (e.g., Free, Pro)
    max_currencies INTEGER,             -- Max currencies user can track
    price_per_month FLOAT               -- Monthly price in USD
);

-- Table: ods.users
CREATE TABLE IF NOT EXISTS ods.users (
    user_id SERIAL PRIMARY KEY,             -- Primary Key, auto-incremented
    username TEXT UNIQUE,                   -- Username, must be unique
    email TEXT UNIQUE,                      -- Email Address, must be unique
    password_hash TEXT,                     -- Hashed Password
    created_at TIMESTAMPTZ,                 -- User registration timestamp
    subscription_id INTEGER,                -- Foreign Key referencing subscriptions table
    FOREIGN KEY (subscription_id) REFERENCES ods.subscriptions (subscription_id)
);

-- Table: ods.currencies
CREATE TABLE IF NOT EXISTS ods.currencies (
    currency_id SERIAL PRIMARY KEY,     -- Primary Key, auto-incremented
    symbol TEXT,                        -- e.g., BTC, ETH
    name TEXT,                          -- Full currency name
    is_flagged_aml BOOLEAN              -- Whether flagged for AML risk
);

-- Table: ods.user_currencies
CREATE TABLE IF NOT EXISTS ods.user_currencies (
    user_id INTEGER,                    -- Foreign Key referencing users table
    currency_id INTEGER,                -- Foreign Key referencing currencies table
    added_at TIMESTAMPTZ,               -- When the user added the currency
    PRIMARY KEY (user_id, currency_id), -- Composite primary key to ensure unique user-currency pairs
    FOREIGN KEY (user_id) REFERENCES ods.users (user_id),
    FOREIGN KEY (currency_id) REFERENCES ods.currencies (currency_id)
);

INSERT INTO ods.subscriptions (name, max_currencies, price_per_month) VALUES ('Free', 5, 0.00), ('Pro', 50, 15.00), ('Enterprise', 500, 75.00);

CREATE TABLE IF NOT EXISTS email_verification (
    email VARCHAR(255) PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ods.survey_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE, -- Each user should only have one questionnaire result

    -- The results of the questionnaire
    score INTEGER,
    rating VARCHAR(50),

    -- The answer to each question is a separate column
    answer_q1 TEXT,
    answer_q2 TEXT,
    answer_q3 TEXT,
    answer_q4 TEXT,
    answer_q5 TEXT,
    answer_q6 TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_ods_survey_results_user_id
      FOREIGN KEY (user_id) REFERENCES ods.users (user_id)
      ON DELETE CASCADE
);

COMMENT ON TABLE ods.survey_results IS 'Stores the users complete questionnaire submission results, including the score and the answer to each question.';