import { format, formatDistanceToNow, isPast } from 'date-fns';

export function formatDate(date: string | Date | null | undefined): string {
	if (!date) return '—';
	return format(new Date(date), 'MMM d, yyyy');
}

export function formatDateTime(date: string | Date | null | undefined): string {
	if (!date) return '—';
	return format(new Date(date), 'MMM d, yyyy h:mm a');
}

export function timeAgo(date: string | Date | null | undefined): string {
	if (!date) return '—';
	return formatDistanceToNow(new Date(date), { addSuffix: true });
}

export function isOverdue(date: string | Date | null | undefined): boolean {
	if (!date) return false;
	return isPast(new Date(date));
}

export const statusColors: Record<string, string> = {
	todo: 'bg-gray-700 text-gray-300',
	in_progress: 'bg-blue-900 text-blue-300',
	review: 'bg-yellow-900 text-yellow-300',
	done: 'bg-green-900 text-green-300',
	blocked: 'bg-red-900 text-red-300'
};

export const statusLabels: Record<string, string> = {
	todo: 'To Do',
	in_progress: 'In Progress',
	review: 'Review',
	done: 'Done',
	blocked: 'Blocked'
};

export const priorityColors: Record<string, string> = {
	low: 'bg-gray-700 text-gray-300',
	medium: 'bg-blue-900 text-blue-300',
	high: 'bg-orange-900 text-orange-300',
	critical: 'bg-red-900 text-red-300'
};

export const taskTypeOptions = ['feature', 'bug', 'task', 'improvement'];

export const taskTypeLabels: Record<string, string> = {
	feature: 'Feature',
	bug: 'Bug',
	task: 'Task',
	improvement: 'Improve'
};

export const taskTypeColors: Record<string, string> = {
	feature: 'bg-cyan-900 text-cyan-300',
	bug: 'bg-red-900 text-red-300',
	task: 'bg-gray-700 text-gray-300',
	improvement: 'bg-emerald-900 text-emerald-300'
};

export const milestoneStatusColors: Record<string, string> = {
	planned: 'bg-gray-700 text-gray-300',
	in_progress: 'bg-blue-900 text-blue-300',
	completed: 'bg-green-900 text-green-300',
	delayed: 'bg-red-900 text-red-300'
};

export function initials(name: string): string {
	return name
		.split(' ')
		.map((w) => w[0])
		.slice(0, 2)
		.join('')
		.toUpperCase();
}
