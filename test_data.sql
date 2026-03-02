-- ============================================================
--  Tea Disease Analysis System — Test Seed Data
--  Insert order follows FK dependency chain
-- ============================================================

-- ============================================================
--  1. users  (4 users — different roles)
-- ============================================================
INSERT INTO users (user_code, user_name, email, password, user_type) VALUES
('USR00001', 'Kamal Perera',    'kamal.perera@teaplant.lk',   '$2b$12$dummyhash1', 'farmer'),
('USR00002', 'Nimal Silva',     'nimal.silva@teaplant.lk',    '$2b$12$dummyhash2', 'farmer'),
('USR00003', 'Dr. Suneth Dias', 'suneth.dias@agro.lk',        '$2b$12$dummyhash3', 'agronomist'),
('USR00004', 'Admin User',      'admin@teaplant.lk',          '$2b$12$dummyhash4', 'admin');


-- ============================================================
--  2. field  (4 fields — Sri Lanka locations)
-- ============================================================
INSERT INTO field (field_name, field_latitude, field_longitude, field_elevation, tea_variety, plant_age_in_years) VALUES
('Nuwara Eliya Block A',  6.97080000,  80.78290000, 1868.00, 'Ceylon High Grown',  8.5),
('Kandy Estate Block B',  7.29430000,  80.63500000, 1200.00, 'Assam Hybrid',        5.0),
('Matara Lowland Block',  5.94490000,  80.54550000,   30.00, 'Ceylon Low Grown',   12.0),
('Badulla Hill Block C',  6.98940000,  81.05490000, 1400.00, 'Uva Variety',         3.5);


-- ============================================================
--  3. ownership  (assign fields to users)
-- ============================================================
INSERT INTO ownership (user_id, field_id) VALUES
(1, 1),   -- Kamal owns Nuwara Eliya Block A
(1, 2),   -- Kamal also owns Kandy Estate Block B
(2, 3),   -- Nimal owns Matara Lowland Block
(3, 4);   -- Dr. Suneth owns Badulla Hill Block C


-- ============================================================
--  4. disease  (5 tea diseases)
-- ============================================================
INSERT INTO disease (disease_name, description, standard_symptoms) VALUES
(
    'Blister Blight',
    'A fungal disease caused by Exobasidium vexans, most prevalent in high-elevation wet zones. '
    'Highly destructive to young tea shoots and flushes.',
    'Pale yellow translucent spots on young leaves; white powdery blisters on undersides; '
    'leaf distortion and curling; brownish necrotic patches on mature lesions'
),
(
    'Brown Blight',
    'A fungal disease caused by Colletotrichum spp. commonly affecting tea during wet seasons. '
    'Causes significant yield loss through shoot dieback.',
    'Water-soaked brown lesions on leaves and stems; dark brown to black necrotic areas; '
    'premature defoliation; dieback of young shoots; pinkish spore masses in humid conditions'
),
(
    'Gray Blight',
    'A fungal disease caused by Pestalotiopsis spp. often occurring as secondary infection '
    'on already stressed or wounded tea plants.',
    'Grayish-white irregular lesions on mature leaves; dark borders around lesions; '
    'black fruiting bodies visible on leaf surface; tip burn appearance; '
    'gradual spread from leaf margins inward'
),
(
    'Helopeltis',
    'Insect pest damage caused by Helopeltis theivora (tea mosquito bug). '
    'One of the most economically damaging pests of tea plantations.',
    'Dark brown to black lesions at feeding puncture sites; wilting and dieback of young shoots; '
    'characteristic cork-like scab formation; distorted and stunted new growth; '
    'shot-hole appearance on leaves'
),
(
    'Red Rust',
    'An algal disease caused by Cephaleuros parasiticus affecting tea leaves and stems. '
    'More common in poorly maintained or nutrient-deficient plantations.',
    'Rusty red or orange powdery patches on upper leaf surface; '
    'circular to irregular velvety growth; hair-like algal filaments visible; '
    'yellowing of surrounding tissue; premature leaf drop in severe cases'
);


