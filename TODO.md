# CricVision - New Features Progress

## Phase 1: ML Implementation
- [ ] Update requirements.txt (add tensorflow, mediapipe, opencv-python)
- [ ] Implement src/preprocess.py (MediaPipe video -> landmarks sequence)
- [ ] Create src/train.py (simple LSTM training)
- [ ] Train initial model -> models/shot_classifier.h5
- [ ] Update src/classify.py (load model, real predict)

## Phase 2: Upload Flow & DB
- [ ] Add DB models: Analysis, Player, Favorite (models/*.py or app.py)
- [ ] Update app.py /classify: real preprocess + classify + save Analysis
- [ ] Run db_init.py / migrations

## Phase 3: UI Enhancements
- [ ] Update templates/dashboard.html (upload form + results viz)
- [ ] Update templates/history.html (analysis list)
- [ ] Update templates/leaderboard.html (user stats)
- [ ] Add frontend/ charts (Recharts pie for shots)

## Phase 4: Test & Polish
- [ ] pip install -r requirements.txt
- [ ] python app.py
- [ ] Test upload/classify
- [ ] Browser verify

**Current Progress: Starting Phase 1**
