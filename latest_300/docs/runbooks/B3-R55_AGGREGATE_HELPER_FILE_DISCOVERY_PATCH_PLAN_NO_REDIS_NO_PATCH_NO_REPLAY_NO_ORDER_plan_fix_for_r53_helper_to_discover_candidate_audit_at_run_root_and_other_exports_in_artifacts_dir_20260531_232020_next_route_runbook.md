# B3-R55 next route

Run B3-R56 one-file helper discovery patch in app/mme_scalpx/replay/artifacts.py.

Rules:
1. Patch only the R53 aggregate helper discovery logic.
2. Find candidate audit independently from artifacts_dir.
3. No replay in patch batch.
4. Then run B3-R57 manual helper smoke.