-- ============================================================
--  5. scan_history_chat  (6 scan sessions with GPS)
-- ============================================================
INSERT INTO scan_history_chat (chat_created_timestamp, latitude, longitude, elevation) VALUES
('2025-01-10 08:30:00+05:30',  6.97085000,  80.78295000, 1869.00),  -- scan 1: Nuwara Eliya
('2025-01-15 09:15:00+05:30',  6.97090000,  80.78300000, 1870.00),  -- scan 2: Nuwara Eliya follow-up
('2025-02-05 10:00:00+05:30',  7.29435000,  80.63505000, 1201.00),  -- scan 3: Kandy
('2025-02-20 14:30:00+05:30',  5.94495000,  80.54560000,   31.00),  -- scan 4: Matara
('2025-03-01 07:45:00+05:30',  6.98945000,  81.05495000, 1401.00),  -- scan 5: Badulla
('2025-03-15 11:00:00+05:30',  6.97088000,  80.78298000, 1868.50);  -- scan 6: Nuwara Eliya recovery scan


-- ============================================================
--  6. user_scan_history  (link users + fields + scans)
-- ============================================================
INSERT INTO user_scan_history (user_id, field_id, scan_id) VALUES
(1, 1, 1),   -- Kamal scanned Nuwara Eliya Block A  — initial scan
(1, 1, 2),   -- Kamal scanned Nuwara Eliya Block A  — follow-up scan
(1, 2, 3),   -- Kamal scanned Kandy Estate Block B
(2, 3, 4),   -- Nimal scanned Matara Lowland Block
(3, 4, 5),   -- Dr. Suneth scanned Badulla Hill Block C
(1, 1, 6);   -- Kamal recovery scan Nuwara Eliya Block A


-- ============================================================
--  7. treatment_recommendation  (6 RAG-generated recommendations)
--     NOTE: feedback_score is NULL when user has not yet rated
-- ============================================================
INSERT INTO treatment_recommendation (recommendation_code, generated_advice, feedback_score, model_version) VALUES
(
    'REC00001',
    'Apply copper-based fungicide (Copper Oxychloride 50% WP) at 3g/L every 7-10 days during flushing. '
    'Ensure adequate shade regulation to reduce humidity. Remove and destroy severely infected shoots. '
    'Improve air circulation by pruning. Apply systemic fungicide (Hexaconazole) as curative treatment.',
    5, 'rag-v1.2'
),
(
    'REC00002',
    'Apply Carbendazim 50% WP at 1g/L or Thiophanate-methyl as foliar spray. '
    'Drain waterlogged areas around plants. Remove infected plant debris promptly. '
    'Avoid overhead irrigation. Consider resistant variety replanting for severely affected zones.',
    4, 'rag-v1.2'
),
(
    'REC00003',
    'Apply Mancozeb 75% WP at 2.5g/L as protective spray. '
    'Remove and burn infected leaves. Improve drainage and reduce nitrogen fertilizer. '
    'Spray Chlorothalonil during high humidity periods. Monitor secondary infections closely.',
    NULL, 'rag-v1.2'   -- user has not yet rated this recommendation
),
(
    'REC00004',
    'Apply Imidacloprid 17.8% SL at 0.5ml/L or Thiamethoxam as systemic insecticide. '
    'Use neem-based organic sprays as preventive measure. Introduce natural predators. '
    'Spray during early morning when pest activity is highest. Repeat every 14 days.',
    4, 'rag-v1.3'
),
(
    'REC00005',
    'Apply Copper Hydroxide 77% WP at 3g/L to affected areas. '
    'Improve soil nutrition especially potassium and phosphorus. '
    'Prune heavily infected branches and dispose safely. '
    'Ensure good drainage and sunlight penetration into canopy.',
    3, 'rag-v1.3'
),
(
    'REC00006',
    'Follow-up treatment: Continue copper fungicide application at reduced frequency. '
    'Recovery showing 45% improvement from initial scan. '
    'Reduce spray interval to every 14 days. Monitor new flush growth closely. '
    'Consider soil pH adjustment if recovery plateaus below 80%.',
    5, 'rag-v1.3'
);


