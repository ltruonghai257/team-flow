# Phase 21: Import Map

## Importer Inventory

Command used: `rtk rg '\$lib/api' frontend/src`

| File | Import Kind | Current Import | Target Import |
|------|-------------|----------------|---------------|
| `frontend/src/routes/+page.svelte` | value | `import { dashboard } from '$lib/api'` | `import { dashboard } from '$lib/apis'` |
| `frontend/src/routes/+layout.svelte` | value | `import { sub_teams } from '$lib/api'` | `import { sub_teams } from '$lib/apis'` |
| `frontend/src/routes/ai/+page.svelte` | value | `import { ai as aiApi } from '$lib/api'` | `import { ai as aiApi } from '$lib/apis'` |
| `frontend/src/routes/invite/accept/+page.svelte` | value | `import { invites } from '$lib/api'` | `import { invites } from '$lib/apis'` |
| `frontend/src/routes/milestones/+page.svelte` | value | `import { milestones as milestonesApi, projects as projectsApi } from '$lib/api'` | `import { milestones as milestonesApi, projects as projectsApi } from '$lib/apis'` |
| `frontend/src/routes/performance/+page.svelte` | value | `import { performance } from '$lib/api'` | `import { performance } from '$lib/apis'` |
| `frontend/src/routes/performance/[id]/+page.svelte` | value | `import { performance } from '$lib/api'` | `import { performance } from '$lib/apis'` |
| `frontend/src/routes/projects/+page.svelte` | value | `import { projects as projectsApi, ai as aiApi, statusSets } from '$lib/api'` | `import { projects as projectsApi, ai as aiApi, statusSets } from '$lib/apis'` |
| `frontend/src/routes/projects/+page.svelte` | type | `import type { StatusSet } from '$lib/api'` | `import type { StatusSet } from '$lib/types'` |
| `frontend/src/routes/register/+page.svelte` | value | `import { auth } from '$lib/api'` | `import { auth } from '$lib/apis'` |
| `frontend/src/routes/schedule/+page.svelte` | value | `import { schedules as schedulesApi, tasks as tasksApi, notifications as notifApi } from '$lib/api'` | `import { schedules as schedulesApi, tasks as tasksApi, notifications as notifApi } from '$lib/apis'` |
| `frontend/src/routes/tasks/+page.svelte` | value | `import { tasks as tasksApi, users as usersApi, projects as projectsApi, milestones as milestonesApi, sprints as sprintsApi, statusSets } from '$lib/api'` | `import { ... } from '$lib/apis'` |
| `frontend/src/routes/tasks/+page.svelte` | type | `import type { CustomStatus, StatusSet, StatusTransition } from '$lib/api'` | `import type { CustomStatus, StatusSet, StatusTransition } from '$lib/types'` |
| `frontend/src/routes/team/+page.svelte` | value | `import { users as usersApi, tasks as tasksApi, invites as invitesApi, sub_teams as subTeamsApi, reminderSettings as reminderSettingsApi } from '$lib/api'` | `import { ... } from '$lib/apis'` |
| `frontend/src/routes/team/+page.svelte` | type | `type ReminderSettings, type ReminderSettingsProposal` from `$lib/api` | `import type { ReminderSettings, ReminderSettingsProposal } from '$lib/types'` |
| `frontend/src/routes/timeline/+page.svelte` | value | `import { timeline, tasks as taskApi } from '$lib/api'` | `import { timeline, tasks as taskApi } from '$lib/apis'` |
| `frontend/src/lib/stores/auth.ts` | value | `import { auth as authApi } from '$lib/api'` | `import { auth as authApi } from '$lib/apis'` |
| `frontend/src/lib/stores/notifications.ts` | value | `import { notifications as notifApi } from '$lib/api'` | `import { notifications as notifApi } from '$lib/apis'` |
| `frontend/src/lib/components/performance/KpiWarnButton.svelte` | value | `import { performance } from '$lib/api'` | `import { performance } from '$lib/apis'` |
| `frontend/src/lib/components/sprints/SprintCloseModal.svelte` | value | `import { sprints } from '$lib/api'` | `import { sprints } from '$lib/apis'` |
| `frontend/src/lib/components/sprints/SprintForm.svelte` | value | `import { sprints } from '$lib/api'` | `import { sprints } from '$lib/apis'` |
| `frontend/src/lib/components/statuses/ProjectStatusPanel.svelte` | value | `import { statusSets } from '$lib/api'` | `import { statusSets } from '$lib/apis'` |
| `frontend/src/lib/components/statuses/ProjectStatusPanel.svelte` | type | `import type { StatusSet } from '$lib/api'` | `import type { StatusSet } from '$lib/types'` |
| `frontend/src/lib/components/statuses/StatusDeleteDialog.svelte` | type | `import type { CustomStatus } from '$lib/api'` | `import type { CustomStatus } from '$lib/types'` |
| `frontend/src/lib/components/statuses/StatusEditorRow.svelte` | type | `import type { CustomStatus } from '$lib/api'` | `import type { CustomStatus } from '$lib/types'` |
| `frontend/src/lib/components/statuses/StatusReorderList.svelte` | type | `import type { CustomStatus } from '$lib/api'` | `import type { CustomStatus } from '$lib/types'` |
| `frontend/src/lib/components/statuses/StatusSetManager.svelte` | value | `import { statusSets } from '$lib/api'` | `import { statusSets } from '$lib/apis'` |
| `frontend/src/lib/components/statuses/StatusSetManager.svelte` | type | `import type { CustomStatus, StatusSet, StatusTransition, StatusTransitionPair } from '$lib/api'` | `import type { CustomStatus, StatusSet, StatusTransition, StatusTransitionPair } from '$lib/types'` |
| `frontend/src/lib/components/statuses/StatusTransitionEditor.svelte` | type | `import type { CustomStatus, StatusSet, StatusTransition, StatusTransitionPair } from '$lib/api'` | `import type { CustomStatus, StatusSet, StatusTransition, StatusTransitionPair } from '$lib/types'` |
| `frontend/src/lib/components/statuses/StatusTransitionPreview.svelte` | type | `import type { CustomStatus, StatusTransitionPair } from '$lib/api'` | `import type { CustomStatus, StatusTransitionPair } from '$lib/types'` |
| `frontend/src/lib/components/tasks/AiTaskInput.svelte` | value | `import { tasks as tasksApi } from '$lib/api'` | `import { tasks as tasksApi } from '$lib/apis'` |
| `frontend/src/lib/components/tasks/KanbanBoard.svelte` | type | `import type { CustomStatus } from '$lib/api'` | `import type { CustomStatus } from '$lib/types'` |
| `frontend/src/lib/components/timeline/TimelineGantt.svelte` | value | `import { tasks as taskApi } from '$lib/api'` | `import { tasks as taskApi } from '$lib/apis'` |
