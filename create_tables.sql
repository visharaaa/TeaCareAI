-- 1. Main Entity Tables
CREATE TABLE users (
    user_id SERIAL,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    password VARCHAR(255) NOT NULL,
    user_type VARCHAR(50) NOT NULL,
    CONSTRAINT users_pk PRIMARY KEY (user_id),
    CONSTRAINT users_email_uk UNIQUE (email)
);

CREATE TABLE field (
    field_id SERIAL,
    field_name VARCHAR(100) NOT NULL,
    field_latitude DECIMAL(10, 8),
    field_longitude DECIMAL(11, 8),
    field_elevation DECIMAL(8, 2),
    tea_variety VARCHAR(100),
    plant_age_in_years INT,
    CONSTRAINT field_pk PRIMARY KEY (field_id)
);

CREATE TABLE scan (
    scan_id SERIAL,
    img VARCHAR(500) NOT NULL,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    elevation DECIMAL(8, 2),
    CONSTRAINT scan_pk PRIMARY KEY (scan_id)
);

CREATE TABLE disease (
    disease_id SERIAL,
    disease_name VARCHAR(255) NOT NULL,
    description TEXT,
    standard_symptoms TEXT,
    CONSTRAINT disease_pk PRIMARY KEY (disease_id)
);

CREATE TABLE treatment_recommendation (
    recommendation_id SERIAL,
    treatment_name VARCHAR(255) NOT NULL,
    description TEXT,
    dosage_instructions TEXT,
    CONSTRAINT treatment_recommendation_pk PRIMARY KEY (recommendation_id)
);

-- 2. Detection Table
CREATE TABLE detection (
    detection_id SERIAL,
    scan_id INT,
    disease_id INT,
    confidence_score DECIMAL(5, 4),
    bounding_box JSONB, 
    severity_level VARCHAR(50),
    lesion_count INT,
    healthy_leaf_area DECIMAL(10, 2),
    affected_area DECIMAL(10, 2),
    previous_detection_id INT,
    recovery_percentage DECIMAL(5, 2),
    status VARCHAR(50),
    CONSTRAINT detection_pk PRIMARY KEY (detection_id),
    CONSTRAINT detection_scan_fk FOREIGN KEY (scan_id) REFERENCES scan(scan_id) ON DELETE CASCADE,
    CONSTRAINT detection_disease_fk FOREIGN KEY (disease_id) REFERENCES disease(disease_id) ON DELETE SET NULL,
    CONSTRAINT detection_previous_fk FOREIGN KEY (previous_detection_id) REFERENCES detection(detection_id) ON DELETE SET NULL
);

-- 3. Junction / Associative Tables
CREATE TABLE ownership (
    user_id INT,
    field_id INT,
    CONSTRAINT ownership_pk PRIMARY KEY (user_id, field_id),
    CONSTRAINT ownership_user_fk FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT ownership_field_fk FOREIGN KEY (field_id) REFERENCES field(field_id) ON DELETE CASCADE
);

CREATE TABLE user_scan_history (
    user_id INT,
    field_id INT,
    scan_id INT,
    CONSTRAINT user_scan_history_pk PRIMARY KEY (user_id, field_id, scan_id),
    CONSTRAINT ush_user_fk FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT ush_field_fk FOREIGN KEY (field_id) REFERENCES field(field_id) ON DELETE CASCADE,
    CONSTRAINT ush_scan_fk FOREIGN KEY (scan_id) REFERENCES scan(scan_id) ON DELETE CASCADE
);

CREATE TABLE applied_treatment (
    detection_id INT,
    recommendation_id INT,
    CONSTRAINT applied_treatment_pk PRIMARY KEY (detection_id, recommendation_id),
    CONSTRAINT at_detection_fk FOREIGN KEY (detection_id) REFERENCES detection(detection_id) ON DELETE CASCADE,
    CONSTRAINT at_recommendation_fk FOREIGN KEY (recommendation_id) REFERENCES treatment_recommendation(recommendation_id) ON DELETE CASCADE
);