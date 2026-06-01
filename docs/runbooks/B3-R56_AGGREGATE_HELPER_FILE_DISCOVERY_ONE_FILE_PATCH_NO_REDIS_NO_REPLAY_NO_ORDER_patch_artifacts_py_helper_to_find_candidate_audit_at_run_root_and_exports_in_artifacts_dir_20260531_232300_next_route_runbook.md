# B3-R56 next route

Run B3-R57 manual helper smoke against existing R47 run dir.

Expected:
- combined_candidate_audit rows = 5887
- combined_economics_summary combined_row_count = 5887
- date_range_manifest combined_candidate_rows = 5887
- blocker rows = 5
- family-side rows = 5

No replay. No Redis. No hook yet.
