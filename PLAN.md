# IntegrateAgent Voicemeeter Integration Plan (Phased + Trackable)

## Summary
Add Voicemeeter Potato control and readback to the existing IntegrateAgent HTTP API while preserving the current security model. Introduce new `voicemeeter_*` actions for applying settings in batch, grouped bus control, engine reset, and state queries. Provide config-driven allowlists for safe parameter access. Ensure silent operation with no visible command prompts.

## Milestones
- M1 — Voicemeeter Integration Skeleton
- M2 — Write Actions
- M3 — Read Actions
- M4 — Security + Observability
- M5 — Documentation + Test Scenarios

## Phase Checklists
### Phase 1 — Repo Prep + API Wiring
- [x] Add voicemeeter dependency to `pyproject.toml`.
- [x] Create a `voicemeeter` module.
- [x] Extend request/response models.
- [x] Route new actions in the FastAPI handler.

### Phase 2 — Write Operations
- [x] Implement `voicemeeter_apply`.
- [x] Implement `voicemeeter_group_bus_gain`.
- [x] Implement `voicemeeter_command`.

### Phase 3 — Read Operations
- [x] Implement `voicemeeter_get` (targets/fields).
- [x] Implement raw `voicemeeter_get` via allowlisted params.

### Phase 4 — Security and Config
- [x] Add voicemeeter allowlist settings.
- [x] Enforce validation for targets/fields/commands/params.

### Phase 5 — Logging + Docs
- [x] Update `README.md` with usage examples.
- [x] Update `STATUS.md` with new features.
- [x] Document test results in `STATUS.md`.

## Decisions Log (Locked)
- Voicemeeter edition: Potato only
- Strips: 0–7 (8 total), 0-based
- Buses: 0–4 (5 total), 0-based
- Read support required for controller boot sync
- Security: config-driven allowlist patterns
- Grouping: server-side `bus_group_gain` action
- Must run silently (no visible command prompts)

## API Additions
- `voicemeeter_apply`
- `voicemeeter_group_bus_gain`
- `voicemeeter_command`
- `voicemeeter_get`
- `voicemeeter_set`

## Tests / Validation Scenarios
- Apply valid gains and mutes.
- Reject out-of-range gain.
- Reject unknown target.
- Group bus gain sets bus 0–2.
- Command reset succeeds.
- Get returns current values for strips/buses.
- Raw param access blocked unless allowlisted.
- Existing `run_app` and `key_press` still function.

## Change Log
- 2026-02-14: Initial plan created and implemented.
- 2026-02-14: Added test results section to `STATUS.md`.
