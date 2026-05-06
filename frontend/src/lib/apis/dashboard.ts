import { request } from './request';

export interface DashboardTaskItem {
    id: number;
    title: string;
    project_name: string | null;
    status: string;
    priority: string | null;
    due_date: string | null;
    is_overdue: boolean;
    is_due_soon: boolean;
}

export interface DashboardTeamHealthMember {
    user_id: number;
    full_name: string;
    avatar_url: string | null;
    status: 'green' | 'yellow' | 'red';
    active_tasks: number;
    completed_30d: number;
    overdue_tasks: number;
}

export interface DashboardKpiSummary {
    avg_score: number;
    completion_rate: number;
    needs_attention_count: number;
}

export interface DashboardActivityItem {
    post_id: number;
    author_id: number;
    author_name: string;
    created_at: string;
    field_values: Record<string, string>;
}

export interface DashboardPayload {
    my_tasks: DashboardTaskItem[];
    team_health?: DashboardTeamHealthMember[];
    kpi_summary?: DashboardKpiSummary;
    recent_activity: DashboardActivityItem[];
}

export const dashboard = {
    get: () => request<DashboardPayload>('/dashboard/'),
};
