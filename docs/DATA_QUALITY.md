# course_program_cmo_ver — data quality

## Status (BSCPE / CMO 87 s.2017)
- **Sequencing, titles, lec/lab/units, prereqs**: curated from CMO sample Program of Study → treat as CMO-grounded (still spot-check against PDF).
- **`course_code`**: **inferred** (CHED does not assign institutional codes). Stable SAGE IDs only.
- **`classification`**: **inferred** (`core_gened` / `shared_major` / `program_specific` / `elective`).
- **`competency_tags`**: **inferred** (1–4 tags for SAGE topic expansion). **Must human-review before prod seed.**
- **`verified`**: currently `false` on all rows until a reviewer flips after audit.

## Review checklist
- [ ] Titles/units/prereqs match CMO 87 PoS pages (PDF)
- [ ] `course_code` unique and acceptable to SAGE seed (`ON CONFLICT program_code,cmo_reference,course_code`)
- [ ] `competency_tags` sensible (not generic junk)
- [ ] `classification` consistent across GE / major / electives
- [ ] Set `verified=true` (or filter verified-only on import)

## Files
| File | Use |
|------|-----|
| `data/course_program_cmo_ver.csv` | Full table + provenance columns |
| `data/course_program_cmo_ver.json` | Same as JSON |
| `data/course_program_cmo_ver.sage.json` | SAGE `CMORecordCreate` shape + `_provenance` |
