<script lang="ts">
	import { onMount } from 'svelte';
	import { schedules as schedulesApi } from '$lib/api';
	import { formatDateTime } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import { Plus, Pencil, Trash2, X, Calendar, MapPin, Clock } from 'lucide-svelte';
	import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, isSameMonth, startOfWeek, endOfWeek } from 'date-fns';

	let scheduleList: any[] = [];
	let loading = true;
	let showModal = false;
	let editingSchedule: any = null;
	let currentMonth = new Date();

	let form = {
		title: '',
		description: '',
		start_time: '',
		end_time: '',
		all_day: false,
		color: '#6366f1',
		location: ''
	};

	onMount(loadSchedules);

	async function loadSchedules() {
		loading = true;
		try {
			scheduleList = await schedulesApi.list();
		} finally {
			loading = false;
		}
	}

	function openCreate(date?: Date) {
		editingSchedule = null;
		const base = date ? format(date, "yyyy-MM-dd") : format(new Date(), "yyyy-MM-dd");
		form = {
			title: '',
			description: '',
			start_time: `${base}T09:00`,
			end_time: `${base}T10:00`,
			all_day: false,
			color: '#6366f1',
			location: ''
		};
		showModal = true;
	}

	function openEdit(s: any) {
		editingSchedule = s;
		form = {
			title: s.title,
			description: s.description || '',
			start_time: s.start_time.slice(0, 16),
			end_time: s.end_time.slice(0, 16),
			all_day: s.all_day,
			color: s.color,
			location: s.location || ''
		};
		showModal = true;
	}

	async function handleSubmit() {
		const payload = {
			...form,
			start_time: new Date(form.start_time).toISOString(),
			end_time: new Date(form.end_time).toISOString()
		};
		try {
			if (editingSchedule) {
				await schedulesApi.update(editingSchedule.id, payload);
				toast.success('Event updated');
			} else {
				await schedulesApi.create(payload);
				toast.success('Event created');
			}
			showModal = false;
			await loadSchedules();
		} catch (e) {
			toast.error(e.message);
		}
	}

	async function deleteSchedule(id: number) {
		if (!confirm('Delete this event?')) return;
		try {
			await schedulesApi.delete(id);
			toast.success('Event deleted');
			await loadSchedules();
		} catch (e) {
			toast.error(e.message);
		}
	}

	function eventsOnDay(day: Date) {
		return scheduleList.filter((s) => isSameDay(new Date(s.start_time), day));
	}

	$: calDays = (() => {
		const start = startOfWeek(startOfMonth(currentMonth), { weekStartsOn: 1 });
		const end = endOfWeek(endOfMonth(currentMonth), { weekStartsOn: 1 });
		return eachDayOfInterval({ start, end });
	})();

	const colorOptions = [
		{ value: '#6366f1', label: 'Indigo' },
		{ value: '#10b981', label: 'Green' },
		{ value: '#f59e0b', label: 'Amber' },
		{ value: '#ef4444', label: 'Red' },
		{ value: '#8b5cf6', label: 'Purple' },
		{ value: '#3b82f6', label: 'Blue' }
	];
</script>

<svelte:head><title>Schedule · TeamFlow</title></svelte:head>

