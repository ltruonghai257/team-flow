<script lang="ts">
	import type { MilestoneCommandViewMilestone } from '$lib/apis/milestones';
	import { ChevronDown, ChevronRight, Calendar, Flag, AlertTriangle, CheckCircle2, Clock, Ban, Eye, Pencil, Trash2, ExternalLink } from 'lucide-svelte';
	import { formatDate, statusDisplayName } from '$lib/utils';
	import { slide } from 'svelte/transition';
	import { createEventDispatcher } from 'svelte';
	import MilestoneDecisionForm from './MilestoneDecisionForm.svelte';

	export let milestone: MilestoneCommandViewMilestone;
	export let highlighted = false;
	export let initiallyExpanded = false;

	const dispatch = createEventDispatcher();

	let expanded = initiallyExpanded || milestone.planning_state === 'active' || (milestone.risk && milestone.risk !== 'watch');

	const riskLabels = {
		at_risk: 'At risk',
		delayed: 'Delayed',
		blocked: 'Blocked',
		watch: 'Watch'
	};

	const riskColors = {
		at_risk: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
		delayed: 'bg-red-500/10 text-red-500 border-red-500/20',
		blocked: 'bg-red-700/10 text-red-400 border-red-700/20',
		watch: 'bg-blue-500/10 text-blue-400 border-blue-500/20'
	};

    const stateColors = {
        planned: 'bg-gray-800 text-gray-400',
        committed: 'bg-indigo-500/10 text-indigo-400',
        active: 'bg-primary-500/10 text-primary-400',
        completed: 'bg-green-500/10 text-green-400'
    };

	function toggleExpand() {
		expanded = !expanded;
	}

	// Group tasks by status
	$: groupedTasks = (milestone.tasks || []).reduce((acc: any, task) => {
		const status = statusDisplayName(task.custom_status) || task.status || 'Other';
		if (!acc[status]) acc[status] = [];
		acc[status].push(task);
		return acc;
	}, {});

	// Sort tasks in each group by due date
	$: {
		for (const status in groupedTasks) {
			groupedTasks[status].sort((a: any, b: any) => {
				if (!a.due_date) return 1;
				if (!b.due_date) return -1;
				return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
			});
		}
	}

    // Status order for grouping
    const statusOrder = ['Todo', 'In Progress', 'Review', 'Done', 'Blocked'];
    $: sortedStatusGroups = Object.keys(groupedTasks).sort((a, b) => {
        const idxA = statusOrder.findIndex(s => a.toLowerCase().includes(s.toLowerCase()));
        const idxB = statusOrder.findIndex(s => b.toLowerCase().includes(s.toLowerCase()));
        if (idxA === -1 && idxB === -1) return a.localeCompare(b);
        if (idxA === -1) return 1;
        if (idxB === -1) return -1;
        return idxA - idxB;
    });

	function editMilestone() {
		dispatch('edit', milestone);
	}
</script>

<div
	id={`milestone-${milestone.id}`}
	class="card p-0 overflow-hidden transition-all duration-200 {highlighted ? 'ring-1 ring-primary-500/40 border-primary-500/40' : 'hover:border-gray-700'}"
