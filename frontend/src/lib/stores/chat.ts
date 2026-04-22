import { writable, get } from 'svelte/store';
import { chatWS } from '$lib/websocket';

export interface ChatMessage {
	id: number;
	sender_id: number;
	sender_name?: string;
	channel_id?: number | null;
	conversation_id?: number | null;
	content: string;
	created_at: string;
}

export interface PresenceInfo {
	user_id: number;
	is_online: boolean;
	custom_status?: string | null;
	last_seen?: string | null;
}

export interface DMConversation {
	conversation_id: number;
	other_user_id: number;
	other_user_name: string;
	last_message: string | null;
	last_message_at: string;
}

interface AssistantStreamMsg {
	id: string;
	role: 'user' | 'assistant';
	content: string;
	streaming?: boolean;
}

interface ChatState {
	connected: boolean;
	channelMessages: Record<number, ChatMessage[]>;
	dmMessages: Record<number, ChatMessage[]>; // conversation_id -> messages
	dmConversations: DMConversation[];
	presence: Record<number, PresenceInfo>;
	assistantMessages: AssistantStreamMsg[];
	assistantStreaming: boolean;
}

const initial: ChatState = {
	connected: false,
	channelMessages: {},
	dmMessages: {},
	dmConversations: [],
	presence: {},
	assistantMessages: [],
	assistantStreaming: false
};

function createChatStore() {
	const { subscribe, update, set } = writable<ChatState>(initial);
	let unsubscribeWS: (() => void) | null = null;
	let currentAssistantId: string | null = null;

	function handleMessage(msg: any) {
		switch (msg.type) {
			case 'heartbeat_ack':
				break;
			case 'presence_initial':
				update((s) => {
					const presence: Record<number, PresenceInfo> = {};
					for (const u of msg.users) presence[u.user_id] = u;
					return { ...s, presence };
				});
				break;
			case 'presence_update':
				update((s) => ({
					...s,
					presence: { ...s.presence, [msg.user_id]: { user_id: msg.user_id, is_online: msg.is_online, custom_status: msg.custom_status } }
				}));
				break;
			case 'presence_status':
				update((s) => ({ ...s, presence: { ...s.presence, [msg.user_id]: { user_id: msg.user_id, is_online: msg.is_online, custom_status: msg.custom_status, last_seen: msg.last_seen } } }));
				break;
			case 'presence_batch':
				update((s) => {
					const presence = { ...s.presence };
					for (const u of msg.users) presence[u.user_id] = u;
					return { ...s, presence };
				});
				break;
			case 'channel_history':
				update((s) => ({
					...s,
					channelMessages: { ...s.channelMessages, [msg.channel_id]: msg.messages }
				}));
				break;
			case 'channel_message':
				update((s) => {
					const list = s.channelMessages[msg.channel_id] || [];
					return {
						...s,
						channelMessages: { ...s.channelMessages, [msg.channel_id]: [...list, msg] }
					};
				});
				break;
			case 'dm_history':
				update((s) => ({
					...s,
					dmMessages: { ...s.dmMessages, [msg.conversation_id]: msg.messages }
				}));
				break;
			case 'dm_message':
			case 'dm_sent':
				update((s) => {
					const list = s.dmMessages[msg.conversation_id] || [];
					// Avoid duplicating: dm_sent and dm_message can both arrive for the sender
					if (list.some((m) => m.id === msg.id)) return s;
					return {
						...s,
						dmMessages: { ...s.dmMessages, [msg.conversation_id]: [...list, msg] }
					};
				});
				break;
			case 'dm_conversation_list':
				update((s) => ({ ...s, dmConversations: msg.conversations }));
				break;
			case 'dm_conversation':
				// Triggered after dm_start
				break;
			case 'assistant_chunk':
				update((s) => {
					const messages = [...s.assistantMessages];
					const last = messages[messages.length - 1];
					if (last && last.role === 'assistant' && last.streaming) {
						last.content += msg.content;
					} else {
						currentAssistantId = `a_${Date.now()}`;
						messages.push({ id: currentAssistantId, role: 'assistant', content: msg.content, streaming: true });
					}
					return { ...s, assistantMessages: messages, assistantStreaming: true };
				});
				break;
			case 'assistant_done':
				update((s) => {
					const messages = [...s.assistantMessages];
					const last = messages[messages.length - 1];
					if (last && last.role === 'assistant' && last.streaming) {
						last.content = msg.content;
						last.streaming = false;
					}
					return { ...s, assistantMessages: messages, assistantStreaming: false };
				});
				currentAssistantId = null;
				break;
			case 'assistant_cancelled':
				update((s) => ({ ...s, assistantStreaming: false }));
				currentAssistantId = null;
				break;
			case 'assistant_reset_ack':
				update((s) => ({ ...s, assistantMessages: [], assistantStreaming: false }));
				break;
			case 'error':
				console.warn('Chat WS error:', msg.message);
				break;
		}
	}

	return {
		subscribe,
		async connect() {
			if (unsubscribeWS) return;
			unsubscribeWS = chatWS.on(handleMessage);
			await chatWS.connect();
			update((s) => ({ ...s, connected: true }));
		},
		disconnect() {
			if (unsubscribeWS) {
				unsubscribeWS();
				unsubscribeWS = null;
			}
			chatWS.close();
			set(initial);
		},
		// Channel ops
		joinChannel(channel_id: number) {
			chatWS.send({ type: 'channel_join', channel_id });
		},
		leaveChannel(channel_id: number) {
			chatWS.send({ type: 'channel_leave', channel_id });
		},
		sendChannelMessage(channel_id: number, content: string) {
			chatWS.send({ type: 'channel_message', channel_id, content });
		},
		// DM ops
		startDM(recipient_id: number) {
			chatWS.send({ type: 'dm_start', recipient_id });
		},
		sendDM(recipient_id: number, content: string, conversation_id?: number) {
			// Optimistic local echo
			if (conversation_id) {
				const tempId = -Date.now();
				update((s) => {
					const list = s.dmMessages[conversation_id] || [];
					return {
						...s,
						dmMessages: {
							...s.dmMessages,
							[conversation_id]: [
								...list,
								{ id: tempId, sender_id: -1, content, conversation_id, created_at: new Date().toISOString(), sender_name: 'You' }
							]
						}
					};
				});
			}
			chatWS.send({ type: 'dm_message', recipient_id, content });
		},
		loadDMHistory(other_user_id: number) {
			chatWS.send({ type: 'dm_history', other_user_id });
		},
		loadDMConversations() {
			chatWS.send({ type: 'dm_conversations' });
		},
		// Presence
		setStatus(status: string) {
			chatWS.send({ type: 'presence_status_set', status });
		},
		clearStatus() {
			chatWS.send({ type: 'presence_status_clear' });
		},
		queryPresenceBatch(user_ids: number[]) {
			chatWS.send({ type: 'presence_query_batch', user_ids });
		},
		// Assistant
		sendAssistantMessage(content: string) {
			update((s) => ({
				...s,
				assistantMessages: [...s.assistantMessages, { id: `u_${Date.now()}`, role: 'user', content }],
				assistantStreaming: true
			}));
			chatWS.send({ type: 'assistant_message', content });
		},
		cancelAssistant() {
			chatWS.send({ type: 'assistant_cancel' });
		},
		resetAssistant() {
			chatWS.send({ type: 'assistant_reset' });
		}
	};
}

export const chatStore = createChatStore();
