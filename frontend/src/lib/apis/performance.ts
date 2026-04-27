import { request } from './request';

function qs(params?: Record<string, string | number | boolean | null | undefined>): string {
    if (!params) return '';
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
        if (v !== null && v !== undefined && v !== '') p.append(k, String(v));
    }
    const s = p.toString();
    return s ? `?${s}` : '';
}

export const performance = {
    teamStats: () => request('/performance/team'),
    memberStats: (id: number) => request(`/performance/user/${id}`),
    kpiOverview: (params?: Record<string, string | number | boolean | null | undefined>) => request(`/performance/kpi/overview${qs(params)}`),
    kpiSprint: (params?: Record<string, string | number | boolean | null | undefined>) => request(`/performance/kpi/sprint${qs(params)}`),
    kpiQuality: (params?: Record<string, string | number | boolean | null | undefined>) => request(`/performance/kpi/quality${qs(params)}`),
    kpiMembers: (params?: Record<string, string | number | boolean | null | undefined>) => request(`/performance/kpi/members${qs(params)}`),
    kpiDrilldown: (params?: Record<string, string | number | boolean | null | undefined>) => request(`/performance/kpi/drilldown${qs(params)}`),
    kpiWeights: () => request('/performance/kpi/weights'),
    updateKpiWeights: (data: object) => request('/performance/kpi/weights', { method: 'PATCH', body: JSON.stringify(data) }),
    sendKpiWarningEmail: (data: { user_id: number; kpi_score: number; level: string; message?: string }) =>
        request('/performance/kpi/warning-email', { method: 'POST', body: JSON.stringify(data) }),
};