>
	<div class="relative">
		<button
			class="w-full text-left p-4 focus:outline-none"
			on:click={toggleExpand}
		>
			<div class="flex items-start justify-between gap-4">
				<div class="flex-1 min-w-0">
					<div class="flex items-center gap-2 mb-1 flex-wrap">
						<h3 class="font-semibold text-white leading-tight">{milestone.title}</h3>
						<span class="badge {stateColors[milestone.planning_state]} text-[10px] uppercase tracking-wider px-1.5 py-0.5">
							{milestone.planning_state}
						</span>
						{#if milestone.risk}
							<span class="badge {riskColors[milestone.risk]} text-[10px] uppercase tracking-wider px-1.5 py-0.5">
								{riskLabels[milestone.risk]}
							</span>
						{/if}
					</div>
					
					<div class="flex items-center gap-3 text-xs text-gray-500 mb-3">
						<span class="flex items-center gap-1"><Calendar size={12} /> {formatDate(milestone.due_date)}</span>
						<span class="text-gray-600">·</span>
						<span class="truncate">{milestone.project_name}</span>
					</div>

					<!-- Task rollup -->
					<div class="flex items-center gap-4 mb-3">
						<div class="flex-1 bg-gray-800 rounded-full h-1.5 max-w-[120px]">
							<div
								class="h-1.5 rounded-full bg-primary-500 transition-all"
								style="width: {milestone.progress.completion_percent}%"
							></div>
						</div>
						<span class="text-[10px] text-gray-400 font-medium">
							{milestone.progress.done}/{milestone.progress.total} tasks
							{#if milestone.progress.blocked > 0}
								<span class="text-red-400 ml-1">({milestone.progress.blocked} blocked)</span>
							{/if}
						</span>
					</div>

					<!-- Decision summary -->
					<div class="flex items-center gap-2">
						{#if milestone.decision_summary.proposed > 0}
							<span class="text-[10px] bg-indigo-500/10 text-indigo-400 px-1.5 py-0.5 rounded border border-indigo-500/20">
								{milestone.decision_summary.proposed} Proposed
							</span>
						{/if}
						{#if milestone.decision_summary.approved > 0}
							<span class="text-[10px] bg-green-500/10 text-green-400 px-1.5 py-0.5 rounded border border-green-500/20">
								{milestone.decision_summary.approved} Approved
							</span>
						{/if}
					</div>
				</div>
				
				<div class="text-gray-500 mt-1 flex-shrink-0">
					{#if expanded}
						<ChevronDown size={18} />
					{:else}
						<ChevronRight size={18} />
					{/if}
				</div>
			</div>
		</button>
		
		<div class="absolute top-4 right-10 flex items-center gap-1">
			<button 
				on:click|stopPropagation={editMilestone}
				class="p-1.5 text-gray-500 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
				title="Edit Milestone"
			>
				<Pencil size={14} />
			</button>
		</div>
	</div>

	{#if expanded}
		<div class="border-t border-gray-800 bg-gray-900/50" transition:slide={{ duration: 200 }}>
			{#if milestone.description}
				<div class="p-4 pb-2 border-b border-gray-800/50">
					<p class="text-xs text-gray-400 leading-relaxed">{milestone.description}</p>
				</div>
			{/if}

			<!-- Tasks Section -->
			<div class="p-4 space-y-4">
				<div class="flex items-center justify-between">
					<h4 class="text-[10px] font-bold text-gray-500 uppercase tracking-widest flex items-center gap-1.5">
						<Clock size={12} /> Linked Tasks
					</h4>
				</div>

				{#if milestone.tasks && milestone.tasks.length > 0}
					<div class="space-y-4">
						{#each sortedStatusGroups as status}
							<div class="space-y-1.5">
								<h5 class="text-[10px] font-semibold text-gray-600 px-1">{status}</h5>
								<div class="space-y-1">
									{#each groupedTasks[status] as task}
										<a 
											href="/tasks?task_id={task.id}" 
											class="flex items-center justify-between p-2 hover:bg-gray-800 rounded group transition-colors border border-transparent hover:border-gray-700"
										>
											<div class="flex-1 min-w-0 pr-4">
												<p class="text-xs text-gray-300 truncate group-hover:text-white transition-colors">
													{task.title}
												</p>
											</div>
											<div class="flex items-center gap-3 flex-shrink-0">
												{#if task.due_date}
													<span class="text-[10px] text-gray-600">
														{formatDate(task.due_date)}
													</span>
												{/if}
												<ExternalLink size={10} class="text-gray-700 group-hover:text-gray-400 transition-colors" />
											</div>
										</a>
									{/each}
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<p class="text-xs text-gray-600 italic px-1">No tasks linked to this milestone.</p>
				{/if}
			</div>

			<!-- Decisions Section -->
			<div class="p-4 border-t border-gray-800/50 space-y-4">
				<h4 class="text-[10px] font-bold text-gray-500 uppercase tracking-widest flex items-center gap-1.5">
					<Eye size={12} /> Decisions
				</h4>
				<div id="decisions-container-{milestone.id}">
					<MilestoneDecisionForm 
						milestoneId={milestone.id} 
						decisions={milestone.decisions}
						on:refresh={() => dispatch('refresh')}
					/>
				</div>
			</div>
		</div>
	{/if}
</div>
