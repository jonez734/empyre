# Empyre Database Schema

This file documents the database schema for the Empyre empire building game. Both tables and views are documented since views are critical for the application layer.

## Schema Overview

The `empyre` schema contains base tables (prefixed with `__`) and public views that provide timezone-adjusted data to clients.

## Tables

### empyre.__player

Player accounts and game state.

| Column | Type | Constraints | Description |
|--------|------|-------------|--------------|
| membermoniker | citext | FK → engine.__member(moniker) | BBS member reference |
| moniker | citext | UNIQUE | Player name |
| datelastplayed | timestamptz | | Last play timestamp |
| datecreated | timestamptz | | Account creation timestamp |
| rank | bigint | | Player rank (0=Lord, 1=Prince, 2=King, 3=Emperor) |
| previousrank | bigint | | Previous rank before promotion |
| datepromoted | timestamptz | | Last promotion timestamp |
| turncount | bigint | | Turns played today |
| weatherconditions | bigint | | Current weather condition |
| soldierpromotioncount | bigint | | Number of soldier promotions |
| combatvictorycount | bigint | | Number of combat victories |
| beheaded | boolean | | Execution status |
| training | bigint | | Training level |
| taxrate | bigint | | Tax rate percentage (0-100) |
| resources | jsonb | | Game resources (coins, serfs, land, grain, soldiers, etc.) |

### empyre.__ship

Player-owned vessels.

| Column | Type | Constraints | Description |
|--------|------|-------------|--------------|
| moniker | citext | PK, UNIQUE | Ship name |
| playermoniker | citext | FK → empyre.__player(moniker) | Owner |
| location | text | | Current location |
| status | text | | Ship status |
| manifest | jsonb | | Cargo and passenger manifest |
| navigator | boolean | | Has navigator |
| kind | text | | Ship type (cargo, passenger, military) |
| datedocked | timestamptz | | When ship docked |
| datecreated | timestamptz | | Creation timestamp |
| createdbymoniker | citext | FK → engine.__member(moniker) | Creator |
| dateupdated | timestamptz | | Last update timestamp |
| updatedbymoniker | citext | FK → engine.__member(moniker) | Last updater |

### empyre.__island

Discovered islands available for colonization.

| Column | Type | Constraints | Description |
|--------|------|-------------|--------------|
| name | citext | PK, UNIQUE | Island name |
| playermoniker | citext | FK → empyre.__player(moniker) | Owner/claimant |
| resources | jsonb | | Island resources |
| status | text | | Island status |
| datediscovered | timestamptz | | Discovery timestamp |
| discoveredbymoniker | citext | FK → empyre.__player(moniker) | Discoverer |

### empyre.__colony

Player-established colonies on islands.

| Column | Type | Constraints | Description |
|--------|------|-------------|--------------|
| name | text | PK, UNIQUE | Colony name |
| foundermoniker | citext | FK → empyre.__player(moniker) | Colony founder |
| islandname | citext | FK → empyre.__island(name) | Location island |
| resources | jsonb | | Colony resources |
| datefounded | timestamptz | | Founding timestamp |
| status | text | | Colony status |

### empyre.__newsentry

Game news and event log.

| Column | Type | Constraints | Description |
|--------|------|-------------|--------------|
| id | bigserial | PK | Unique identifier |
| message | text | | News message |
| status | text | | Publication status |
| datecreated | timestamptz | | Creation timestamp |
| playermoniker | citext | FK → empyre.__player(moniker) | Related player |
| membermoniker | citext | FK → engine.__member(moniker) | BBS member |

### empyre.__mercs

Hired mercenary teams.

| Column | Type | Constraints | Description |
|--------|------|-------------|--------------|
| teammoniker | text | PK, UNIQUE | Team name |
| hiredbymoniker | citext | FK → empyre.__player(moniker) | Hiring player |
| price | bigint | | Hire price |
| quantity | bigint | | Number of mercenaries |
| contractstart | timestamptz | | Contract start |
| contractduration | interval | | Contract duration |

## Views

Views wrap base tables and provide timezone-adjusted timestamps based on the current user's preferences. All views join with `engine.__member` to obtain the user's timezone (`tz`).

### empyre.player

Wraps `empyre.__player` with timezone-adjusted timestamps.

| Column | Type | Description |
|--------|------|-------------|
| * | * | All columns from __player |
| datelastplayedlocal | timestamptz | User's local last played time |
| datepromotedlocal | timestamptz | User's local promotion time |

### empyre.ship

Wraps `empyre.__ship` with timezone-adjusted timestamps.

| Column | Type | Description |
|--------|------|-------------|
| * | * | All columns from __ship |
| datedockedlocal | timestamptz | User's local dock time |
| datecreatedlocal | timestamptz | User's local creation time |
| dateupdatedlocal | timestamptz | User's local update time |

### empyre.island

Wraps `empyre.__island` with timezone-adjusted timestamps.

| Column | Type | Description |
|--------|------|-------------|
| * | * | All columns from __island |
| datediscoveredlocal | timestamptz | User's local discovery time |

### empyre.colony

Wraps `empyre.__colony` with timezone-adjusted timestamps.

| Column | Type | Description |
|--------|------|-------------|
| * | * | All columns from __colony |
| datefoundedlocal | timestamptz | User's local founding time |

### empyre.newsentry

Wraps `empyre.__newsentry` for news display.

### empyre.mercs

Wraps `empyre.__mercs` with timezone-adjusted timestamps and computed contract end.

| Column | Type | Description |
|--------|------|-------------|
| * | * | All columns from __mercs |
| contractstartlocal | timestamptz | User's local contract start |
| contractend | timestamptz | Computed contract end (absolute) |
| contractendlocal | timestamptz | User's local contract end |

## SQL Files

The schema is split across multiple SQL files:

| File | Contents |
|------|----------|
| schema.sql | Schema creation and grants |
| player.sql | Player table and view |
| ship.sql | Ship table |
| shipview.sql | Ship view |
| island.sql | Island table and view |
| colony.sql | Colony table and view |
| newsentry.sql | News entry table and view |
| mercs.sql | Mercenaries table and view |
| empyre.sql | Master file that includes all above |

## Row Security

Views automatically filter data based on the current user via `CURRENT_USER` session variable, providing data isolation between players.
