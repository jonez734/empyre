# Empyre - Text-Based Empire Building Game Specification

## Project Overview

**Empyre** is a text-based empire building game designed to run on a Bulletin Board System (BBS). It is written in Python and uses the `bbsengine6` framework for terminal-based user interaction. Players build and manage their own empire by managing resources, expanding their territory, engaging in combat, and completing quests.

## Project Structure

```
empyre/src/empyre/
├── __init__.py              # Package initialization - runs main module
├── __main__.py             # CLI entry point
├── _version.py             # Version information (githash, datestamp)
├── main.py                 # Main game menu and player management
├── lib.py                  # Core game utilities and shared functions
├── player.py               # Player class and player management functions
├── play.py                 # Main game loop - turn processing
├── startup.py              # Initialization and database setup
├── instructions.py         # Display game instructions
├── playerstatus.py         # Display player status
├── shownews.py             # Display game news
├── weather.py              # Weather system module
├── disaster.py             # Natural disaster system module
├── harvest.py              # Harvest/grain management module
├── yearlyreport.py         # Annual financial report module
├── investments.py          # Investment/trading module
├── dock.py                 # Dock/port management module
├── shipyard.py             # Shipyard module
├── sail.py                 # Sailing module (stub)
├── sysopoptions.py        # Sysop/admin options module
├── generatenpc.py          # NPC generation utility
├── loadship.py            # Load ship with cargo
├── unloadship.py          # Unload ship cargo
├── install.py             # Installation module
├── quests.py-original     # Original quests module (backup)
├── sql/                   # SQL schema files
│   ├── __init__.py
│   ├── schema.sql         # Main schema creation
│   ├── empyre.sql        # Master SQL file (includes all)
│   ├── player.sql        # Player table definition
│   ├── island.sql        # Island table definition
│   ├── colony.sql        # Colony table definition
│   ├── ship.sql          # Ship table definition
│   ├── shipview.sql      # Ship view definition
│   ├── newsentry.sql    # News entries table
│   └── mercs.sql        # Mercenaries table
├── town/                  # Town activities submodule
│   ├── __init__.py
│   ├── lib.py            # Town module utilities
│   ├── main.py           # Town menu
│   ├── naturaldisasterbank.py  # Disaster bank
│   ├── lucifersden.py   # Lucifer's Den ( tavern)
│   ├── trainsoldiers.py # Train serfs to soldiers
│   ├── realtorsadvice.py # Land purchase advice
│   ├── juicebar.py      # Juice bar (stub)
│   ├── soldierpromotion.py # Promote soldiers to nobles
│   └── changetaxrate.py # Change tax rate
├── ship/                  # Ship management submodule
│   ├── __init__.py
│   ├── lib.py            # Ship utilities and Ship class
│   ├── main.py           # Ship management menu
│   ├── load.py           # Load cargo/passengers
│   ├── unload.py         # Unload cargo/passengers
│   ├── sail.py           # Sail to location
│   └── manifest.py      # Ship manifest (stub)
├── combat/                # Combat submodule
│   ├── __init__.py
│   ├── lib.py            # Combat utilities
│   ├── main.py           # Combat menu
│   ├── attackarmy.py     # Attack enemy army
│   ├── attackpalace.py   # Attack enemy palace
│   ├── attacknobles.py   # Attack nobles
│   ├── senddiplomat.py   # Send diplomat/spy
│   ├── joust.py          # Jousting
│   └── dragon.py         # Dragon combat
├── colony/                # Colony management submodule
│   ├── __init__.py
│   ├── lib.py            # Colony utilities
│   └── main.py           # Colony management
├── island/                # Island exploration submodule
│   ├── __init__.py
│   ├── lib.py            # Island utilities
│   └── main.py           # Island management
├── maint/                 # Maintenance/admin submodule
│   ├── __init__.py
│   ├── lib.py            # Maintenance utilities
│   ├── main.py           # Maintenance menu
│   ├── listplayers.py    # List all players
│   ├── resetempyre.py    # Reset empire
│   ├── scratchnews.py   # Manage news
│   └── mercs.py         # Manage mercenaries
├── quests/                # Quests submodule
│   ├── __init__.py
│   ├── lib.py            # Quest utilities
│   ├── main.py           # Quests menu
│   ├── module.py         # Quest module utilities
│   ├── raidpiratecamp.py # Raid pirate camp quest
│   ├── hauntedcave.py    # Haunted cave quest
│   └── zircon.py         # Zircon mage quest
└── data/                  # Game data files
    └── __init__.py
```

## Core Game Systems

### 1. Player Resources

Players manage the following resources:

| Resource | Default | Description |
|----------|---------|-------------|
| coins | 250,000 | Currency |
| serfs | 2,000 | Population/workers |
| land | 5,000 | Territory (acres) |
| grain | 20,000 | Food supply |
| soldiers | 40 | Military units |
| nobles | 3 | Nobility |
| palaces | 1 | residences |
| markets | 1 | Trade facilities |
| mills | 1 | Food processing |
| foundries | 2 | Manufacturing |
| shipyards | 0 | Ship construction |
| diplomats | 0 | Diplomatic agents |
| ships | 0 | Vessels |
| navigators | 0 | Ship crew |
| stables | 1 | Horse facilities |
| colonies | 0 | Overseas colonies |
| spices | 0 | Trade goods |
| cannons | 0 | Artillery |
| forts | 0 | Defense structures |
| dragons | 0 | Mythical units |
| horses | 0 | Mounts |
| timber | 0 | Building materials |
| rebels | 0 | Rebel units |
| exports | 0 | Trade exports |
| islands | 0 | Discovered islands |

### 2. Player Attributes

