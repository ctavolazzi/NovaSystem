**NovaSystem UI Design Document (Comprehensive)**

**1. Introduction**

This document provides a comprehensive overview of the current structure, components, functionality, and interactions within the NovaSystem React UI. It incorporates details from the main application shell (`App.tsx`) and the individual page components (`DashboardPage`, `HubsPage`, `BotsPage`, `TasksPage`, `WorkEffortsPage`). The purpose is to give a designer a thorough understanding of the existing application, enabling them to design an enhanced, streamlined, and modern UI while retaining all current features and addressing usability improvements.

**2. Core Application Shell (`App.tsx`)**

*   **Layout:** Fixed top navigation bar, main content area below for dynamic page rendering.
*   **Navigation Bar:**
    *   Left: Branding ("NovaSystem" linking to `/`), primary navigation links (Dashboard, Hubs, Bots, Tasks, Work Efforts) with active state highlighting.
    *   Right: Connection status indicator (icon + text: Connected/Connecting/Disconnected based on `systemStore`), "Refresh" button (currently logs to console, shows "Not Implemented" tooltip).
*   **Routing:** Uses `react-router-dom` to map paths (`/`, `/hubs`, `/bots`, `/tasks`, `/work-efforts`) to their respective page components.
*   **Global Elements:** Implements a basic tooltip mechanism triggered by certain clicks (e.g., Refresh button).

**3. Common UI Patterns & Components**

*   **Page Header (`page-header`):** Consistently used at the top of each page. Contains the main page title (`page-title`) and usually a primary action button (e.g., "Add Hub", "Create Task").
*   **Content Box (`content-box`):** A common container element used to group related content, often with a header (`content-box-header`) and body (`content-box-body`). Headers sometimes include secondary information (e.g., item counts using Pills). `no-padding` class variant removes body padding, often used for tables.
*   **Data Tables (`data-table`):** Used extensively for displaying lists of items (Bots, Tasks, Work Efforts).
    *   **Structure:** Standard `<thead>` for headers and `<tbody>` for data rows.
    *   **Expandable Rows:** Clicking a table row often expands a hidden row (`expanded-row-content`) below it to show more details (`details-content`). The trigger row gets an `expanded-row-trigger` class.
    *   **Actions:** Often include buttons within table cells for row-specific actions (e.g., Start/Stop, View, Cancel).
*   **Status Pills (`pill status-X`):** Small, rounded elements used to visually indicate status (e.g., `status-connected`, `status-idle`, `status-pending`, `status-completed`, `status-failed`). Text inside indicates the status.
*   **Buttons (`button`, `button-primary`, `button-secondary`, `button-small`):** Standard buttons for actions. `button-primary` typically used for the main page action, `button-secondary` for others or less prominent actions. `button-small` variant used within table rows. Icons (from `react-icons/lu`) are often included alongside text.
*   **Loading/Empty States:** Pages and content boxes display "Loading..." messages (often checking `systemStatus === 'connecting'`) or "No X available" messages when data is being fetched or is absent.
*   **Tooltips (`click-tooltip`):** Simple, temporary popups providing feedback on clicks, especially for non-implemented actions. Implemented locally within each page component where needed.
*   **Links (`Link` from `react-router-dom`, `inline-link` class):** Used for internal navigation, sometimes passing state (e.g., to pre-filter the destination page). `inline-link` class used for links embedded within text or tables.
*   **Icons (`react-icons/lu`):** Used in buttons, stat cards, and potentially other areas to add visual cues (`LuServer`, `LuBot`, `LuActivity`, `LuTriangle`, `LuBriefcase`).
*   **State Management (`useSystemStore` - Zustand):** Central store providing data (hubs, bots, tasks, work efforts, systemStatus) that drives the content displayed on most pages.

**4. Page-Specific Details**

**4.1. Dashboard (`DashboardPage.tsx`)**

*   **Purpose:** Provide a high-level overview of the system's status and key entities.
*   **Layout:**
    *   Page Title ("Dashboard").
    *   Statistics Grid (`stats-grid`): Four `stat-card` elements showing counts for Hubs, Bots, Active Tasks (hardcoded '0'), and Errors (hardcoded '0'), each with an icon.
    *   Main Content Grid (`main-content-grid`): Two columns.
        *   Main Column (`main-column`):
            *   Hubs Overview (`content-box`): Displays `HubCard` components in a grid (`hubs-grid`). Shows loading/empty state.
            *   Bot Management (`content-box`): Displays bots in an expandable `data-table` (similar to `BotsPage`), showing ID/Name, Status, Hub, and Start/Stop buttons. Clicking rows expands to show activity details and a "View Full Details" button.
        *   Side Column (`side-column`):
            *   Recent Events (`content-box`): Shows a static list of example events with status indicators. (Likely placeholder).
*   **Interactions:** Clicking bot rows expands details. Start/Stop buttons (show "Not Implemented" tooltip). "View Full Details" navigates to the specific bot's page (`/bots/:botId`).
*   **Data:** Uses `hubs`, `bots`, `systemStatus` from store. Calculates totals.

