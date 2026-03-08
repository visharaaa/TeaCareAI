-- ============================================================
--  Tea Disease Analysis System — Test Seed Data
--  Insert order follows FK dependency chain
-- ============================================================

-- ============================================================
--  1. users  (4 users — different roles)
-- ============================================================
INSERT INTO users (user_code, user_name, email, password, user_type) VALUES
    ('USR00001', 'Kamal Perera',    'kamal.perera@teaplant.lk', '$2b$12$dummyhash1', 'farmer'),
    ('USR00002', 'Nimal Silva',     'nimal.silva@teaplant.lk',  '$2b$12$dummyhash2', 'farmer'),
    ('USR00003', 'Dr. Suneth Dias', 'suneth.dias@agro.lk',      '$2b$12$dummyhash3', 'agronomist'),
    ('USR00004', 'Admin User',      'admin@teaplant.lk',        '$2b$12$dummyhash4', 'admin'),
    ('USR00005', 'Ruwan Fernando',  'ruwan.fernando@teaplant.lk','$2b$12$dummyhash5', 'farmer'),
    ('USR00006', 'Dilini Jayawardena','dilini.j@agro.lk',       '$2b$12$dummyhash6', 'agronomist'),
    ('USR00007', 'State Officer 01','state01@gov.lk',           '$2b$12$dummyhash7', 'state'),
    ('USR00008', 'Chamara Bandara', 'chamara.b@teaplant.lk',    '$2b$12$dummyhash8', 'farmer');

-- ============================================================
--  2. field  (8 fields — Sri Lanka locations)
-- ============================================================
INSERT INTO field (field_name, field_latitude, field_longitude, field_elevation, tea_variety, plant_age_in_years) VALUES
    ('Nuwara Eliya Block A',  6.97080000,  80.78290000, 1868.00, 'Ceylon High Grown',  8.5),
    ('Kandy Estate Block B',  7.29430000,  80.63500000, 1200.00, 'Assam Hybrid',        5.0),
    ('Matara Lowland Block',  5.94490000,  80.54550000,   30.00, 'Ceylon Low Grown',   12.0),
    ('Badulla Hill Block C',  6.98940000,  81.05490000, 1400.00, 'Uva Variety',         3.5),
    ('Hatton Block D',        6.89420000,  80.59310000, 1600.00, 'Ceylon High Grown',   6.0),
    ('Galle Coastal Block',   6.03380000,  80.21700000,   15.00, 'Ceylon Low Grown',   10.0),
    ('Ella Highland Block',   6.86750000,  81.04600000, 1050.00, 'Uva Variety',         4.5),
    ('Dimbula Valley Block',  6.92100000,  80.64800000, 1500.00, 'Assam Hybrid',        7.0);

-- ============================================================
--  3. ownership
-- ============================================================
INSERT INTO ownership (user_id, field_id) VALUES
    (1, 1),  -- Kamal owns Nuwara Eliya Block A
    (1, 2),  -- Kamal also owns Kandy Estate Block B
    (2, 3),  -- Nimal owns Matara Lowland Block
    (3, 4),  -- Dr. Suneth owns Badulla Hill Block C
    (5, 5),  -- Ruwan owns Hatton Block D
    (5, 6),  -- Ruwan also owns Galle Coastal Block
    (8, 7),  -- Chamara owns Ella Highland Block
    (8, 8);  -- Chamara also owns Dimbula Valley Block

-- ============================================================
--  4. disease  (5 tea diseases)
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
    );

-- ============================================================
--  5. scan_history_chat  (12 scan sessions)
-- ============================================================
INSERT INTO scan_history_chat (chat_code, chat_created_timestamp, latitude, longitude, elevation) VALUES
    ('CHAT00001', '2025-01-10 08:30:00+05:30', 6.97085000,  80.78295000, 1869.00),  -- Nuwara Eliya initial
    ('CHAT00002', '2025-01-15 09:15:00+05:30', 6.97090000,  80.78300000, 1870.00),  -- Nuwara Eliya follow-up
    ('CHAT00003', '2025-02-05 10:00:00+05:30', 7.29435000,  80.63505000, 1201.00),  -- Kandy
    ('CHAT00004', '2025-02-20 14:30:00+05:30', 5.94495000,  80.54560000,   31.00),  -- Matara
    ('CHAT00005', '2025-03-01 07:45:00+05:30', 6.98945000,  81.05495000, 1401.00),  -- Badulla
    ('CHAT00006', '2025-03-15 11:00:00+05:30', 6.97088000,  80.78298000, 1868.50),  -- Nuwara Eliya recovery
    ('CHAT00007', '2025-03-20 08:00:00+05:30', 6.89425000,  80.59315000, 1601.00),  -- Hatton initial
    ('CHAT00008', '2025-04-01 09:30:00+05:30', 6.89430000,  80.59320000, 1602.00),  -- Hatton follow-up
    ('CHAT00009', '2025-04-05 10:15:00+05:30', 6.03385000,  80.21705000,   16.00),  -- Galle
    ('CHAT00010', '2025-04-10 07:30:00+05:30', 6.86755000,  81.04605000, 1051.00),  -- Ella
    ('CHAT00011', '2025-04-15 08:45:00+05:30', 6.92105000,  80.64805000, 1501.00),  -- Dimbula initial
    ('CHAT00012', '2025-04-28 09:00:00+05:30', 6.92110000,  80.64810000, 1502.00);  -- Dimbula follow-up

