# Zerodha old API key purge — 20260619_095049

## Issue
zlogin still generated login URL using old API key acd1...9syp after credential rotation.

## Action
- Searched old API key in shell/config/secret/login areas
- Backed up hit files
- Replaced old key with new key
- Forced primary Zerodha env files to new key/user/secret
- Cleared old access/request tokens
- Scrubbed shared tokens.json to new broker/api_key/user_id only
- Verified old key no longer appears in searched locations

## Safety
- runtime stopped
- no feeds/features/strategy/risk/execution started
- no paper/live enabled
- orders_xlen checked