**4.2. Hubs (`HubsPage.tsx`)**

*   **Purpose:** Display and manage Hubs.
*   **Layout:**
    *   Page Header: Title "Hubs", "Add Hub" button (with `LuServer` icon).
    *   Hubs Grid (`hubs-grid`): Displays a grid of `HubCard` components (content of `HubCard` not detailed here, but presumably shows hub info).
    *   Shows loading/empty states.
*   **Interactions:** "Add Hub" button (shows "Not Implemented" tooltip). Interactions within `HubCard` are not defined in this file.
*   **Data:** Uses `hubs`, `systemStatus` from store.

**4.3. Bots (`BotsPage.tsx`)**

*   **Purpose:** Display, manage, and monitor Bots.
*   **Layout:**
    *   Page Header: Title "Bots", "Deploy Bot" button (with `LuBot` icon).
    *   Bot Management (`content-box`): Displays bots in an expandable `data-table`.
        *   **Columns:** Bot ID/Name, Status (Pill), Hub, Actions (Start/Stop buttons).
        *   **Expanded Row:** Shows Current Activity, Last Update time, Last Log entry, and a "View Full Details" button.
    *   Shows loading/empty states.
*   **Interactions:** Clicking rows expands details. Start/Stop buttons (show "Not Implemented" tooltip). "Deploy Bot" button (shows "Not Implemented" tooltip). "View Full Details" button navigates to `/bots/:botId` (presumably a future detail page, currently not defined in `App.tsx` routes).
*   **Data:** Uses `bots`, `systemStatus` from store. Uses `formatDate` helper.

**4.4. Tasks (`TasksPage.tsx`)**

*   **Purpose:** Display and manage Tasks.
*   **Layout:**
    *   Page Header: Title "Tasks", "Create Task" button.
    *   Task Overview (`content-box`): Displays tasks in an expandable `data-table`.
        *   **Columns:** ID, Description, Status (Pill), Assigned Bot, Created At, Result/Actions. The last column shows truncated results for completed/failed tasks or a "Cancel" button for others.
        *   **Expanded Row:** Shows full details including Description, Status, Created/Completed Times, Assigned Bot, full Result (in `<pre>`), and a link to the Related Work Effort (if any).
    *   Shows loading/empty states.
*   **Interactions:** Clicking rows expands details. "Create Task" button (shows "Not Implemented" tooltip). "Cancel" button (shows "Not Implemented" tooltip). Clicking the "Related Work Effort" link navigates to `/work-efforts` with state to filter.
*   **Data:** Uses `tasks`, `systemStatus` from store. Uses `formatDate` helper.

**4.5. Work Efforts (`WorkEffortsPage.tsx`)**

*   **Purpose:** Display and manage Work Efforts.
*   **Layout:**
    *   Page Header: Title "Work Efforts", "Create Work Effort" button (with `LuBriefcase` icon).
    *   Work Efforts Table (`content-box`): Displays work efforts in an expandable `data-table`.
        *   **Columns:** ID, Title, Status (Pill), Linked Tasks (shows comma-separated task IDs as links), Actions ("View" button).
        *   **Expanded Row:** Shows Title, Status, and a list of Linked Tasks (as links).
    *   Shows loading/empty states.
*   **Interactions:** Clicking rows expands details. "Create Work Effort" button (shows "Not Implemented" tooltip). "View" button (shows "Not Implemented" tooltip). Clicking Linked Task links navigates to `/tasks` with state to filter.
*   **Data:** Uses `workEfforts`, `systemStatus` from store.

**5. Design Considerations for Improvement**

*   **Visual Consistency & Modernization:** Apply a consistent, modern design language across all pages, components (including `HubCard`), tables, buttons, pills, and forms (once created).
*   **UX/Interaction Flow:**
    *   Implement the "Not Implemented" features (Refresh, Add Hub, Deploy Bot, Create Task/Work Effort, Start/Stop Bot, Cancel Task, View Details).
    *   Improve feedback mechanisms (loading states, success/error messages, button states). The current tooltip is basic.
    *   Consider alternatives or improvements to expandable table rows for displaying details, especially if details become complex.
    *   Standardize navigation (e.g., ensure "View Full Details" consistently links to a dedicated detail page). The `/bots/:botId` navigation implies detail pages are intended but not yet routed in `App.tsx`.
    *   Refine the linking between Tasks and Work Efforts for clarity.
*   **Information Density:** Evaluate if tables or cards present information effectively. Can dashboards be more visually engaging?
*   **Data Visualization:** Explore charts or graphs for the Dashboard stats and potentially for task/bot history.
*   **Responsiveness:** Ensure layouts adapt gracefully to various screen sizes.
*   **Accessibility:** Adhere to accessibility best practices (semantic HTML, ARIA attributes, color contrast).
*   **Error Handling:** Define how backend errors or invalid data should be presented to the user.
*   **Forms:** Design intuitive forms for creating/editing Hubs, Bots, Tasks, and Work Efforts.