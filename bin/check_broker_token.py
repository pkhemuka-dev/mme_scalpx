from __future__ import annotations

import sys

from app.mme_scalpx.integrations.bootstrap_quote import fetch_underlying_ltp, QuoteFetchError

QUOTE_KEY = "NSE:NIFTY 50"

def main() -> int:
    try:
        quote = fetch_underlying_ltp(QUOTE_KEY)
    except Exception as exc:
        msg = str(exc)
        print(f"TOKEN_CHECK_FAIL: {msg}", file=sys.stderr)
        if "Incorrect `api_key` or `access_token`" in msg or "TokenException" in msg:
            return 20
        return 21

    if quote is None:
        print("TOKEN_CHECK_FAIL: empty quote response", file=sys.stderr)
        return 21

    print("TOKEN_CHECK_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
