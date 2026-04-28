import type { TimelineTask } from '$lib/apis/timeline';

export interface LaneAssignment {
	taskId: number;
	laneIndex: number;
	rowId: string;
}

const MS_DAY = 86_400_000;

export function assignLanesToTasks(tasks: Array<{ task: TimelineTask; rowId: string }>): Map<number, LaneAssignment> {
	const assignments = new Map<number, LaneAssignment>();
	if (tasks.length === 0) return assignments;

	const sorted = [...tasks].sort((a, b) => {
		const aStart = a.task.created_at ? new Date(a.task.created_at).getTime() : Date.now();
		const bStart = b.task.created_at ? new Date(b.task.created_at).getTime() : Date.now();
		return aStart - bStart;
	});

	const lanes: Array<{ start: number; end: number }[]> = [];

	for (const { task, rowId } of sorted) {
		// Skip tasks without IDs
		if (task.id == null) continue;

		const taskStart = task.created_at ? new Date(task.created_at).getTime() : Date.now();
		const taskEnd = task.due_date ? new Date(task.due_date).getTime() : Date.now() + 3 * MS_DAY;

		let assignedLane = -1;
		for (let i = 0; i < lanes.length; i++) {
			const lane = lanes[i];
			let hasOverlap = false;
			for (const range of lane) {
				if (taskStart < range.end && taskEnd > range.start) {
					hasOverlap = true;
					break;
				}
			}
			if (!hasOverlap) {
				assignedLane = i;
				break;
			}
		}

		if (assignedLane === -1) {
			assignedLane = lanes.length;
			lanes.push([]);
		}

		lanes[assignedLane].push({ start: taskStart, end: taskEnd });

		const virtualRowId = assignedLane === 0 ? rowId : `${rowId}-lane-${assignedLane}`;
		assignments.set(task.id, { taskId: task.id, laneIndex: assignedLane, rowId: virtualRowId });
	}

	return assignments;
}