-- ============================================================
--  6. user_scan_history
-- ============================================================
INSERT INTO user_scan_history (user_id, field_id, scan_id) VALUES
    (1, 1,  1),   -- Kamal: Nuwara Eliya — initial
    (1, 1,  2),   -- Kamal: Nuwara Eliya — follow-up
    (1, 2,  3),   -- Kamal: Kandy Estate
    (2, 3,  4),   -- Nimal: Matara Lowland
    (3, 4,  5),   -- Dr. Suneth: Badulla Hill
    (1, 1,  6),   -- Kamal: Nuwara Eliya — recovery
    (5, 5,  7),   -- Ruwan: Hatton — initial
    (5, 5,  8),   -- Ruwan: Hatton — follow-up
    (5, 6,  9),   -- Ruwan: Galle Coastal
    (8, 7, 10),   -- Chamara: Ella Highland
    (8, 8, 11),   -- Chamara: Dimbula — initial
    (8, 8, 12);   -- Chamara: Dimbula — follow-up

-- ============================================================
--  7. treatment_recommendation  (10 RAG-generated)
-- ============================================================
INSERT INTO treatment_recommendation (recommendation_code, generated_advice, feedback_score, model_version) VALUES
    (
        'REC00001',
        'Apply copper-based fungicide (Copper Oxychloride 50% WP) at 3g/L every 7-10 days during flushing. Ensure adequate shade regulation to reduce humidity. Remove and destroy severely infected shoots. Improve air circulation by pruning. Apply systemic fungicide (Hexaconazole) as curative treatment.',
        5, 'rag-v1.2'
    ),
    (
        'REC00002',
        'Apply Carbendazim 50% WP at 1g/L or Thiophanate-methyl as foliar spray. Drain waterlogged areas around plants. Remove infected plant debris promptly. Avoid overhead irrigation. Consider resistant variety replanting for severely affected zones.',
        4, 'rag-v1.2'
    ),
    (
        'REC00003',
        'Apply Mancozeb 75% WP at 2.5g/L as protective spray. Remove and burn infected leaves. Improve drainage and reduce nitrogen fertilizer. Spray Chlorothalonil during high humidity periods. Monitor secondary infections closely.',
        NULL, 'rag-v1.2'
    ),
    (
        'REC00004',
        'Apply Imidacloprid 17.8% SL at 0.5ml/L or Thiamethoxam as systemic insecticide. Use neem-based organic sprays as preventive measure. Introduce natural predators. Spray during early morning when pest activity is highest. Repeat every 14 days.',
        4, 'rag-v1.3'
    ),
    (
        'REC00005',
        'Apply Copper Hydroxide 77% WP at 3g/L to affected areas. Improve soil nutrition especially potassium and phosphorus. Prune heavily infected branches and dispose safely. Ensure good drainage and sunlight penetration into canopy.',
        3, 'rag-v1.3'
    ),
    (
        'REC00006',
        'Follow-up treatment: Continue copper fungicide application at reduced frequency. Recovery showing 45% improvement from initial scan. Reduce spray interval to every 14 days. Monitor new flush growth closely. Consider soil pH adjustment if recovery plateaus below 80%.',
        5, 'rag-v1.3'
    ),
    (
        'REC00007',
        'Apply Propiconazole 25% EC at 1ml/L as systemic fungicide for Gray Blight control. Remove and destroy all infected leaf litter. Avoid wounding plants during harvesting. Apply preventive Bordeaux mixture during wet seasons. Increase potassium fertilizer to boost plant immunity.',
        4, 'rag-v1.3'
    ),
    (
        'REC00008',
        'Immediate action: Isolate severely affected blocks. Apply Chlorpyrifos 20% EC at 2ml/L for Helopeltis control. Install yellow sticky traps to monitor pest population. Prune and burn wilted shoots. Schedule follow-up inspection in 10 days.',
        5, 'rag-v1.4'
    ),
    (
        'REC00009',
        'Apply Trifloxystrobin + Tebuconazole at recommended dosage for combined fungal control. Improve field drainage urgently. Conduct soil pH test and adjust to 4.5-5.5 optimal range. Increase spacing between plants to improve air circulation.',
        NULL, 'rag-v1.4'
    ),
    (
        'REC00010',
        'Recovery monitoring: Disease progression halted. Maintain preventive copper spray schedule monthly. Continue soil nutrition program with balanced NPK. Record new flush growth rate weekly. Escalate to agronomist if affected area increases beyond 10%.',
        4, 'rag-v1.4'
    );

