export type StatusSetScope = 'sub_team_default' | 'project';

export interface CustomStatus {
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

export interface StatusSet {
    id: number;
    scope: StatusSetScope;
    sub_team_id: number | null;
    project_id: number | null;
    created_at: string;
    updated_at: string;
    statuses: CustomStatus[];
}

export interface StatusTransition {
    id: number;
    status_set_id: number;
    from_status_id: number;
    to_status_id: number;
    created_at: string;
}

export interface StatusTransitionPair {
    from_status_id: number;
    to_status_id: number;
}
