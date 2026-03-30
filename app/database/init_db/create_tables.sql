-- ============================================================
--  Tea Disease Analysis System — Database Schema
-- ============================================================

-- ENUMS
CREATE TYPE user_type_enum AS ENUM ('farmer', 'agronomist', 'admin', 'state');
CREATE TYPE severity_level_enum AS ENUM ('low', 'medium', 'high');
CREATE TYPE detection_status_enum AS ENUM ('new','improving','stable','deteriorating');

-- ============================================================
--  1. users
-- ============================================================
CREATE TABLE users (
    user_id     SERIAL NOT NULL,
    user_code   VARCHAR(10)  NOT NULL,
    user_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    password    VARCHAR(255) NOT NULL,
    user_type   user_type_enum NOT NULL DEFAULT 'farmer',
    is_revoked  BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT user_pk       PRIMARY KEY (user_id),
    CONSTRAINT user_code_uk  UNIQUE (user_code),
    CONSTRAINT user_email_uk UNIQUE (email)
);

-- ============================================================
--  2. field
-- ============================================================
CREATE TABLE field (
    field_id            SERIAL NOT NULL,
    user_id             INT NOT NULL,
    field_name          VARCHAR(150) NOT NULL,
    field_latitude      DECIMAL(10, 8) NOT NULL,
    field_longitude     DECIMAL(11, 8) NOT NULL,
    field_elevation     DECIMAL(8, 2)  NOT NULL,
    tea_variety         VARCHAR(100)   NOT NULL,
    plant_age_in_years  DECIMAL(5, 1)  NOT NULL,
    CONSTRAINT field_pk PRIMARY KEY (field_id),
    CONSTRAINT field_user_fk FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
--  4. scan_history_chat
-- ============================================================
CREATE TABLE scan_history_chat (
    scan_id                 SERIAL NOT NULL,
    chat_created_timestamp  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    chat_code               VARCHAR(10) NOT NULL,
    latitude                DECIMAL(10, 8),
    longitude               DECIMAL(11, 8),
    elevation               DECIMAL(8, 2),
    CONSTRAINT scan_history_chat_pk PRIMARY KEY (scan_id),
    CONSTRAINT user_chat_code_uk UNIQUE (chat_code)
);

-- ============================================================
--  5. user_scan_history  (users <---> field <---> scan)
-- ============================================================
CREATE TABLE user_scan_history (
    user_id  INT NOT NULL,
    field_id INT NOT NULL,
    scan_id  INT NOT NULL,
    CONSTRAINT user_scan_history_pk           PRIMARY KEY (user_id, field_id, scan_id),
    CONSTRAINT user_scan_history_user_fk      FOREIGN KEY (user_id)  REFERENCES users(user_id)             ON DELETE CASCADE,
    CONSTRAINT user_scan_history_field_fk     FOREIGN KEY (field_id) REFERENCES field(field_id)            ON DELETE CASCADE,
    CONSTRAINT user_scan_history_scan_fk      FOREIGN KEY (scan_id)  REFERENCES scan_history_chat(scan_id) ON DELETE CASCADE
);

-- ============================================================
--  6. disease  (reference / lookup table)
-- ============================================================
CREATE TABLE disease (
    disease_id       SERIAL NOT NULL,
    disease_name     VARCHAR(150) NOT NULL,
    description      TEXT,
    standard_symptoms TEXT,
    CONSTRAINT disease_pk      PRIMARY KEY (disease_id),
    CONSTRAINT disease_name_uk UNIQUE (disease_name)
);


CREATE OR REPLACE FUNCTION fn_disease_no_delete() RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Deletion from the disease table is not permitted. Disease records are permanent. To retire a disease, update its name or description instead.';
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_disease_no_delete
    BEFORE DELETE ON disease
    FOR EACH ROW EXECUTE FUNCTION fn_disease_no_delete();


-- ============================================================
--  7. treatment_recommendation
-- ============================================================
CREATE TABLE treatment_recommendation (
    recommendation_id   SERIAL NOT NULL,
    recommendation_code VARCHAR(10)  NOT NULL,
    generated_advice    TEXT         NOT NULL,
    RAG_confidence_score    DECIMAL(5, 2) NOT NULL,
    model_version       VARCHAR(50)  NOT NULL,
    CONSTRAINT treatment_recommendation_pk           PRIMARY KEY (recommendation_id),
    CONSTRAINT treatment_recommendation_code_uk      UNIQUE (recommendation_code),
    CONSTRAINT treatment_recommendation_RAG_confidence_score_chk CHECK (RAG_confidence_score BETWEEN 0 AND 100)
);

-- ============================================================
--  8. detection
-- ============================================================
CREATE TABLE detection (
    detection_id        SERIAL NOT NULL,
    detection_code      VARCHAR(20)  NOT NULL,
    scan_id             INT          NOT NULL,
    disease_id          INT          NOT NULL,
    confidence_score    DECIMAL(5, 2) NOT NULL,
    bounding_box        JSONB         NOT NULL,
    severity_level      severity_level_enum   NOT NULL,
    lesion_count        INT           NOT NULL DEFAULT 0,
    healthy_leaf_area   DECIMAL(8, 2) NOT NULL,
    affected_area       DECIMAL(8, 2) NOT NULL DEFAULT 0,
    recovery_percentage DECIMAL(5, 2)          DEFAULT 0.00,
    status              detection_status_enum  NOT NULL DEFAULT 'new',
    image_name          VARCHAR(255)  NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT detection_pk               PRIMARY KEY (detection_id),
    CONSTRAINT detection_code_uk          UNIQUE (detection_code),
    CONSTRAINT detection_scan_fk          FOREIGN KEY (scan_id)    REFERENCES scan_history_chat(scan_id) ON DELETE CASCADE,
    CONSTRAINT detection_disease_fk       FOREIGN KEY (disease_id) REFERENCES disease(disease_id)        ON DELETE RESTRICT,
    CONSTRAINT detection_confidence_chk   CHECK (confidence_score   BETWEEN 0 AND 100),
    CONSTRAINT detection_recovery_chk     CHECK (recovery_percentage BETWEEN -100 AND 100)
);

-- ============================================================
--  9. applied_treatment  (detection <---> treatment_recommendation)
-- ============================================================
CREATE TABLE applied_treatment (
    detection_id      INT NOT NULL,
    recommendation_id INT NOT NULL,
    CONSTRAINT applied_treatment_pk             PRIMARY KEY (detection_id, recommendation_id),
    CONSTRAINT applied_treatment_detection_fk   FOREIGN KEY (detection_id)      REFERENCES detection(detection_id)                       ON DELETE CASCADE,
    CONSTRAINT applied_treatment_recommendation_fk FOREIGN KEY (recommendation_id) REFERENCES treatment_recommendation(recommendation_id) ON DELETE CASCADE
);

-- ============================================================
--  10. user_refresh_token
-- ============================================================
CREATE TABLE user_refresh_token (
    token_id    SERIAL NOT NULL,
    user_id     INT    NOT NULL,
    token_hash  VARCHAR(255) NOT NULL,
    device_info VARCHAR(255),
    latitude    DECIMAL(10, 8),
    longitude   DECIMAL(11, 8),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ  NOT NULL,
    is_revoked  BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT user_refresh_token_pk      PRIMARY KEY (token_id),
    CONSTRAINT user_refresh_token_hash_uk UNIQUE (token_hash),
    CONSTRAINT user_refresh_token_user_fk FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
--  INDEXES
-- ============================================================
CREATE INDEX idx_scan_history_field  ON user_scan_history(field_id);
CREATE INDEX idx_scan_history_user   ON user_scan_history(user_id);
CREATE INDEX idx_detection_scan      ON detection(scan_id);
CREATE INDEX idx_detection_disease   ON detection(disease_id);
CREATE INDEX idx_detection_status    ON detection(status);
CREATE INDEX idx_refresh_token_user  ON user_refresh_token(user_id);

-- ============================================================
--  END OF SCHEMA
-- ============================================================


INSERT INTO disease (disease_name, description, standard_symptoms) VALUES
    (
        'Blister Blight',
        'A fungal disease caused by Exobasidium vexans, most prevalent in high-elevation wet zones. Highly destructive to young tea shoots and flushes.',
        'Pale yellow translucent spots on young leaves; white powdery blisters on undersides; leaf distortion and curling; brownish necrotic patches on mature lesions'
    ),
    (
        'Brown Blight',
        'A fungal disease caused by Colletotrichum spp. commonly affecting tea during wet seasons. Causes significant yield loss through shoot dieback.',
        'Water-soaked brown lesions on leaves and stems; dark brown to black necrotic areas; premature defoliation; dieback of young shoots; pinkish spore masses in humid conditions'
    ),
    (
        'Gray Blight',
        'A fungal disease caused by Pestalotiopsis spp. often occurring as secondary infection on already stressed or wounded tea plants.',
        'Grayish-white irregular lesions on mature leaves; dark borders around lesions; black fruiting bodies visible on leaf surface; tip burn appearance; gradual spread from leaf margins inward'
    ),
    (
        'Helopeltis',
        'Insect pest damage caused by Helopeltis theivora (tea mosquito bug). One of the most economically damaging pests of tea plantations.',
        'Dark brown to black lesions at feeding puncture sites; wilting and dieback of young shoots; characteristic cork-like scab formation; distorted and stunted new growth; shot-hole appearance on leaves'
    ),
    (
        'Red Rust',
        'An algal disease caused by Cephaleuros parasiticus affecting tea leaves and stems. More common in poorly maintained or nutrient-deficient plantations.',
        'Rusty red or orange powdery patches on upper leaf surface; circular to irregular velvety growth; hair-like algal filaments visible; yellowing of surrounding tissue; premature leaf drop in severe cases'
    ),
    (
        'Healthy Leaf',
        'A healthy tea leaf with no visible signs of fungal infection, pest damage, or nutrient deficiency. Represents optimal plant health.',
        'Uniform green color; smooth and intact surface; no lesions, spots, or abnormal discoloration; normal leaf shape and growth pattern'
    ),
    (
        'Unknown Disease',
        'The system detected abnormalities but could not confidently classify the visual symptoms into a known disease category. Manual expert inspection is recommended.',
        'Atypical symptoms not matching standard disease profiles; complex mixed infections; unusual damage patterns requiring further analysis'
    );