-- ============================================================
--  8. detection  (6 detections covering all 5 diseases)
--     disease_id mapping:
--       1 = Blister Blight
--       2 = Brown Blight
--       3 = Gray Blight
--       4 = Helopeltis
--       5 = Red Rust
-- ============================================================
INSERT INTO detection (
    detection_code, scan_id, disease_id, confidence_score, bounding_box,
    severity_level, lesion_count, healthy_leaf_area, affected_area,
    recovery_percentage, status, image_name
) VALUES
(
    'DET20250110001', 1, 1, 0.9245,
    '{"x": 120, "y": 85,  "w": 310, "h": 220, "polygon": [[120,85],[430,85],[430,305],[120,305]]}',
    'high', 12, 42.50, 57.50, 0.00, 'under_treatment',
    'scan_001_blister_blight_20250110.jpg'
),
(
    'DET20250115001', 2, 1, 0.8870,
    '{"x": 100, "y": 90,  "w": 280, "h": 200, "polygon": [[100,90],[380,90],[380,290],[100,290]]}',
    'medium', 7, 61.00, 39.00, 32.00, 'under_treatment',
    'scan_002_blister_blight_20250115.jpg'
),
(
    'DET20250205001', 3, 2, 0.9112,
    '{"x": 200, "y": 150, "w": 400, "h": 300, "polygon": [[200,150],[600,150],[600,450],[200,450]]}',
    'high', 18, 35.00, 65.00, 0.00, 'new',
    'scan_003_brown_blight_20250205.jpg'
),
(
    'DET20250220001', 4, 4, 0.8650,
    '{"x": 80,  "y": 60,  "w": 250, "h": 180, "polygon": [[80,60],[330,60],[330,240],[80,240]]}',
    'medium', 9, 55.25, 44.75, 0.00, 'new',
    'scan_004_helopeltis_20250220.jpg'
),
(
    'DET20250301001', 5, 5, 0.7890,
    '{"x": 150, "y": 100, "w": 320, "h": 240, "polygon": [[150,100],[470,100],[470,340],[150,340]]}',
    'low', 4, 78.00, 22.00, 0.00, 'new',
    'scan_005_red_rust_20250301.jpg'
),
(
    'DET20250315001', 6, 1, 0.9310,
    '{"x": 110, "y": 80,  "w": 290, "h": 210, "polygon": [[110,80],[400,80],[400,290],[110,290]]}',
    'low', 3, 82.50, 17.50, 72.00, 'recovered',
    'scan_006_blister_blight_followup_20250315.jpg'
);


-- ============================================================
--  9. applied_treatment  (link detections to recommendations)
-- ============================================================
INSERT INTO applied_treatment (detection_id, recommendation_id) VALUES
(1, 1),   -- Blister Blight (high severity)     → REC00001 (copper fungicide)
(2, 1),   -- Blister Blight (follow-up)         → REC00001 (same treatment continued)
(2, 6),   -- Blister Blight (follow-up)         → REC00006 (additional follow-up advice)
(3, 2),   -- Brown Blight                       → REC00002
(4, 4),   -- Helopeltis                         → REC00004 (insecticide)
(5, 5),   -- Red Rust                           → REC00005
(6, 6);   -- Blister Blight recovered           → REC00006 (recovery monitoring advice)


-- ============================================================
--  10. user_refresh_token  (active + revoked sessions)
-- ============================================================
INSERT INTO user_refresh_token (user_id, token_hash, device_info, latitude, longitude, expires_at, is_revoked) VALUES
(1, '$2b$12$tokenhashabc111dummy1', 'Chrome on Windows 11',  6.97085000, 80.78295000, NOW() + INTERVAL '30 days', FALSE),
(1, '$2b$12$tokenhashabc222dummy2', 'Safari on iPhone 15',   6.97085000, 80.78295000, NOW() + INTERVAL '30 days', FALSE),
(2, '$2b$12$tokenhashabc333dummy3', 'Chrome on Android',     5.94495000, 80.54560000, NOW() + INTERVAL '30 days', FALSE),
(3, '$2b$12$tokenhashabc444dummy4', 'Firefox on MacOS',      6.98945000, 81.05495000, NOW() + INTERVAL '30 days', FALSE),
(1, '$2b$12$tokenhashabc555dummy5', 'Chrome on Windows 10',  6.97085000, 80.78295000, NOW() - INTERVAL '5 days',  TRUE);
-- last row: expired and revoked — old session from Kamal's previous device

-- ============================================================
--  END OF SEED DATA
-- ============================================================
