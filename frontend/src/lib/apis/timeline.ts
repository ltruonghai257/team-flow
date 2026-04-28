import { request } from './request';

export interface TimelineTaskAssignee {
    id: number;
    email: string;
    username: string;
    full_name: string;
    role: 'admin' | 'supervisor' | 'member';
    avatar_url: string | null;
    is_active: boolean;
    sub_team_id: number | null;
    created_at: string;
}

export interface TimelineTaskCustomStatus {
    id: number;
    status_set_id: number;
    name: string;
    slug: string;
    color: string;
    position: number;
    is_done: boolean;
    is_archived: boolean;
    legacy_status: string | null;
    task_count: number;
    created_at: string;
    updated_at: string;
}

export interface TimelineTask {
    id: number;
    title: string;
    description: string | null;
    tags: string | null;
    status: 'todo' | 'in_progress' | 'review' | 'done' | 'blocked';
    priority: 'low' | 'medium' | 'high' | 'critical';
    due_date: string | null;
    created_at: string;
    milestone_id: number | null;
    project_id: number | null;
    assignee_id: number | null;
    custom_status_id: number | null;
    custom_status: TimelineTaskCustomStatus | null;
    assignee: TimelineTaskAssignee | null;
}

export interface TimelineMilestone {
    id: number;
    title: string;
    description: string | null;
    status: 'planned' | 'in_progress' | 'completed' | 'overdue';
    start_date: string | null;
    due_date: string;
    completed_at: string | null;
    tasks: TimelineTask[];
}

export interface TimelineProject {
    id: number;
    name: string;
    color: string;
    milestones: TimelineMilestone[];
    unassigned_tasks: TimelineTask[];
}

export const timeline = {
    get: () => request<TimelineProject[]>('/timeline/'),
};
