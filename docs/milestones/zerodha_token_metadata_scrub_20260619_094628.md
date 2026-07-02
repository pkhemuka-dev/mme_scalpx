# Zerodha token metadata scrub — 20260619_094628

## Purpose
Removed stale old Zerodha session metadata after API key rotation.

## Removed
- old metadata block
- old public_token
- old session_id
- old issued_at/login/session fields
- old token/session material

## Preserved
- broker=zerodha
- new api_key
- new user_id=PES178

## Next
Run fresh login:
```bash
source ~/.bashrc
zlogin
plogin
```