-- ============================================================
--  8. detection  (12 detections — all 5 diseases covered)
--     disease_id: 1=Blister Blight  2=Brown Blight  3=Gray Blight
--                 4=Helopeltis      5=Red Rust
-- ============================================================
INSERT INTO detection (
    detection_code, scan_id, disease_id, confidence_score, bounding_box,
    severity_level, lesion_count, healthy_leaf_area, affected_area,
    recovery_percentage, status, image_name
) VALUES
    (
        'DET20250110001', 1, 1, 0.9245,
        '{"x":120,"y":85,"w":310,"h":220,"polygon":[[120,85],[430,85],[430,305],[120,305]]}',
        'high', 12, 42.50, 57.50, 0.00, 'under_treatment',
        'scan_001_blister_blight_20250110.jpg'
    ),
    (
        'DET20250115001', 2, 1, 0.8870,
        '{"x":100,"y":90,"w":280,"h":200,"polygon":[[100,90],[380,90],[380,290],[100,290]]}',
        'medium', 7, 61.00, 39.00, 32.00, 'under_treatment',
        'scan_002_blister_blight_20250115.jpg'
    ),
    (
        'DET20250205001', 3, 2, 0.9112,
        '{"x":200,"y":150,"w":400,"h":300,"polygon":[[200,150],[600,150],[600,450],[200,450]]}',
        'high', 18, 35.00, 65.00, 0.00, 'new',
        'scan_003_brown_blight_20250205.jpg'
    ),
    (
        'DET20250220001', 4, 4, 0.8650,
        '{"x":80,"y":60,"w":250,"h":180,"polygon":[[80,60],[330,60],[330,240],[80,240]]}',
        'medium', 9, 55.25, 44.75, 0.00, 'new',
        'scan_004_helopeltis_20250220.jpg'
    ),
    (
        'DET20250301001', 5, 5, 0.7890,
        '{"x":150,"y":100,"w":320,"h":240,"polygon":[[150,100],[470,100],[470,340],[150,340]]}',
        'low', 4, 78.00, 22.00, 0.00, 'new',
        'scan_005_red_rust_20250301.jpg'
    ),
    (
        'DET20250315001', 6, 1, 0.9310,
        '{"x":110,"y":80,"w":290,"h":210,"polygon":[[110,80],[400,80],[400,290],[110,290]]}',
        'low', 3, 82.50, 17.50, 72.00, 'recovered',
        'scan_006_blister_blight_followup_20250315.jpg'
    ),
    (
        'DET20250320001', 7, 3, 0.8540,
        '{"x":90,"y":70,"w":260,"h":190,"polygon":[[90,70],[350,70],[350,260],[90,260]]}',
        'medium', 11, 52.00, 48.00, 0.00, 'under_treatment',
        'scan_007_gray_blight_20250320.jpg'
    ),
    (
        'DET20250401001', 8, 3, 0.8120,
        '{"x":85,"y":65,"w":240,"h":175,"polygon":[[85,65],[325,65],[325,240],[85,240]]}',
        'low', 6, 68.00, 32.00, 38.00, 'under_treatment',
        'scan_008_gray_blight_20250401.jpg'
    ),
    (
        'DET20250405001', 9, 4, 0.9005,
        '{"x":175,"y":130,"w":350,"h":260,"polygon":[[175,130],[525,130],[525,390],[175,390]]}',
        'high', 22, 28.75, 71.25, 0.00, 'escalated',
        'scan_009_helopeltis_20250405.jpg'
    ),
    (
        'DET20250410001', 10, 2, 0.8330,
        '{"x":130,"y":95,"w":300,"h":220,"polygon":[[130,95],[430,95],[430,315],[130,315]]}',
        'medium', 8, 58.50, 41.50, 0.00, 'new',
        'scan_010_brown_blight_20250410.jpg'
    ),
    (
        'DET20250415001', 11, 5, 0.7650,
        '{"x":95,"y":75,"w":270,"h":200,"polygon":[[95,75],[365,75],[365,275],[95,275]]}',
        'low', 5, 74.00, 26.00, 0.00, 'new',
        'scan_011_red_rust_20250415.jpg'
    ),
    (
        'DET20250428001', 12, 5, 0.8210,
        '{"x":88,"y":68,"w":255,"h":185,"polygon":[[88,68],[343,68],[343,253],[88,253]]}',
        'low', 3, 81.00, 19.00, 55.00, 'recovered',
        'scan_012_red_rust_20250428.jpg'
    );

