# Champions - Project Documentation

## Overview
**Champions** is a custom FIFA World Cup 2026 fantasy web application designed for a private group of friends. It features squad building, real-time snake drafting, betting, and a silent auction mechanism for eliminated players. 

The project is split into two parts:
- **Backend:** Django + Django REST Framework (Python)
- **Frontend:** Next.js + TailwindCSS + React (TypeScript)

---

## 1. What Has Been Built So Far (Phase 1)

The backend foundation is 100% complete. All core services and data models have been built, integrated with SQLite, and are ready for API consumption.

### Core Architecture & Settings
- **Project Structure:** Standard Django project configured in `backend/champions`.
- **Authentication:** Integrated SimpleJWT for secure API authentication and cross-origin resource sharing (CORS) configured for frontend communication.
- **Game Config:** Global constants defined in `settings.GAME_CONFIG` (e.g., initial budgets, bench multipliers, transfer penalties, and World Cup constants).

### App Modules
1. **Accounts App (`backend/accounts`)**
   - Implemented `UserProfile` linked to Django's native `User` model.
   - Handles tracking of the user's `balance` (starting at $10M) and total fantasy points.

2. **Core App (`backend/core`)**
   - **Models:** `Country`, `Player`, `Fixture`, and `PlayerMatchStats`.
   - **API-Football Client (`api_client.py`):** Service layer to interact with the API-Football v3 endpoints (seeded teams, player rosters, live fixtures, and stats).
   - **Scoring Engine (`scoring.py`):** Logic that maps real-world match events (goals, assists, clean sheets, tackles) into our custom fantasy points system based on player position (GK, DEF, MID, FWD).

3. **Squad App (`backend/squad`)**
   - **Models:** `Squad` and `SquadPlayer`.
   - Allows users to maintain a 16-player squad (11 starters, 5 bench).
   - Includes formation validation logic (e.g., ensuring a 4-3-3 has exactly 4 DEFs, 3 MIDs, and 3 FWDs) and slot assignments.
   - Calculates dynamic team totals where bench players receive a reduced point modifier (50%).

4. **Draft App (`backend/draft`)**
   - Contains the real-time **Snake Draft** logic (`services.py`).
   - Generates the draft order, enforces the strict 1-player-per-country rule for each user, and tracks pick deadlines.
   - Provides a polling endpoint (`/api/draft/state/`) for the frontend to sync live without WebSockets.
   - Implements an "Auto-Pick" fallback for missed turns.

5. **Betting App (`backend/betting`)**
   - **Models:** `BettingOdds` and `Bet`.
   - Fetches pre-match odds (Match Winner & Exact Score) from the API.
   - Deducts stake from user balances and credits payouts upon match resolution via the `resolve_bets_for_fixture` service.

6. **Transfers App (`backend/transfers`)**
   - Handles buying, selling, and swapping players in the open market subject to country constraints and roster caps.
   - **Silent Auction System:** Triggers when a country is eliminated from the World Cup. Users are compensated for their eliminated players at a percentage of their market value. Eliminated players are released to the pool, and an auction opens where users place hidden bids.
   - Comprehensive `Transaction` ledger mapping all financial flows (bets, transfers, compensation).

---

## 2. Next Steps (Phase 2 & 3)

The immediate next phase revolves entirely around building the user interfaces to consume the backend APIs.

### Phase 2: Frontend (Next.js)
The basic Next.js app has been initialized with TailwindCSS.
- **Design System:** Implement the "Premium Dark & Gold" aesthetic with smooth transitions (Framer Motion) and modern UI elements.
- **Authentication Pages:** Login and Registration screens that capture JWTs.
- **Dashboard View:** Showing the global leaderboard and upcoming real-world fixtures.
- **The Draft Room:** A dynamic, polling UI where friends can watch picks happen live and see the countdown clock.
- **Pitch / Squad View:** A visual soccer pitch layout to map the user's drafted squad, allowing them to drag/drop or click to swap starters with the bench.
- **Betting Interface:** A sportsbook-style UI to browse fixtures, see odds, and place stakes.
- **Transfers Market & Auctions:** A table/grid to browse available players and submit hidden bids for active auctions.

### Phase 3: Live Deployment & Seeding
- Configure the production PostgreSQL database via **Supabase**.
- Deploy the Django backend via **Render**.
- Deploy the Next.js frontend via **Vercel**.
- Run the one-time sync scripts to populate the database with the real World Cup 2026 data via API-Football.
