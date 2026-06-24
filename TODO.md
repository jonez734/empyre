# TODO

- [ ] Make sure all trades route through the bank
- [x] Check quests to make sure they route through the bank
- [ ] Check all empyre modules for direct manipulation of player.coins or member.coins

## Plan: Check Quests Bank Routing

### Goal
Ensure all empyre quests that involve coin transactions route through the bank instead of directly manipulating `player.coins`.

### Current State
Quests with direct coin manipulation found:
- `quests/raidpiratecamp.py:33` - `player.coins += 30000`
- `quests/zircon.py:30` - `player.coins += 30000`
- `quests/zircon.py:165` - `player.coins -= coins`

### Implementation Steps

**1. Create validation test** (`src/tests/test_quests_bank_routing.py`)
- Scan all quest files in `empyre/quests/` directory
- Use regex/AST to detect direct `player.coins` manipulation (`+=`, `-=`, `= ... +`, `= ... -`)
- Verify coin operations use `bank.BankService.add_funds()` or `remove_funds()` instead
- Fail with clear error messages showing violators

**2. Run validation** to identify all quests needing updates

**3. Fix each quest file**
- Import `bank.BankService` from bbsengine6
- Replace `player.coins += X` with `bank_service.add_funds(player.moniker, X, "quest_reward", "...")`
- Replace `player.coins -= X` with `bank_service.remove_funds(player.moniker, X, "quest_cost", "...")`
- Call `player.coins = bank_service.get_balance(player.moniker)` after bank ops

**4. Run tests** to verify all quests pass validation

### Files to Modify
1. `src/tests/test_quests_bank_routing.py` (new)
2. `src/empyre/quests/raidpiratecamp.py`
3. `src/empyre/quests/zircon.py`

## Plan: Check All Modules for Coins Manipulation

### Goal
Audit all empyre modules for direct manipulation of `player.coins` or `member.coins` and route them through the bank.

### Known Files with Direct Manipulation
- `player.py:756` - `self.coins -= a`
- `town/naturaldisasterbank.py:62` - `player.coins += amount * exchangerate`
- `ship/lib.py:290` - `player.coins -= nav["price"]`
- `combat/joust.py:87,91` - `player.coins += 1000` / `-= 1000`
- `town/lucifersden.py:100,103` - `player.coins += bet * odds` / `+= bet`
- `yearlyreport.py:162,163` - `player.coins += receivables` / `-= payables`
- (quests fixed above)

### Implementation Steps

**1. Create validation test** (`src/tests/test_all_coins_routing.py`)
- Scan all Python files in `src/empyre/` (excluding test files)
- Use AST to detect direct manipulation of `player.coins` and `member.coins`
- Allow `player.coins = bank_service.get_balance(...)` as valid sync pattern
- Generate report of all violations

**2. Run validation** to identify all modules needing updates

**3. Categorize each violation**
- Must route through bank (trades, purchases, gambling, etc.)
- Can remain direct (e.g., yearly report calculations, disaster bank exchange rate)
- Document rationale for each decision

**4. Fix each module** as appropriate

**5. Run tests** to verify all modules pass validation

### Files to Modify
1. `src/tests/test_all_coins_routing.py` (new)
2. Various empyre modules as identified

## Plan: Route All Trades Through the Bank

### Goal
Route all coin transactions (buying/selling) through the bank system while keeping `player.coins` as a cached value synced with the bank for backward compatibility.

### Current State
- `lib.trade()` directly modifies `player.coins` at lines 308 (buy) and 327 (sell)
- `BankService` in bbsengine6 provides `add_funds()` and `remove_funds()` with transaction logging
- 52+ places in codebase use `player.coins` directly

### Implementation Steps

**1. Add config for trade fee**
- Add `trade_fee` to empyre config (default: 0)
- Location: likely `src/empyre/config.py` or similar

**2. Add bank sync helpers to `lib.py`**
```python
def get_player_coins(player) -> int:
    """Get coins from bank, fallback to cached player.coins"""
    
def sync_player_coins(player) -> None:
    """Sync player.coins from bank balance"""
```

**3. Modify `player.py` to sync on load/save**
- In `load()`: After building player, sync coins from bank to `player.coins`
- In `save()`: After saving, optionally sync to bank (or trust runtime updates)

**4. Modify `lib.trade()` to route through bank**
- Import `BankService` from bbsengine6
- On **buy**: `bank.remove_funds(moniker, total, "purchase", f"Bought {qty} {name}")`
- On **sell**: `bank.add_funds(moniker, total, "sale", f"Sold {qty} {name}")`
- Apply fee if configured (deduct from transaction or add to cost)
- Update `player.coins` cache after bank operation

**5. Update other coin-handling code**
- Review all 52+ usages of `player.coins`:
  - `ship/lib.py` (navigators purchase) - route through bank
  - `town/naturaldisasterbank.py` - already uses bank, just sync cache
  - `combat/joust.py`, `town/lucifersden.py`, etc. - decide per-case

**6. Testing**
- Run existing tests in `src/tests/test_lib.py`
- Verify `player.coins` displays correctly in UI after bank operations

### Files to Modify
1. `src/empyre/lib.py` - Core trade logic + helper functions
2. `src/empyre/player.py` - Load/save sync
3. Config file - Add `trade_fee` setting

### Backward Compatibility
- `player.coins` remains as cached value
- Display shows `player.coins` (synced from bank)
- All existing code continues to work
