export interface ReminderSettings {
    id: number;
    sub_team_id: number;
    lead_time_days: number;
    sprint_reminders_enabled: boolean;
    milestone_reminders_enabled: boolean;
    created_at: string;
    updated_at: string;
}

export interface ReminderSettingsProposal {
    id: number;
    sub_team_id: number;
    proposed_by_id: number;
    reviewed_by_id: number | null;
    lead_time_days: number | null;
    sprint_reminders_enabled: boolean | null;
    milestone_reminders_enabled: boolean | null;
    status: 'pending' | 'approved' | 'rejected';
    created_at: string;
    reviewed_at: string | null;
}
