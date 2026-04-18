<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { ai as aiApi } from '$lib/api';
	import { timeAgo } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import { Plus, Send, Trash2, Bot, User, Sparkles, MessageSquare } from 'lucide-svelte';

	let conversations: any[] = [];
	let activeConv: any = null;
	let messages: any[] = [];
	let input = '';
	let loading = false;
	let sending = false;
	let messagesEl: HTMLElement;

	onMount(async () => {
		loading = true;
		try {
			conversations = await aiApi.listConversations();
			if (conversations.length > 0) {
				await selectConversation(conversations[0]);
			}
		} finally {
			loading = false;
		}
	});

	async function selectConversation(conv: any) {
		activeConv = conv;
		const full = await aiApi.getConversation(conv.id);
		messages = full.messages;
		await scrollToBottom();
	}

	async function newConversation() {
		const conv = await aiApi.createConversation();
		conversations = [conv, ...conversations];
		activeConv = conv;
		messages = [];
	}

	async function deleteConversation(conv: any) {
		if (!confirm('Delete this conversation?')) return;
		try {
			await aiApi.deleteConversation(conv.id);
			conversations = conversations.filter((c) => c.id !== conv.id);
			if (activeConv?.id === conv.id) {
				activeConv = conversations[0] || null;
				messages = activeConv ? (await aiApi.getConversation(activeConv.id)).messages : [];
			}
		} catch (e) {
			toast.error(e.message);
		}
	}

	async function sendMessage() {
		if (!input.trim() || !activeConv || sending) return;
		const content = input.trim();
		input = '';

		messages = [...messages, { id: Date.now(), role: 'user', content, created_at: new Date().toISOString() }];
		await scrollToBottom();

		sending = true;
		try {
			const reply = await aiApi.sendMessage(activeConv.id, content);
			messages = [...messages.slice(0, -1), { id: Date.now() - 1, role: 'user', content, created_at: new Date().toISOString() }, reply];
			conversations = conversations.map((c) => c.id === activeConv.id ? { ...c, title: c.title === 'New Conversation' ? content.slice(0, 40) : c.title } : c);
			await scrollToBottom();
		} catch (e) {
			toast.error(e.message || 'AI error');
			messages = messages.slice(0, -1);
		} finally {
			sending = false;
		}
	}

	async function scrollToBottom() {
		await tick();
		if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			sendMessage();
		}
	}

	const suggestions = [
		'Summarize our current project status',
		'What tasks are most overdue?',
		'Help me write a task description for a user authentication feature',
		'What should I prioritize this week?'
	];
</script>

<svelte:head><title>AI Assistant · TeamFlow</title></svelte:head>

<div class="flex h-screen overflow-hidden">
	<!-- Conversation list -->
	<div class="w-64 flex-shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
		<div class="p-3 border-b border-gray-800">
			<button on:click={newConversation} class="btn-primary w-full justify-center text-xs py-2">
				<Plus size={14} /> New Chat
			</button>
		</div>
		<div class="flex-1 overflow-y-auto p-2 space-y-1">
			{#if loading}
				<div class="flex justify-center py-8">
					<div class="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
				</div>
			{:else if conversations.length === 0}
				<p class="text-gray-600 text-xs text-center py-6">No conversations yet</p>
			{:else}
				{#each conversations as conv}
					<div class="group flex items-center gap-1">
						<button
							on:click={() => selectConversation(conv)}
							class="flex-1 text-left px-3 py-2 rounded-lg text-xs transition-colors truncate {activeConv?.id === conv.id ? 'bg-primary-600/20 text-primary-300' : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'}"
						>
							<p class="truncate font-medium">{conv.title || 'New Chat'}</p>
							<p class="text-gray-600 mt-0.5">{timeAgo(conv.updated_at)}</p>
						</button>
						<button
							on:click={() => deleteConversation(conv)}
							class="p-1 text-gray-600 hover:text-red-400 rounded opacity-0 group-hover:opacity-100 transition-all"
						>
							<Trash2 size={12} />
						</button>
					</div>
				{/each}
			{/if}
		</div>
	</div>

	<!-- Chat area -->
	<div class="flex-1 flex flex-col overflow-hidden">
		{#if !activeConv}
			<div class="flex-1 flex flex-col items-center justify-center p-8 text-center">
				<div class="w-16 h-16 rounded-2xl bg-primary-600/20 flex items-center justify-center mb-4">
					<Sparkles class="text-primary-400" size={32} />
				</div>
				<h2 class="text-xl font-semibold text-white mb-2">AI Project Assistant</h2>
				<p class="text-gray-500 text-sm mb-8 max-w-sm">
					Ask me anything about your projects, tasks, or team. I can help you prioritize, write descriptions, or give status summaries.
				</p>
				<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg w-full">
					{#each suggestions as s}
						<button
							on:click={async () => { await newConversation(); input = s; await sendMessage(); }}
							class="text-left p-3 bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-lg text-xs text-gray-400 hover:text-gray-200 transition-colors"
						>
							{s}
						</button>
					{/each}
				</div>
			</div>
		{:else}
			<!-- Messages -->
			<div bind:this={messagesEl} class="flex-1 overflow-y-auto p-6 space-y-4">
				{#if messages.length === 0}
					<div class="flex flex-col items-center justify-center h-full text-center">
						<MessageSquare class="text-gray-700 mb-3" size={36} />
						<p class="text-gray-500 text-sm">Start the conversation by typing a message below.</p>
					</div>
				{:else}
					{#each messages as msg}
						<div class="flex gap-3 {msg.role === 'user' ? 'flex-row-reverse' : ''}">
							<div class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center {msg.role === 'user' ? 'bg-primary-700' : 'bg-gray-700'}">
								{#if msg.role === 'user'}
									<User size={14} class="text-white" />
								{:else}
									<Bot size={14} class="text-primary-300" />
								{/if}
							</div>
							<div class="max-w-[75%] {msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1">
								<div class="px-4 py-3 rounded-2xl text-sm leading-relaxed {msg.role === 'user' ? 'bg-primary-600 text-white rounded-tr-sm' : 'bg-gray-800 text-gray-200 rounded-tl-sm'}">
									{@html msg.content.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/`(.*?)`/g, '<code class="bg-black/30 px-1 rounded text-xs">$1</code>')}
								</div>
								<p class="text-xs text-gray-600">{timeAgo(msg.created_at)}</p>
							</div>
						</div>
					{/each}
					{#if sending}
						<div class="flex gap-3">
							<div class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
								<Bot size={14} class="text-primary-300" />
							</div>
							<div class="bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3">
								<div class="flex gap-1.5 items-center h-4">
									<span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
									<span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
									<span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
								</div>
							</div>
						</div>
					{/if}
				{/if}
			</div>

			<!-- Input -->
			<div class="p-4 border-t border-gray-800 bg-gray-900/50">
				<div class="flex gap-3 items-end max-w-4xl mx-auto">
					<textarea
						bind:value={input}
						on:keydown={handleKeydown}
						placeholder="Ask anything about your projects and tasks..."
						class="input flex-1 resize-none max-h-32 min-h-[42px]"
						rows="1"
						disabled={sending}
					></textarea>
					<button
						on:click={sendMessage}
						disabled={!input.trim() || sending}
						class="btn-primary px-3 py-2.5 flex-shrink-0 disabled:opacity-40"
					>
						<Send size={16} />
					</button>
				</div>
				<p class="text-xs text-gray-600 text-center mt-2">Press Enter to send, Shift+Enter for new line</p>
			</div>
		{/if}
	</div>
</div>
