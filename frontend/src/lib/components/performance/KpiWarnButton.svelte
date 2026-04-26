<script lang="ts">
    import { performance } from '$lib/api';
    import { toast } from 'svelte-sonner';

    export let userId: number;
    export let userName: string;
    export let kpiScore: number;

    $: level = kpiScore >= 60 && kpiScore < 80 ? 'fair' : kpiScore < 60 ? 'at_risk' : null;
    $: isFair = level === 'fair';
    $: isAtRisk = level === 'at_risk';

    let open = false;
    let sending = false;
    let customMessage = '';

    $: defaultMessage = isFair
        ? `Hi ${userName}, this is a friendly reminder that your KPI score (${kpiScore}/100) is currently in the Fair range. Please review your workload and delivery timing so we can improve together.`
        : `Hi ${userName}, this is a serious warning that your KPI score (${kpiScore}/100) is At Risk. Please review your performance dashboard and align with your supervisor on immediate next steps.`;

    async function send() {
        sending = true;
        try {
            await performance.sendKpiWarningEmail({
                user_id: userId,
                kpi_score: kpiScore,
                level: level!,
                message: customMessage.trim() || undefined,
            });
            toast.success(`Warning email sent to ${userName}`);
            open = false;
            customMessage = '';
        } catch (e: any) {
            toast.error(e?.message ?? 'Failed to send warning email');
        } finally {
            sending = false;
        }
    }

    function cancel() {
        open = false;
        customMessage = '';
    }
</script>

{#if level}
    <button
        type="button"
        on:click={() => open = true}
        class="text-xs font-medium px-2 py-0.5 rounded transition-colors
            {isFair
                ? 'bg-yellow-900/40 text-yellow-300 hover:bg-yellow-800/60'
                : 'bg-red-900/40 text-red-300 hover:bg-red-800/60'}"
        title="Send KPI warning email"
    >
        {isFair ? '✉ Remind' : '⚠ Warn'}
    </button>
{/if}

{#if open}
    <div
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
        role="dialog"
        aria-modal="true"
        aria-label="KPI warning email"
        tabindex="-1"
        on:click|self={cancel}
        on:keydown={(e) => e.key === 'Escape' && cancel()}
    >
        <div class="bg-gray-900 border {isFair ? 'border-yellow-700/50' : 'border-red-700/50'} rounded-2xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <!-- Header -->
            <div class="flex items-start gap-3">
                <span class="text-2xl">{isFair ? '📧' : '🚨'}</span>
                <div>
                    <h3 class="font-semibold text-white text-base">
                        {isFair ? 'Send friendly reminder' : 'Send serious warning'}
                    </h3>
                    <p class="text-sm text-gray-400 mt-0.5">
                        To: <strong class="text-gray-200">{userName}</strong>
                        · KPI score: <strong class="{isFair ? 'text-yellow-400' : 'text-red-400'}">{kpiScore}/100</strong>
                    </p>
                </div>
            </div>

            <!-- What this email says -->
            <div class="rounded-lg {isFair ? 'bg-yellow-900/20 border border-yellow-700/30' : 'bg-red-900/20 border border-red-700/30'} p-3 text-xs text-gray-300 space-y-1">
                <p class="font-medium {isFair ? 'text-yellow-300' : 'text-red-300'}">What will be sent:</p>
                <p>{isFair
                    ? 'A warm, supportive email encouraging the member to review their workload and delivery pace.'
                    : 'A direct warning email stating that their performance is At Risk and immediate action is needed.'
                }</p>
            </div>

            <!-- Custom message (optional) -->
            <div class="space-y-1.5">
                <label class="text-xs text-gray-400 font-medium" for="warn-msg">
                    Custom message <span class="text-gray-600">(optional — leave blank for default)</span>
                </label>
                <textarea
                    id="warn-msg"
                    rows="4"
                    bind:value={customMessage}
                    placeholder={defaultMessage}
                    class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 resize-none focus:outline-none focus:border-primary-500 transition-colors"
                ></textarea>
            </div>

            <!-- Actions -->
            <div class="flex gap-3 pt-1">
                <button
                    type="button"
                    on:click={send}
                    disabled={sending}
                    class="flex-1 py-2 rounded-lg font-medium text-sm text-white transition-colors disabled:opacity-40
                        {isFair ? 'bg-yellow-600 hover:bg-yellow-500' : 'bg-red-600 hover:bg-red-500'}"
                >
                    {sending ? 'Sending…' : isFair ? 'Send reminder' : 'Send warning'}
                </button>
                <button
                    type="button"
                    on:click={cancel}
                    class="px-4 py-2 rounded-lg border border-gray-700 text-gray-400 hover:text-gray-200 text-sm transition-colors"
                >
                    Cancel
                </button>
            </div>
        </div>
    </div>
{/if}
