-- 1. Insert a test user (Farmer)
INSERT INTO users (user_name, email, password, user_type) 
VALUES ('Kamal Perera', 'kamal.test@example.com', 'hashed_password_123', 'Farmer');

-- 2. Insert a test tea field (Using coordinates typical for a tea estate)
INSERT INTO field (field_name, field_latitude, field_longitude, field_elevation, tea_variety, plant_age_in_years)
VALUES ('Estate Block A', 6.96000000, 80.76000000, 1800.50, 'Camellia sinensis var. assamica', 15);

-- 3. Link the user to the field (Ownership)
-- Assuming the user_id is 1 and field_id is 1 based on the inserts above
INSERT INTO ownership (user_id, field_id) VALUES (1, 1);

-- 4. Insert common tea diseases
INSERT INTO disease (disease_name, description, standard_symptoms) VALUES 
('Blister Blight', 'A fungal disease affecting young tea shoots.', 'Translucent spots on leaves that turn into white, blister-like swellings.'),
('Red Rust', 'An algal disease affecting the stems and leaves.', 'Orange-red hairy patches on the upper surface of mature leaves.');

-- 5. Insert treatment recommendations
INSERT INTO treatment_recommendation (treatment_name, description, dosage_instructions) VALUES 
('Copper Fungicide Spray', 'Standard chemical control for Blister Blight.', 'Apply 0.2% concentration every 7-10 days during rainy seasons.'),
('Improve Ventilation', 'Cultural control method for fungal/algal infections.', 'Prune surrounding shade trees to reduce humidity and increase sunlight.');

-- 6. Insert a test scan 
-- IMPORTANT: Change the 'img' path here to match where your actual image is stored on your computer!
INSERT INTO scan (img, latitude, longitude, elevation)
VALUES ('Blister_Blight_dt3_00245', 6.96010000, 80.76020000, 1800.50);

-- 7. Log the scan history
INSERT INTO user_scan_history (user_id, field_id, scan_id) VALUES (1, 1, 1);

-- 8. Insert a mock YOLO/SAM Detection result
INSERT INTO detection (
    scan_id, disease_id, confidence_score, bounding_box, severity_level, 
    lesion_count, healthy_leaf_area, affected_area, status
) VALUES (
    1, 1, 0.9250, '{"box": [150, 80, 240, 190], "label": "blister"}', 'Moderate', 
    3, 45.50, 12.20, 'Needs Treatment'
);

-- 9. Log the recommended treatment for this specific detection
INSERT INTO applied_treatment (detection_id, recommendation_id) VALUES (1, 1);