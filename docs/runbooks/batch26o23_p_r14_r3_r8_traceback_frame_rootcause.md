# 26-O23-P-R14-R3-R8 — traceback frame root-cause classifier

- generated_at_utc: `2026-05-10T04:23:05.869244+00:00`
- final_verdict: `FAIL_O23_P_R14_R3_R8_TRACEBACK_FRAME_ROOTCAUSE_NOT_PROVEN`
- false_keys: `['manifest_written', 'milestone_written', 'proof_written', 'runbook_written']`
- rootcause: `ZERODHA_KITECONNECT_BOOTSTRAP_TOKEN_OR_QUOTE_STARTUP_FAILURE`
- rootcause_supported: `True`
- exception_candidates: `['The above exception was the direct cause of the following exception:', "app.mme_scalpx.integrations.bootstrap_quote.QuoteFetchError: kite.ltp('NSE:NIFTY 50') failed: Incorrect `api_key` or `access_token`.", 'kiteconnect.exceptions.TokenException: Incorrect `api_key` or `access_token`.', 'raise QuoteFetchError(f"kite.ltp({instrument_key!r}) failed: {exc}") from exc', 'return self._get("market.quote.ltp", params={"i": ins})']`
- unique_frames: `['.venv/lib/python3.10/site-packages/kiteconnect/connect.py', '/usr/lib/python3.10/runpy.py', 'app/mme_scalpx/integrations/bootstrap_provider.py', 'app/mme_scalpx/integrations/bootstrap_quote.py', 'app/mme_scalpx/integrations/runtime_instruments_factory.py', 'app/mme_scalpx/main.py']`
- has_kiteconnect: `True`
- has_bootstrap_quote: `True`
- has_runtime_instruments: `True`
- source_patch_applied: `False`
- service_start_attempted: `False`
- orders_zero: `True`
- position_flat: `True`
- runtime_no_mme_service_pids: `True`
- runtime_no_risk_execution_pids: `True`
- next_recommended_batch: `26-O23-P-R14-R3-R9 add off-market/read-only service-start bootstrap guard so feeds/features/strategy diagnostics do not hard fail on Zerodha quote bootstrap; exact source patch only; no paper/live.`
