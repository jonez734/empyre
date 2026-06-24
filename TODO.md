# TODO

- [ ] Make sure all trades route through the bank
- [ ] Check quests to make sure they route through the bank

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
