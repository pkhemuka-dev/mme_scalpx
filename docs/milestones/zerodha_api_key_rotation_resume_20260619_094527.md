# Zerodha API key rotation resume — 20260619_094527

## Status
Credential update resumed after earlier Python env KeyError caused by non-exported Bash variables.

## Updated
- Zerodha credentials/session env files
- shared/tokens.json with broker=zerodha, new api_key/user_id
- old access/request tokens cleared to force fresh login
- project env files updated where existing Zerodha/Kite keys were present

## Safety
- runtime verified stopped
- no feeds/features/strategy/risk/execution started
- no paper/live enabled
- no broker/order path started
- proofs are redacted

## Required next step
Run fresh login:
```bash
source ~/.bashrc
zlogin
plogin
```

Then:
```bash
pfeeds --force-all
pfeedcheck
```
