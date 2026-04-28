import type { TimelineMilestone, TimelineProject, TimelineTask } from '$lib/apis/timeline';

type TaskStatus = TimelineTask['status'];

export type RiskLevel = 'low' | 'medium' | 'high';

export interface MilestoneSignals {
	risk: RiskLevel;
	planning: boolean;
	decision: boolean;
}

export interface MilestoneProgress {
	total: number;
	done: number;
	percent: number;
	counts: Record<TaskStatus, number>;
}

export interface MilestoneViewModel {
	id: number;
	projectId: number;
	projectName: string;
	projectColor: string;
	title: string;
	status: TimelineMilestone['status'];
	startDate: string | null;
	dueDate: string;
	description: string | null;
	progress: MilestoneProgress;
	signals: MilestoneSignals;
	expandedByDefault: boolean;
	tasks: TimelineTask[];
}

export interface TimelineViewModel {
	projects: TimelineProject[];
	milestones: MilestoneViewModel[];
	tasksByMilestone: Map<number, TimelineTask[]>;
	taskToMilestone: Map<number, number>;
}

const EMPTY_COUNTS: Record<TaskStatus, number> = {
	todo: 0,
	in_progress: 0,
	review: 0,
	done: 0,
	blocked: 0
};

const STATUS_ORDER: Record<TaskStatus, number> = {
	blocked: 0,
	in_progress: 1,
	review: 2,
	todo: 3,
	done: 4
};

function getTaskDueTime(task: TimelineTask): number {
	return task.due_date ? new Date(task.due_date).getTime() : Number.MAX_SAFE_INTEGER;
}

export function deriveMilestoneSignals(milestone: TimelineMilestone): MilestoneSignals {
	const now = Date.now();
	const text = `${milestone.title} ${milestone.description ?? ''}`.toLowerCase();
	const dueTime = new Date(milestone.due_date).getTime();
	const dueSoon = dueTime > now && dueTime - now <= 3 * 86_400_000;
	const overdue = milestone.status !== 'completed' && dueTime < now;
	const blockedTasks = milestone.tasks.filter((task) => task.status === 'blocked').length;
	const criticalTasks = milestone.tasks.filter((task) => task.priority === 'critical' && task.status !== 'done').length;
	const doneCount = milestone.tasks.filter((task) => task.status === 'done').length;
	const totalTasks = milestone.tasks.length;
	const completion = totalTasks === 0 ? 100 : Math.round((doneCount / totalTasks) * 100);
	const lowCompletionNearDue = dueSoon && completion < 60;
	const atRiskStatus = milestone.status === 'overdue';

	let risk: RiskLevel = 'low';
	if (atRiskStatus || overdue || blockedTasks >= 2 || criticalTasks >= 2 || lowCompletionNearDue) {
		risk = 'high';
	} else if (dueSoon || blockedTasks > 0 || criticalTasks > 0) {
		risk = 'medium';
	}

	return {
		risk,
		planning: Boolean(milestone.start_date),
		decision: /decision|approve|pending review|tradeoff|option/.test(text)
	};
}

export function buildTimelineViewModel(projects: TimelineProject[]): TimelineViewModel {
	const milestones: MilestoneViewModel[] = [];
	const tasksByMilestone = new Map<number, TimelineTask[]>();
	const taskToMilestone = new Map<number, number>();

	for (const project of projects) {
		for (const milestone of project.milestones) {
			const counts = { ...EMPTY_COUNTS };
			for (const task of milestone.tasks) {
				counts[task.status] += 1;
			}

			const total = milestone.tasks.length;
			const done = counts.done;
			const percent = total === 0 ? 0 : Math.round((done / total) * 100);
			const signals = deriveMilestoneSignals(milestone);
			const tasks = [...milestone.tasks].sort((a, b) => {
				const statusSort = STATUS_ORDER[a.status] - STATUS_ORDER[b.status];
				if (statusSort !== 0) return statusSort;
				return getTaskDueTime(a) - getTaskDueTime(b);
			});

			for (const task of tasks) {
				taskToMilestone.set(task.id, milestone.id);
			}
			tasksByMilestone.set(milestone.id, tasks);

			milestones.push({
				id: milestone.id,
				projectId: project.id,
				projectName: project.name,
				projectColor: project.color,
				title: milestone.title,
				status: milestone.status,
				startDate: milestone.start_date,
				dueDate: milestone.due_date,
				description: milestone.description,
				progress: { total, done, percent, counts },
				signals,
				expandedByDefault: signals.risk !== 'low' || milestone.status === 'in_progress',
				tasks
			});
		}
	}

	return { projects, milestones, tasksByMilestone, taskToMilestone };
}
