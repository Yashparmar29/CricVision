# TODO List - Fix Match Index Functionality

## Phase 1: Update app.py
- [x] Add match data structure with Indian and International matches
- [x] Add API endpoint `/api/matches` to get all matches grouped by category
- [x] Add API endpoint `/api/matches/<match_id>` to get specific match details
- [x] Update `/match/<match_id>` route to fetch and pass match data to template

## Phase 2: Update templates/match.html
- [ ] Add match selection UI with Indian/International tabs
- [ ] Add match list display for each category
- [ ] Update JavaScript to fetch match data from API
- [ ] Make the page dynamic based on match_id

## Phase 3: Update templates/base.html
- [ ] Add "Matches" link in navigation

## Phase 4: Testing
- [ ] Test the match selection functionality
- [ ] Verify Indian and International matches are displayed correctly
- [ ] Verify clicking on different matches shows correct data
