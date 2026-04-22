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

<div class="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center gap-4 flex-wrap">
	<!-- View Toggle -->
	<div class="flex rounded-lg overflow-hidden border border-gray-700">
		<button
			onclick={() => setViewMode('project')}
			class="flex items-center gap-1.5 px-3 py-1.5 text-sm transition-colors {viewMode === 'project' ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-gray-200'}"
		>
			<GanttChartSquare size={14} />
			By Project
		</button>
		<button
			onclick={() => setViewMode('member')}
			class="flex items-center gap-1.5 px-3 py-1.5 text-sm transition-colors {viewMode === 'member' ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-gray-200'}"
		>
			<Users size={14} />
			By Member
		</button>
	</div>

	<!-- Range Selector -->
	<div class="flex items-center gap-2 ml-auto">
		<span class="text-xs text-gray-500">Range:</span>
		<select
			value={rangeType}
			onchange={handleRangeType}
			class="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded px-2 py-1"
		>
			<option value="week">Week</option>
			<option value="month">Month</option>
			<option value="custom">Custom</option>
		</select>
		{#if rangeType === 'custom'}
			<input
				type="date"
				value={toInputDate(rangeStart)}
				onchange={(e) => handleCustomDate('start', (e.target as HTMLInputElement).value)}
				class="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded px-2 py-1"
			/>
			<span class="text-gray-500 text-xs">→</span>
			<input
				type="date"
				value={toInputDate(rangeEnd)}
				onchange={(e) => handleCustomDate('end', (e.target as HTMLInputElement).value)}
				class="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded px-2 py-1"
			/>
		{/if}
	</div>
</div>
