import type { ComponentType } from 'svelte';
import {
	LayoutDashboard,
	FolderOpen,
	CheckSquare,
	Milestone,
	GanttChartSquare,
	Users,
	MessageSquare,
	ClipboardList,
	Calendar,
	Bot,
	TrendingUp
} from 'lucide-svelte';

export type UserRole = 'admin' | 'supervisor' | 'member';

export interface NavigationChild {
	href: string;
	label: string;
	icon: ComponentType;
	roles?: UserRole[]; // If specified, only visible to these roles
}

export interface NavigationGroup {
	label: string;
	children: NavigationChild[];
}

export const navigationGroups: NavigationGroup[] = [
	{
		label: 'Dashboard',
		children: [
			{ href: '/', label: 'Dashboard', icon: LayoutDashboard }
		]
	},
	{
		label: 'Work',
		children: [
			{ href: '/projects', label: 'Projects', icon: FolderOpen },
			{ href: '/tasks', label: 'Tasks', icon: CheckSquare }
		]
	},
	{
		label: 'Planning',
		children: [
			{ href: '/milestones', label: 'Milestones', icon: Milestone },
			{ href: '/timeline', label: 'Timeline', icon: GanttChartSquare },
			{ href: '/schedule', label: 'Schedule', icon: Calendar }
		]
	},
	{
		label: 'Team',
		children: [
			{ href: '/team', label: 'Team', icon: Users },
			{ href: '/updates', label: 'Updates', icon: MessageSquare },
			{ href: '/board', label: 'Weekly Board', icon: ClipboardList },
			{ href: '/performance', label: 'Performance', icon: TrendingUp, roles: ['admin', 'supervisor'] }
		]
	},
	{
		label: 'AI',
		children: [
			{ href: '/ai', label: 'AI Assistant', icon: Bot }
		]
	}
];

export interface NavigationState {
	activeGroup: string | null;
	activeChild: NavigationChild | null;
}

export function getActiveNavigationState(pathname: string): NavigationState {
	let activeGroup: string | null = null;
	let activeChild: NavigationChild | null = null;

	for (const group of navigationGroups) {
		for (const child of group.children) {
			// Prefix matching for nested routes (e.g., /performance/[id] matches /performance)
			if (pathname === child.href || (child.href !== '/' && pathname.startsWith(child.href + '/'))) {
				activeGroup = group.label;
				activeChild = child;
				break;
			}
		}
		if (activeGroup) break;
	}

	return { activeGroup, activeChild };
}

export function filterNavigationGroups(role: UserRole | null): NavigationGroup[] {
	return navigationGroups
		.map((group) => ({
			...group,
			children: group.children.filter((child) => {
				// If child has role restrictions, check if user's role is allowed
				if (child.roles && role) {
					return child.roles.includes(role);
				}
				// If no role restrictions or no user role, show the child
				return true;
			})
		}))
		.filter((group) => group.children.length > 0); // Remove groups with no visible children
}

export function isSupervisorOrAdmin(role: UserRole | null): boolean {
	return role === 'admin' || role === 'supervisor';
}