-- ============================================================
--  9. applied_treatment
-- ============================================================
INSERT INTO applied_treatment (detection_id, recommendation_id) VALUES
    (1,  1),   -- Blister Blight high          → copper fungicide
    (2,  1),   -- Blister Blight follow-up     → same treatment continued
    (2,  6),   -- Blister Blight follow-up     → follow-up advice
    (3,  2),   -- Brown Blight                 → Carbendazim spray
    (4,  4),   -- Helopeltis Matara            → insecticide
    (5,  5),   -- Red Rust Badulla             → Copper Hydroxide
    (6,  6),   -- Blister Blight recovered     → recovery monitoring
    (7,  7),   -- Gray Blight initial          → Propiconazole
    (8,  7),   -- Gray Blight follow-up        → same treatment
    (8,  10),  -- Gray Blight follow-up        → recovery monitoring
    (9,  8),   -- Helopeltis escalated         → immediate action plan
    (9,  4),   -- Helopeltis escalated         → insecticide (combined)
    (10, 2),   -- Brown Blight Ella            → Carbendazim spray
    (10, 9),   -- Brown Blight Ella            → combined fungal control
    (11, 5),   -- Red Rust Dimbula initial     → Copper Hydroxide
    (12, 10);  -- Red Rust Dimbula recovered   → recovery monitoring

-- ============================================================
--  10. user_refresh_token
-- ============================================================
INSERT INTO user_refresh_token (user_id, token_hash, device_info, latitude, longitude, expires_at, is_revoked) VALUES
    (1, '$2b$12$tokenhashabc111dummy1', 'Chrome on Windows 11',  6.97085000, 80.78295000, NOW() + INTERVAL '30 days', FALSE),
    (1, '$2b$12$tokenhashabc222dummy2', 'Safari on iPhone 15',   6.97085000, 80.78295000, NOW() + INTERVAL '30 days', FALSE),
    (2, '$2b$12$tokenhashabc333dummy3', 'Chrome on Android',     5.94495000, 80.54560000, NOW() + INTERVAL '30 days', FALSE),
    (3, '$2b$12$tokenhashabc444dummy4', 'Firefox on MacOS',      6.98945000, 81.05495000, NOW() + INTERVAL '30 days', FALSE),
    (1, '$2b$12$tokenhashabc555dummy5', 'Chrome on Windows 10',  6.97085000, 80.78295000, NOW() - INTERVAL '5 days',  TRUE),   -- expired + revoked
    (5, '$2b$12$tokenhashabc666dummy6', 'Samsung Browser Android',6.89425000,80.59315000, NOW() + INTERVAL '30 days', FALSE),
    (5, '$2b$12$tokenhashabc777dummy7', 'Chrome on iPhone 14',   6.89425000, 80.59315000, NOW() - INTERVAL '2 days',  TRUE),   -- expired + revoked
    (8, '$2b$12$tokenhashabc888dummy8', 'Firefox on Windows 11', 6.86755000, 81.04605000, NOW() + INTERVAL '30 days', FALSE),
    (6, '$2b$12$tokenhashabc999dummy9', 'Chrome on MacOS',       6.98945000, 81.05495000, NOW() + INTERVAL '30 days', FALSE),
    (7, '$2b$12$tokenhashabcaaadummy0', 'Edge on Windows 11',    6.97085000, 80.78295000, NOW() + INTERVAL '30 days', FALSE);

-- ============================================================
--  END OF SEED DATA
-- ============================================================