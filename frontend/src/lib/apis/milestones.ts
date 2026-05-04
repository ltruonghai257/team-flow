import { request } from './request';

export interface MilestoneTaskRollup {
    total: number;
    done: number;
    blocked: number;
    completion_percent: number;
}

export interface MilestoneDecisionSummary {
    proposed: number;
    approved: number;
    rejected: number;
    superseded: number;
}

export interface MilestoneDecision {
    id: number;
    milestone_id: number;
    task_id: number | null;
    title: string;
    status: 'proposed' | 'approved' | 'rejected' | 'superseded';
    note: string | null;
    created_at: string;
    updated_at: string;
}

export interface MilestoneCommandViewMilestone {
    id: number;
    title: string;
    description: string | null;
    status: string;
    planning_state: 'planned' | 'committed' | 'active' | 'completed';
    risk: 'at_risk' | 'delayed' | 'blocked' | 'watch' | null;
    start_date: string | null;
    due_date: string;
    completed_at: string | null;
    project_id: number;
    project_name: string;
    project_color: string;
    progress: MilestoneTaskRollup;
    decision_summary: MilestoneDecisionSummary;
    tasks: any[];
    decisions: MilestoneDecision[];
}

export interface MilestoneCommandViewMetrics {
    active_milestones: number;
    risky_milestones: number;
    proposed_decisions: number;
    blocked_tasks: number;
}

export interface MilestoneCommandViewResponse {
    metrics: MilestoneCommandViewMetrics;
    lanes: Record<string, MilestoneCommandViewMilestone[]>;
}

export const milestones = {
    list: (projectId?: number) =>
        request(`/milestones/${projectId ? `?project_id=${projectId}` : ''}`),
    get: (id: number) => request(`/milestones/${id}`),
    create: (data: object) =>
        request('/milestones/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) =>
        request(`/milestones/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
    delete: (id: number) => request(`/milestones/${id}`, { method: 'DELETE' }),
    commandView: () => request<MilestoneCommandViewResponse>('/milestones/command-view/'),
    decisions: {
        list: (milestoneId: number) => 
            request<MilestoneDecision[]>(`/milestones/${milestoneId}/decisions`),
        create: (milestoneId: number, data: object) =>
            request<MilestoneDecision>(`/milestones/${milestoneId}/decisions`, {
                method: 'POST',
                body: JSON.stringify(data),
            }),
        update: (milestoneId: number, decisionId: number, data: object) =>
            request<MilestoneDecision>(`/milestones/${milestoneId}/decisions/${decisionId}`, {
                method: 'PATCH',
                body: JSON.stringify(data),
            }),
        delete: (milestoneId: number, decisionId: number) =>
            request(`/milestones/${milestoneId}/decisions/${decisionId}`, { method: 'DELETE' }),
    }
};
