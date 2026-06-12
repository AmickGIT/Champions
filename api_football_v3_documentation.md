# API-Football v3 — Complete API Documentation

> [!NOTE]
> This documentation was compiled from the official [API-Football v3 Documentation](https://www.api-football.com/documentation-v3). For the most up-to-date response schemas and live testing, use the [API-Football Dashboard](https://dashboard.api-football.com/).

---

## Overview

API-Football v3 is a RESTful API providing comprehensive football (soccer) data including fixtures, standings, player statistics, odds, and more. It covers **860+ competitions** across the globe.

---

## Base URL & Authentication

| Item | Value |
| :--- | :--- |
| **Base URL** | `https://v3.football.api-sports.io` |
| **HTTP Method** | `GET` only |
| **Auth Header** | `x-apisports-key: YOUR_API_KEY` |

### Example Request

```bash
curl -X GET "https://v3.football.api-sports.io/status" \
  -H "x-apisports-key: YOUR_API_KEY"
```

---

## Response Format

Every response follows this standardized JSON structure:

```json
{
  "get": "endpoint_name",
  "parameters": { "league": "39", "season": "2024" },
  "errors": [],
  "results": 20,
  "paging": {
    "current": 1,
    "total": 1
  },
  "response": [ ... ]
}
```

| Field | Type | Description |
| :--- | :--- | :--- |
| `get` | string | The endpoint that was called |
| `parameters` | object | The query parameters passed in the request |
| `errors` | array/object | Error messages (empty if successful) |
| `results` | integer | Number of records in the current response |
| `paging` | object | Pagination info (`current` page, `total` pages) |
| `response` | array | The actual data payload |

---

## Status Codes & Error Handling

| Status Code | Meaning |
| :--- | :--- |
| `200` | OK — Request successful |
| `401` | Unauthorized — Missing, invalid, or expired API key |
| `429` | Too Many Requests — Rate limit exceeded |
| `499` | Time Out — Server took too long |
| `500` | Internal Server Error — Server-side issue |

Errors are returned inside the `errors` field:
```json
{
  "errors": {
    "token": "Error/Missing application key. Go to https://www.api-football.com/documentation-v3 to learn how to get your API application key."
  }
}
```

---

## Pagination

Endpoints returning large datasets (e.g., `/players`, `/odds`) support pagination:

- Use the `page` query parameter: `?page=2`
- Check the `paging` object in the response for `current` and `total` pages
- Loop through pages until `current == total`

---

## Rate Limiting

Rate limits are enforced per subscription plan and tracked via response headers:

| Response Header | Description |
| :--- | :--- |
| `x-ratelimit-requests-limit` | Total daily request quota |
| `x-ratelimit-requests-remaining` | Remaining requests for the day |
| `X-RateLimit-Limit` | Maximum requests per minute |
| `X-RateLimit-Remaining` | Remaining requests before hitting the per-minute cap |

> [!TIP]
> Implement a backoff strategy when `X-RateLimit-Remaining` approaches 0 to avoid temporary blocks.

---

---

## Endpoints — Complete Reference

---

### 1. Core Data

---

#### `GET /status`

Check API server status and your account quota.

| Parameter | Required | Description |
| :--- | :--- | :--- |
| *(none)* | — | No parameters needed |

---

#### `GET /timezone`

Get the list of available timezones (used as the `timezone` param in `/fixtures`).

| Parameter | Required | Description |
| :--- | :--- | :--- |
| *(none)* | — | No parameters needed |

---

#### `GET /countries`

Get the list of available countries.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `name` | No | string | The name of the country |
| `code` | No | string | The country code (2 characters, e.g. `GB`, `FR`) |
| `search` | No | string | Search string for country name (≥ 3 characters) |

---

#### `GET /leagues`

Get the list of available leagues and cups.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `id` | No | integer | The league ID |
| `name` | No | string | The name of the league |
| `country` | No | string | The country name |
| `code` | No | string | The country code (2 chars) |
| `season` | No | integer | The season year (e.g. `2024`) |
| `team` | No | integer | The team ID |
| `type` | No | string | `league` or `cup` |
| `current` | No | string | `true` or `false` — current season only |
| `search` | No | string | Search string (≥ 3 characters) |
| `last` | No | integer | Last X seasons |

---

#### `GET /leagues/seasons`

Get the list of all available seasons.

| Parameter | Required | Description |
| :--- | :--- | :--- |
| *(none)* | — | No parameters needed |

---

#### `GET /venues`

Get venue/stadium information.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `id` | No | integer | The venue ID |
| `name` | No | string | The venue name |
| `city` | No | string | The city name |
| `country` | No | string | The country name |
| `search` | No | string | Search string (≥ 3 characters) |

---

### 2. Teams

---

#### `GET /teams`

Get team information. **At least one parameter is required.**

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `id` | No | integer | The team ID |
| `name` | No | string | The team name |
| `league` | No | integer | The league ID |
| `season` | No | integer | The season year |
| `country` | No | string | The country name |
| `code` | No | string | The team code (3 chars) |
| `venue` | No | integer | The venue ID |
| `search` | No | string | Search string (≥ 3 characters) |

---

#### `GET /teams/statistics`

Get detailed team statistics for a specific league and season.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `league` | **Yes** | integer | The league ID |
| `season` | **Yes** | integer | The season year |
| `team` | **Yes** | integer | The team ID |
| `date` | No | string | End date for stats (`YYYY-MM-DD`) |

---

#### `GET /teams/seasons`

Get the list of seasons available for a team.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `team` | **Yes** | integer | The team ID |

---

#### `GET /teams/countries`

Get list of countries where the team has played.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `team` | **Yes** | integer | The team ID |

---

### 3. Fixtures & Match Events

---

#### `GET /fixtures`

Get match fixtures. Supports extensive filtering.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `id` | No | integer | The fixture ID |
| `ids` | No | string | Multiple fixture IDs (e.g. `id1-id2-id3`) |
| `live` | No | string | `all` for all live matches, or specific league IDs |
| `date` | No | string | Specific date (`YYYY-MM-DD`) |
| `league` | No | integer | The league ID |
| `season` | No | integer | The season year |
| `team` | No | integer | The team ID |
| `last` | No | integer | Last X fixtures for a team |
| `next` | No | integer | Next X fixtures for a team |
| `from` | No | string | Start date (`YYYY-MM-DD`) |
| `to` | No | string | End date (`YYYY-MM-DD`) |
| `round` | No | string | The round name |
| `status` | No | string | Match status code (e.g. `NS`, `1H`, `HT`, `2H`, `FT`) |
| `venue` | No | integer | The venue ID |
| `timezone` | No | string | Timezone from `/timezone` endpoint |

> [!IMPORTANT]
> When querying by `id`, the response includes embedded `events`, `lineups`, `statistics`, and `players` data.

---

#### `GET /fixtures/headtohead`

Get head-to-head data between two teams.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `h2h` | **Yes** | string | Team IDs separated by dash: `TEAM1-TEAM2` (e.g. `33-34`) |
| `date` | No | string | Specific date (`YYYY-MM-DD`) |
| `league` | No | integer | The league ID |
| `season` | No | integer | The season year |
| `last` | No | integer | Last X meetings |
| `from` | No | string | Start date (`YYYY-MM-DD`) |
| `to` | No | string | End date (`YYYY-MM-DD`) |
| `status` | No | string | Match status |
| `venue` | No | integer | The venue ID |
| `timezone` | No | string | Timezone |

---

#### `GET /fixtures/statistics`

Get team statistics for a specific fixture.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `fixture` | **Yes** | integer | The fixture ID |
| `team` | No | integer | Filter by team ID |
| `type` | No | string | Statistic type (e.g. `Shots on Goal`) |

---

#### `GET /fixtures/events`

Get events for a specific fixture (goals, cards, subs, etc.).

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `fixture` | **Yes** | integer | The fixture ID |
| `team` | No | integer | Filter by team ID |
| `player` | No | integer | Filter by player ID |
| `type` | No | string | Event type: `Goal`, `Card`, `subst`, `Var` |

---

#### `GET /fixtures/lineups`

Get lineups for a specific fixture.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `fixture` | **Yes** | integer | The fixture ID |
| `team` | No | integer | Filter by team ID |
| `player` | No | integer | Filter by player ID |
| `type` | No | string | `startXI` or `substitutes` |

---

#### `GET /fixtures/players`

Get player statistics for a specific fixture.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `fixture` | **Yes** | integer | The fixture ID |
| `team` | No | integer | Filter by team ID |

---

#### `GET /fixtures/rounds`

Get the available rounds for a league season.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `league` | **Yes** | integer | The league ID |
| `season` | **Yes** | integer | The season year |
| `current` | No | boolean | `true` to return the current round only |

---

### 4. Standings

---

#### `GET /standings`

Get league standings/table.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `season` | **Yes** | integer | The season year |
| `league` | No | integer | The league ID |
| `team` | No | integer | The team ID |

> [!NOTE]
> At least one of `league` or `team` is required in addition to `season`.

---

### 5. Players

---

#### `GET /players`

Get player profiles and season statistics. **Paginated.**

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `id` | No | integer | The player ID |
| `team` | No | integer | The team ID |
| `league` | No | integer | The league ID |
| `season` | No | integer | The season year |
| `search` | No | string | Search by player name (≥ 4 characters) |
| `page` | No | integer | Page number for pagination |

---

#### `GET /players/seasons`

Get all available seasons for a player.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `player` | **Yes** | integer | The player ID |

---

#### `GET /players/squads`

Get the squad/roster for a team.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `team` | **Yes** | integer | The team ID |
| `player` | No | integer | The player ID |

---

#### `GET /players/topscorers`

Get top 20 scorers for a league season.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `league` | **Yes** | integer | The league ID |
| `season` | **Yes** | integer | The season year |

---

#### `GET /players/topassists`

Get top assist providers for a league season.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `league` | **Yes** | integer | The league ID |
| `season` | **Yes** | integer | The season year |

---

#### `GET /players/topyellowcards`

Get top yellow card recipients for a league season.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `league` | **Yes** | integer | The league ID |
| `season` | **Yes** | integer | The season year |

---

#### `GET /players/topredcards`

Get top red card recipients for a league season.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `league` | **Yes** | integer | The league ID |
| `season` | **Yes** | integer | The season year |

---

### 6. Advanced Entities

---

#### `GET /coachs`

Get coach information.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `id` | No | integer | The coach ID |
| `team` | No | integer | The team ID |
| `search` | No | string | Search by coach name (≥ 3 characters) |

---

#### `GET /transfers`

Get player transfer history.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `player` | No | integer | The player ID |
| `team` | No | integer | The team ID |

> [!NOTE]
> At least one of `player` or `team` is required.

---

#### `GET /trophies`

Get trophy information for a player or coach.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `player` | No | integer | The player ID |
| `coach` | No | integer | The coach ID |

> [!NOTE]
> At least one of `player` or `coach` is required.

---

#### `GET /sidelined`

Get sidelined (injured/suspended) information for a player or coach.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `player` | No | integer | The player ID |
| `coach` | No | integer | The coach ID |

> [!NOTE]
> At least one of `player` or `coach` is required.

---

#### `GET /injuries`

Get player injury information.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `league` | No | integer | The league ID |
| `season` | No | integer | The season year |
| `fixture` | No | integer | The fixture ID |
| `team` | No | integer | The team ID |
| `player` | No | integer | The player ID |
| `date` | No | string | Specific date (`YYYY-MM-DD`) |
| `timezone` | No | string | Timezone |

---

#### `GET /predictions`

Get match predictions and probability data.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `fixture` | **Yes** | integer | The fixture ID |

---

### 7. Odds & Betting

---

#### `GET /odds`

Get pre-match odds. **Paginated.**

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `fixture` | No | integer | The fixture ID |
| `league` | No | integer | The league ID |
| `season` | No | integer | The season year |
| `date` | No | string | Date (`YYYY-MM-DD`) |
| `timezone` | No | string | Timezone |
| `page` | No | integer | Page number |
| `bookmaker` | No | integer | Bookmaker ID |
| `bet` | No | integer | Bet/market ID |

---

#### `GET /odds/live`

Get in-play (live) odds.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `fixture` | No | integer | The fixture ID |
| `league` | No | integer | The league ID |
| `bet` | No | integer | Bet/market ID |

---

#### `GET /odds/live/bets`

Get available betting markets for live odds.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `id` | No | integer | The bet ID |
| `search` | No | string | Search for a market |

---

#### `GET /odds/bookmakers`

Get the list of available bookmakers.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `id` | No | integer | The bookmaker ID |
| `search` | No | string | Search by bookmaker name |

---

#### `GET /odds/bets`

Get the list of available bet types/markets.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `id` | No | integer | The bet ID |
| `search` | No | string | Search for a market name |

---

#### `GET /odds/mapping`

Get the mapping of fixtures with available odds.

| Parameter | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `page` | No | integer | Page number |

---

---

## Common Match Status Codes

| Short | Long | Description |
| :--- | :--- | :--- |
| `TBD` | Time To Be Defined | Scheduled but no time set |
| `NS` | Not Started | Match has not started |
| `1H` | First Half | First half in play |
| `HT` | Halftime | Halftime break |
| `2H` | Second Half | Second half in play |
| `ET` | Extra Time | Extra time in play |
| `P` | Penalty In Progress | Penalty shootout |
| `FT` | Match Finished | Full time |
| `AET` | Match Finished After Extra Time | Finished after extra time |
| `PEN` | Match Finished After Penalty | Finished after penalties |
| `BT` | Break Time | Break time (e.g. between extra time halves) |
| `SUSP` | Match Suspended | Match suspended |
| `INT` | Match Interrupted | Match interrupted |
| `PST` | Match Postponed | Match postponed |
| `CANC` | Match Cancelled | Match cancelled |
| `ABD` | Match Abandoned | Match abandoned |
| `AWD` | Technical Loss | Awarded technical loss |
| `WO` | WalkOver | Walk over |
| `LIVE` | In Progress | Currently live (covers `1H`, `HT`, `2H`, `ET`, `BT`, `P`) |

---

## Quick Reference — All Endpoints

| # | Endpoint | Category |
| :--- | :--- | :--- |
| 1 | `/status` | Core |
| 2 | `/timezone` | Core |
| 3 | `/countries` | Core |
| 4 | `/leagues` | Core |
| 5 | `/leagues/seasons` | Core |
| 6 | `/venues` | Core |
| 7 | `/teams` | Teams |
| 8 | `/teams/statistics` | Teams |
| 9 | `/teams/seasons` | Teams |
| 10 | `/teams/countries` | Teams |
| 11 | `/fixtures` | Fixtures |
| 12 | `/fixtures/headtohead` | Fixtures |
| 13 | `/fixtures/statistics` | Fixtures |
| 14 | `/fixtures/events` | Fixtures |
| 15 | `/fixtures/lineups` | Fixtures |
| 16 | `/fixtures/players` | Fixtures |
| 17 | `/fixtures/rounds` | Fixtures |
| 18 | `/standings` | Standings |
| 19 | `/players` | Players |
| 20 | `/players/seasons` | Players |
| 21 | `/players/squads` | Players |
| 22 | `/players/topscorers` | Players |
| 23 | `/players/topassists` | Players |
| 24 | `/players/topyellowcards` | Players |
| 25 | `/players/topredcards` | Players |
| 26 | `/coachs` | Entities |
| 27 | `/transfers` | Entities |
| 28 | `/trophies` | Entities |
| 29 | `/sidelined` | Entities |
| 30 | `/injuries` | Entities |
| 31 | `/predictions` | Entities |
| 32 | `/odds` | Odds |
| 33 | `/odds/live` | Odds |
| 34 | `/odds/live/bets` | Odds |
| 35 | `/odds/bookmakers` | Odds |
| 36 | `/odds/bets` | Odds |
| 37 | `/odds/mapping` | Odds |