<div class="p-6 max-w-6xl mx-auto">
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-2xl font-bold text-white">My Schedule</h1>
			<p class="text-gray-400 text-sm mt-1">Your personal calendar and events</p>
		</div>
		<button on:click={() => openCreate()} class="btn-primary">
			<Plus size={16} /> New Event
		</button>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Calendar -->
			<div class="lg:col-span-2 card">
				<div class="flex items-center justify-between mb-4">
					<button on:click={() => currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1)}
						class="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors">‹</button>
					<h2 class="font-semibold text-white">{format(currentMonth, 'MMMM yyyy')}</h2>
					<button on:click={() => currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1)}
						class="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors">›</button>
				</div>

				<!-- Day headers -->
				<div class="grid grid-cols-7 gap-1 mb-1">
					{#each ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as d}
						<div class="text-center text-xs font-medium text-gray-500 py-1">{d}</div>
					{/each}
				</div>

				<!-- Days grid -->
				<div class="grid grid-cols-7 gap-1">
					{#each calDays as day}
						{@const events = eventsOnDay(day)}
						{@const isToday = isSameDay(day, new Date())}
						{@const inMonth = isSameMonth(day, currentMonth)}
						<button
							on:click={() => openCreate(day)}
							class="min-h-[64px] p-1 rounded-lg text-left transition-colors hover:bg-gray-800 {inMonth ? '' : 'opacity-30'} {isToday ? 'ring-1 ring-primary-500' : ''}"
						>
							<span class="text-xs {isToday ? 'text-primary-400 font-bold' : 'text-gray-400'} block mb-1 px-0.5">
								{format(day, 'd')}
							</span>
							{#each events.slice(0, 2) as ev}
								<div class="text-xs px-1 py-0.5 rounded mb-0.5 truncate text-white" style="background-color: {ev.color}80; border-left: 2px solid {ev.color}">
									{ev.title}
								</div>
							{/each}
							{#if events.length > 2}
								<span class="text-xs text-gray-500 px-1">+{events.length - 2} more</span>
							{/if}
						</button>
					{/each}
				</div>
			</div>

			<!-- Upcoming events list -->
			<div class="card">
				<h2 class="font-semibold text-white mb-4 flex items-center gap-2">
					<Calendar size={16} class="text-primary-400" /> Upcoming Events
				</h2>
				{#if scheduleList.length === 0}
					<p class="text-gray-500 text-sm text-center py-6">No events yet</p>
				{:else}
					<div class="space-y-2 max-h-[500px] overflow-y-auto">
						{#each scheduleList.sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()) as s}
							<div class="p-3 rounded-lg bg-gray-800 border-l-2" style="border-color: {s.color}">
								<div class="flex items-start justify-between gap-2">
									<div class="flex-1 min-w-0">
										<p class="text-sm font-medium text-gray-200 truncate">{s.title}</p>
										<p class="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
											<Clock size={10} /> {formatDateTime(s.start_time)}
										</p>
										{#if s.location}
											<p class="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
												<MapPin size={10} /> {s.location}
											</p>
										{/if}
									</div>
									<div class="flex gap-1 flex-shrink-0">
										<button on:click={() => openEdit(s)} class="p-1 text-gray-500 hover:text-gray-300 rounded transition-colors">
											<Pencil size={12} />
										</button>
										<button on:click={() => deleteSchedule(s.id)} class="p-1 text-gray-500 hover:text-red-400 rounded transition-colors">
											<Trash2 size={12} />
										</button>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

{#if showModal}
	<div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
		<div class="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-md">
			<div class="flex items-center justify-between p-5 border-b border-gray-800">
				<h2 class="font-semibold text-white">{editingSchedule ? 'Edit Event' : 'New Event'}</h2>
				<button on:click={() => (showModal = false)} class="text-gray-500 hover:text-gray-300"><X size={18} /></button>
			</div>
			<form on:submit|preventDefault={handleSubmit} class="p-5 space-y-4">
				<div>
					<label class="label" for="s-title">Title *</label>
					<input id="s-title" bind:value={form.title} class="input" required />
				</div>
				<div>
					<label class="label" for="s-desc">Description</label>
					<textarea id="s-desc" bind:value={form.description} class="input resize-none" rows="2"></textarea>
				</div>
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="label" for="s-start">Start *</label>
						<input id="s-start" bind:value={form.start_time} type="datetime-local" class="input" required />
					</div>
					<div>
						<label class="label" for="s-end">End *</label>
						<input id="s-end" bind:value={form.end_time} type="datetime-local" class="input" required />
					</div>
				</div>
				<div>
					<label class="label" for="s-location">Location</label>
					<input id="s-location" bind:value={form.location} class="input" placeholder="Conference room, URL..." />
				</div>
				<div>
					<label class="label">Color</label>
					<div class="flex gap-2 flex-wrap">
						{#each colorOptions as c}
							<button
								type="button"
								on:click={() => (form.color = c.value)}
								class="w-7 h-7 rounded-full transition-transform {form.color === c.value ? 'ring-2 ring-white ring-offset-2 ring-offset-gray-900 scale-110' : 'hover:scale-105'}"
								style="background-color: {c.value}"
								title={c.label}
							></button>
						{/each}
					</div>
				</div>
				<div class="flex justify-end gap-3 pt-2">
					<button type="button" on:click={() => (showModal = false)} class="btn-secondary">Cancel</button>
					<button type="submit" class="btn-primary">{editingSchedule ? 'Save Changes' : 'Create Event'}</button>
				</div>
			</form>
		</div>
	</div>
{/if}
