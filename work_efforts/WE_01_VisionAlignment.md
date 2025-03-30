# Work Effort: WE_01 - NovaSystem Vision Alignment

**Goal:** Enhance the NovaSystem codebase to begin implementing the broader vision outlined in the root README.md, moving beyond the v0.1.1 repository installation tool towards features like the Nova Process and potentially agent-based architectures.

**Status:** In Progress

**Date Created:** 2025-03-29

## Defined Scope (Phase 1 - Core "Nova Unit")

Implement the foundational "Nova Unit" of the NovaSystem, consisting of interacting `Bot`, `Hub`, and `Controller` components:

1.  **Bot:** Unique ID, logs actions to `.md` files in accessible "memory".
2.  **Hub:** Unique ID, contains Bots, records internal events to a log/ledger. **Constraint: Can only be assigned one managing Controller.**
3.  **Controller:** Specialized Bot, creates/manages Bots within assigned Hub(s).
4.  **System:** Clear data structures, supports multiple instances, trackable interactions.

**Note:** Inter-hub communication is deferred to a later phase.

## Refined Development Plan

1.  **Data Structures Design:**
    *   Define Python classes/dataclasses for `BaseBot`, `Controller`, `Hub`.
    *   Define structure for Bot IDs, Hub IDs (e.g., using UUID).
    *   Define structure for Hub logs/ledger (e.g., simple text log file per Hub).
    *   Define structure for Bot "memory" (e.g., `bot_memory/[bot_id]/memory/` or `hubs/[hub_id]/bots/[bot_id]/memory/`).
2.  **Base Bot Implementation:**
    *   Create `BaseBot` class with UUID initialization and appropriate memory path logic.
    *   Implement `log_action` method for journaling.
3.  **Hub Implementation:**
    *   Create `Hub` class with UUID initialization, dedicated directory, and log file.
    *   Maintain internal dictionary of contained Bots.
    *   Implement `record_event` method.
    *   Implement `add_bot`, `get_bot`, `remove_bot` methods.
    *   **Implement `assign_managing_controller` method to enforce one-controller rule.**
4.  **Controller Implementation:**
    *   Create `Controller` class inheriting from `BaseBot` (with root memory path).
    *   **Modify `assign_hub` to use `hub.assign_managing_controller` and handle success/failure.**
    *   Implement `create_bot` method (passing hub path to new bot).
5.  **Interaction & Setup:**
    *   Create/update `core_components/demo.py`.
6.  **Testing:** Create/update unit tests (`pytest`) for `BaseBot`, `Hub`, `Controller` classes **including the one-controller constraint**.
7.  **Documentation:** Add initial documentation for the new classes.

## Updates

*   2025-03-29: Work Effort created. Initial plan outlined.
*   2025-03-29: Scope defined for Phase 1 (Core Unit: Bot, Hub, Controller). Development plan refined.
*   2025-03-29: Added constraint: One Controller per Hub. Updated plan to reflect implementation and testing for this rule. Adopted term "Nova Unit".

### Implementation Tasks

*   [x] Create `core_components` directory.
*   [x] Implement `BaseBot` class (`base_bot.py`) with basic ID, name, logging (`journal.md`, `bot.log`), and memory path structure (`<base_path>/memory`).
    *   [x] Ensure `log_action` appends to `journal.md` by default.
    *   [x] Implement `record_event` to log to `bot.log`.
    *   [x] Base `BaseBot` paths on a `base_path` provided during init.
*   [x] Implement `Hub` class (`hub.py`) with ID, name, bot management (`add_bot`, `get_bot`, `list_bots`, `remove_bot`), and event logging (`hub.log`).
    *   [x] Implement `assign_managing_controller` logic to enforce one controller per hub.
    *   [x] Ensure Hub creates its own directory structure (`hubs/<hub_id>`).
*   [x] Implement `Controller` class (`controller.py`) inheriting from `BaseBot`.
    *   [x] Implement `assign_hub` method, interacting with `Hub.assign_managing_controller`.
    *   [x] Implement `create_bot` method to instantiate `BaseBot` within a specific Hub's directory structure (`hubs/<hub_id>/bots/<bot_id>`).
    *   [x] Ensure `Controller` calculates its own `base_path` (`bot_memory/<controller_id>`) and the `base_path` for bots it creates.
*   [x] Update `demo.py` to showcase Hub/Controller/Bot creation and interaction, including data exchange simulation and verification through logs/journals.
*   [x] Create test suite (`tests/test_core_components.py`) using `pytest`.
    *   [x] Add tests for `BaseBot` initialization, path creation, `log_action`, `record_event`, memory access, and error handling.
    *   [x] Add tests for `Hub` initialization, bot management, event logging, controller assignment logic (including conflicts), and error handling.
    *   [x] Add tests for `Controller` initialization, hub assignment (including conflicts), bot creation (path verification), logging, and error handling.
    *   [x] Run tests and debug until all pass.
*   [ ] Document new classes (`BaseBot`, `Hub`, `Controller`) in `docs/components/`.
*   [ ] Update `README.md` with information about the new core components.