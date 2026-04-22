<script lang="ts">
	import { GanttChartSquare, Users } from 'lucide-svelte';

	interface Props {
		viewMode?: 'project' | 'member';
		rangeType?: 'week' | 'month' | 'custom';
		rangeStart?: Date;
		rangeEnd?: Date;
		onviewchange?: (mode: 'project' | 'member') => void;
		onrangechange?: (range: { type: 'week' | 'month' | 'custom'; start: Date; end: Date }) => void;
	}

	let {
		viewMode = $bindable('project'),
		rangeType = $bindable('month'),
		rangeStart = $bindable(new Date()),
		rangeEnd = $bindable(new Date()),
		onviewchange,
		onrangechange
	}: Props = $props();

	function setViewMode(mode: 'project' | 'member') {
		viewMode = mode;
		onviewchange?.(mode);
	}

	function handleRangeType(e: Event) {
		const type = (e.target as HTMLSelectElement).value as 'week' | 'month' | 'custom';
		rangeType = type;
		const now = new Date();
		let start = new Date(now);
		let end = new Date(now);
		if (type === 'week') {
			start.setDate(now.getDate() - now.getDay());
			end.setDate(start.getDate() + 6);
		} else if (type === 'month') {
			start = new Date(now.getFullYear(), now.getMonth(), 1);
			end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
		}
		rangeStart = start;
		rangeEnd = end;
		onrangechange?.({ type, start, end });
	}

	function handleCustomDate(field: 'start' | 'end', value: string) {
		const date = new Date(value);
		if (field === 'start') rangeStart = date;
		else rangeEnd = date;
		onrangechange?.({ type: 'custom', start: rangeStart, end: rangeEnd });
	}

	function toInputDate(d: Date): string {
		return d.toISOString().slice(0, 10);
	}
</script>

<div class="bg-[#0f172a] border-b border-[#1e293b] px-6 py-2.5 flex items-center gap-4 flex-wrap flex-shrink-0">
	<!-- View Toggle pill -->
	<div class="flex rounded-lg overflow-hidden border border-[#1e293b] bg-[#0a0f1e]">
		<button
			onclick={() => setViewMode('project')}
			class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-all {viewMode === 'project' ? 'bg-indigo-600 text-white shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}"
		>
			<GanttChartSquare size={13} />
			By Project
		</button>
		<button
			onclick={() => setViewMode('member')}
			class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-all {viewMode === 'member' ? 'bg-indigo-600 text-white shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}"
		>
			<Users size={13} />
			By Member
		</button>
	</div>

	<!-- Range Selector -->
	<div class="flex items-center gap-2 ml-auto">
		<span class="text-xs text-slate-500 font-medium">Range</span>
		<select
			value={rangeType}
			onchange={handleRangeType}
			class="bg-[#0a0f1e] border border-[#1e293b] text-slate-300 text-xs rounded-md px-2.5 py-1.5 focus:outline-none focus:border-indigo-500 transition-colors"
		>
			<option value="week">Week</option>
			<option value="month">Month</option>
			<option value="custom">Custom range</option>
		</select>
		{#if rangeType === 'custom'}
			<div class="flex items-center gap-1.5">
				<input
					type="date"
					value={toInputDate(rangeStart)}
					onchange={(e) => handleCustomDate('start', (e.target as HTMLInputElement).value)}
					class="bg-[#0a0f1e] border border-[#1e293b] text-slate-300 text-xs rounded-md px-2.5 py-1.5 focus:outline-none focus:border-indigo-500"
				/>
				<span class="text-slate-600 text-xs">→</span>
				<input
					type="date"
					value={toInputDate(rangeEnd)}
					onchange={(e) => handleCustomDate('end', (e.target as HTMLInputElement).value)}
					class="bg-[#0a0f1e] border border-[#1e293b] text-slate-300 text-xs rounded-md px-2.5 py-1.5 focus:outline-none focus:border-indigo-500"
				/>
			</div>
		{/if}
	</div>
</div>
