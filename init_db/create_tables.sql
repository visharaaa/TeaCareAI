--  ENUMS
CREATE TYPE user_type_enum AS ENUM ('farmer', 'agronomist', 'admin','state');

CREATE TYPE severity_level_enum AS ENUM ('low', 'medium', 'high');

CREATE TYPE detection_status_enum AS ENUM ('new', 'under_treatment', 'recovered', 'escalated');


--  1. users
CREATE TABLE users (
    user_id     SERIAL          NOT NULL,
    user_code   VARCHAR(10)     NOT NULL,
    user_name   VARCHAR(100)    NOT NULL,
    email       VARCHAR(255)    NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    password    VARCHAR(255)    NOT NULL,               -- store bcrypt/argon2 hash
    user_type   user_type_enum  NOT NULL DEFAULT 'farmer',

    CONSTRAINT user_pk          PRIMARY KEY (user_id),
    CONSTRAINT user_code_uk  UNIQUE (user_code),
    CONSTRAINT user_email_uk    UNIQUE      (email)    -- AK
);


--  2. field
CREATE TABLE field (
    field_id            SERIAL          NOT NULL,
    field_name          VARCHAR(150)    NOT NULL,
    field_latitude      DECIMAL(10, 8)  NOT NULL,
    field_longitude     DECIMAL(11, 8)  NOT NULL,
    field_elevation     DECIMAL(8, 2)   NOT NULL,             -- meters
    tea_variety         VARCHAR(100)    NOT NULL,
    plant_age_in_years  DECIMAL(5, 1)   NOT NULL,

    CONSTRAINT field_pk PRIMARY KEY (field_id)
);

--  3. ownership  (users <--- owns ---> field)
--     Composite PK: (user_id, field_id)
CREATE TABLE ownership (
    user_id     INT     NOT NULL,
    field_id    INT     NOT NULL,

    CONSTRAINT ownership_pk PRIMARY KEY (user_id, field_id),
    CONSTRAINT ownership_user_fk FOREIGN KEY (user_id) REFERENCES users(user_id)  ON DELETE CASCADE,
    CONSTRAINT ownership_field_fk FOREIGN KEY (field_id) REFERENCES field(field_id)  ON DELETE CASCADE
);

--  4. scan_history_chat
--     Stores per-scan GPS context and timestamp
CREATE TABLE scan_history_chat (
    scan_id                 SERIAL          NOT NULL,
    chat_created_timestamp  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    latitude                DECIMAL(10, 8),
    longitude               DECIMAL(11, 8),
    elevation               DECIMAL(8, 2),

    CONSTRAINT scan_history_chat_pk PRIMARY KEY (scan_id)
);

--  5. user_scan_history(users <---> field <---> scan)
--     Composite PK: (user_id, field_id, scan_id)
CREATE TABLE user_scan_history (
    user_id     INT     NOT NULL,
    field_id    INT     NOT NULL,
    scan_id     INT     NOT NULL,

    CONSTRAINT user_scan_history_pk             PRIMARY KEY (user_id, field_id, scan_id),
    CONSTRAINT user_scan_history_user_fk        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT user_scan_history_field_fk       FOREIGN KEY (field_id) REFERENCES field(field_id) ON DELETE CASCADE,
    CONSTRAINT user_scan_history_scan_fk        FOREIGN KEY (scan_id) REFERENCES scan_history_chat(scan_id)   ON DELETE CASCADE,

    CONSTRAINT user_scan_history_ownership_fk   FOREIGN KEY (user_id, field_id) REFERENCES ownership(user_id, field_id) ON DELETE CASCADE
);


--  6. disease  (reference / lookup table)
CREATE TABLE disease (
    disease_id          SERIAL          NOT NULL,
    disease_name        VARCHAR(150)    NOT NULL,
    description         TEXT,
    standard_symptoms   TEXT,

    CONSTRAINT disease_pk       PRIMARY KEY (disease_id),
    CONSTRAINT disease_name_uk  UNIQUE      (disease_name)
);

-- Trigger: block all DELETE attempts on the disease table
CREATE OR REPLACE FUNCTION fn_disease_no_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION
        'Deletion from the disease table is not permitted. Disease records are permanent. '
        'To retire a disease, update its name or description instead.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_disease_no_delete
BEFORE DELETE ON disease
FOR EACH ROW
EXECUTE FUNCTION fn_disease_no_delete();