| Attribute | Default | Description |
|-----------|---------|-------------|
| moniker | None | Player name |
| membermoniker | None | BBS member name |
| rank | 0 | Player rank (0=Lord, 1=Prince, 2=King, 3=Emperor) |
| previousrank | 0 | Previous rank |
| turncount | 0 | Turns played today |
| soldierpromotioncount | 0 | Soldier promotions |
| datepromoted | None | Last promotion date |
| combatvictorycount | 0 | Combat victories |
| weatherconditions | 0 | Current weather |
| beheaded | False | Execution status |
| datelastplayed | None | Last play timestamp |
| taxrate | 15 | Tax rate percentage |
| training | 1 | Training level |

### 3. Turn Processing Flow

Each game turn executes the following modules in order:
1. **weather** - Determines weather conditions
2. **disaster** - Random disasters (plague, rats, earthquake, volcano, tidal wave)
3. **harvest** - Grain harvesting and distribution
4. **town** - Town activities (optional)
5. **combat** - Combat actions (optional)
6. **shipyard** - Ship building (optional)
7. **dock** - Ship management (optional)
8. **investments** - Buy/sell resources
9. **yearlyreport** - Annual financial summary

### 4. Rank System

Players advance through ranks based on their empire:
- **Lord** (rank 0): Starting rank
- **Prince** (rank 1): Requires markets≥10, diplomats>0, mills>5, foundries>1, shipyards>1, palaces>2, land/serfs>5.1, nobles>15, serfs>3000
- **King** (rank 2): Requires markets>15, mills≥10, diplomats>2, foundries>6, shipyards>4, palaces>6, land/serfs>10.5, serfs>3500, nobles>30
- **Emperor** (rank 3): Requires markets>23, mills≥10, foundries>13, shipyards>11, palaces>9, land/serfs>23.4, serfs≥2500

### 5. Weather System

Weather conditions affect gameplay:
| Value | Name | Effect |
|-------|------|--------|
| 1 | Poor | No rain, locusts migrate |
| 2 | Arid | Early frosts |
| 3 | Rain | Flash floods |
| 4 | Average | Good year |
| 5 | Long Summer | Fine weather |
| 6 | Fantastic | Great year! |

### 6. Disaster System

Random disasters (roll 1-12):
- **2**: Plague - kills serfs, soldiers, nobles
- **3**: Rats - consume grain
- **4**: Earthquake - destroy palaces, kill nobles
- **5**: Volcano - destroy markets, mills, foundries
- **6**: Tidal Wave - damage shipyards

### 7. Town Activities

Available town options:
- **Natural Disaster Bank**: Insurance against disasters
- **Lucifer's Den**: Tavern (stub)
- **Soldier Promotion**: Promote soldiers to nobles
- **Realtor's Advice**: Land purchase guidance
- **Change Tax Rate**: Adjust taxation (0-100%)
- **Train Serfs**: Convert serfs to soldiers
- **Player Status**: View current status

### 8. Combat System

Combat options:
- Attack Army
- Attack Palace
- Attack Nobles
- Send Diplomat (espionage)
- Joust (tournament)

### 9. Ship System

Ship management:
- Build ships (requires shipyards)
- Load cargo/passengers
- Unload cargo/passengers
- Sail to locations (mainland, islands)
- Ship types: Cargo, Passenger, Military

### 10. Quests System

Available quests:
- Raid the Pirate's Camp
- Mystery of the Haunted Cave
- Rescue the Maiden's Sister
- The Quest of the Gods
- Eradicate the Evil Cult
- Search for the Island of Spice
- Quest for the Legendary Bird City
- Look for the Mountain-Side Ship
- Seek Arch-Mage Zircon's Help

## Database Schema

### Tables

**empyre.__player**
- membermoniker (citext, FK to engine.__member)
- moniker (citext, unique)
- datelastplayed (timestamptz)
- datecreated (timestamptz)
- rank (bigint)
- previousrank (bigint)
- datepromoted (timestamptz)
- turncount (bigint)
- weatherconditions (bigint)
- soldierpromotioncount (bigint)
- combatvictorycount (bigint)
- beheaded (boolean)
- training (bigint)
- taxrate (bigint)
- resources (jsonb)

**empyre.__ship**
- moniker (citext, PK)
- playermoniker (citext, FK to empyre.__player)
- location (text)
- status (text)
- manifest (jsonb)
- navigator (boolean)
- kind (text)
- datedocked (timestamptz)
- datecreated (timestamptz)
- createdbymoniker (citext)
- dateupdated (timestamptz)
- updatedbymoniker (citext)

**empyre.__island**
- name (citext, PK)
- playermoniker (citext, FK)
- resources (jsonb)
- status (text)
- datediscovered (timestamptz)
- discoveredbymoniker (citext)

**empyre.__colony**
- name (text, PK)
- foundermoniker (citext, FK)
- islandname (citext, FK)
- resources (jsonb)
- datefounded (timestamptz)
- status (text)

**empyre.__newsentry**
- id (bigserial, PK)
- message (text)
- status (text)
- datecreated (timestamptz)
- playermoniker (citext)
- membermoniker (citext)

**empyre.__mercs**
- teammoniker (text, PK)
- hiredbymoniker (citext, FK)
- price (bigint)
- quantity (bigint)
- contractstart (timestamptz)
- contractduration (interval)

## Dependencies

- **bbsengine6**: BBS engine framework for terminal UI
- **psycopg2-binary**: PostgreSQL database driver
- **python-dateutil**: Date/time utilities

## Configuration

- Database: PostgreSQL (default: zoid6)
- Database host: localhost
- Database port: 5432
- Turns per day: 99
- Default tax rate: 15%

## Entry Points

- CLI: `python -m empyre`
- BBS Module: Integrated via bbsengine6
