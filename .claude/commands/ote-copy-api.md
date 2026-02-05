---
description: Generate On Time Edge copy by calling the local API running on localhost:8000.
---

Steps:
1) If the API is not running, instruct the user to run:
   uvicorn main:app --reload --port 8000
   and background it with Ctrl+B.
2) Ask for: asset_type, audience, outcome, benefits, capabilities, proof_points, objections, offer_details, CTA.
3) Call the API via curl to /generate and return:
   - the `content` object first
   - then `warnings` (especially banned terms like "IED-Net" and invented stats)