--  7. treatment_recommendation
--     RAG-generated treatment advice
CREATE TABLE treatment_recommendation (
    recommendation_id   SERIAL          NOT NULL,
    recommendation_code VARCHAR(10)     NOT NULL,
    generated_advice    TEXT            NOT NULL,
    feedback_score      SMALLINT        NULL,
    model_version       VARCHAR(50)     NOT NULL,

    CONSTRAINT treatment_recommendation_pk              PRIMARY KEY (recommendation_id),
    CONSTRAINT treatment_recommendation_code_uk  UNIQUE (recommendation_code),
    CONSTRAINT treatment_recommendation_feedback_chk    CHECK (feedback_score BETWEEN 1 AND 5)
);


--  8. detection
--     Core output of the YOLO segmentation model+recovery_percentage is updated by the NN recovery tracker
CREATE TABLE detection (
    detection_id        SERIAL                  NOT NULL,
    detection_code      VARCHAR(20)             NOT NULL,
    scan_id             INT                     NOT NULL,
    disease_id          INT                     NOT NULL,
    confidence_score    DECIMAL(5, 4)           NOT NULL,
    bounding_box        JSONB                   NOT NULL,
    severity_level      severity_level_enum     NOT NULL,
    lesion_count        INT                     NOT NULL DEFAULT 0,
    healthy_leaf_area   DECIMAL(5, 2)           NOT NULL,                     -- percentage 0.00-100.00
    affected_area       DECIMAL(5, 2)           NOT NULL DEFAULT 0,           -- percentage 0.00-100.00
    recovery_percentage DECIMAL(5, 2)           DEFAULT 0.00,
    status              detection_status_enum   NOT NULL   DEFAULT 'new',
    image_name          VARCHAR(255)            NOT NULL,

    CONSTRAINT detection_pk                 PRIMARY KEY (detection_id),
    CONSTRAINT detection_code_uk            UNIQUE (detection_code),
    CONSTRAINT detection_scan_fk            FOREIGN KEY (scan_id) REFERENCES scan_history_chat(scan_id) ON DELETE CASCADE,
    CONSTRAINT detection_disease_fk         FOREIGN KEY (disease_id) REFERENCES disease(disease_id) ON DELETE RESTRICT,
    CONSTRAINT detection_confidence_chk     CHECK (confidence_score BETWEEN 0 AND 1),
    CONSTRAINT detection_healthy_area_chk   CHECK (healthy_leaf_area BETWEEN 0 AND 100),
    CONSTRAINT detection_affected_area_chk  CHECK (affected_area BETWEEN 0 AND 100),
    CONSTRAINT detection_recovery_chk       CHECK (recovery_percentage BETWEEN 0 AND 100)
);

--  9. applied_treatment (detection <---> treatment_recommendation)
--     Composite PK: (detection_id, recommendation_id)
CREATE TABLE applied_treatment (
    detection_id        INT     NOT NULL,
    recommendation_id   INT     NOT NULL,

    CONSTRAINT applied_treatment_pk                 PRIMARY KEY (detection_id, recommendation_id),
    CONSTRAINT applied_treatment_detection_fk       FOREIGN KEY (detection_id) REFERENCES detection(detection_id) ON DELETE CASCADE,
    CONSTRAINT applied_treatment_recommendation_fk  FOREIGN KEY (recommendation_id) REFERENCES treatment_recommendation(recommendation_id)  ON DELETE CASCADE
);

-- 10.user_refresh_token
CREATE TABLE user_refresh_token (
    token_id        SERIAL          NOT NULL,
    user_id         INT             NOT NULL,
    token_hash      VARCHAR(255)    NOT NULL ,   -- store hashed, never plain
    device_info     VARCHAR(255),               -- e.g. "Chrome on Windows"
    latitude        DECIMAL(10, 8),
    longitude       DECIMAL(11, 8),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ     NOT NULL,
    is_revoked      BOOLEAN         NOT NULL DEFAULT FALSE,

    CONSTRAINT user_refresh_token_pk        PRIMARY KEY (token_id),
    CONSTRAINT user_refresh_token_hash_uk   UNIQUE (token_hash),
    CONSTRAINT user_refresh_token_user_fk   FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);


--  INDEXES

CREATE INDEX idx_ownership_user         ON ownership(user_id);

CREATE INDEX idx_scan_history_field     ON user_scan_history(field_id);

CREATE INDEX idx_scan_history_user      ON user_scan_history(user_id);

CREATE INDEX idx_detection_scan         ON detection(scan_id);

CREATE INDEX idx_detection_disease      ON detection(disease_id);

CREATE INDEX idx_detection_status       ON detection(status);

CREATE INDEX idx_refresh_token_user ON user_refresh_token(user_id);
