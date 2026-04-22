/**
 * WebSocket service for real-time chat.
 *
 * Single multiplexed connection used for assistant chat, team channels,
 * direct messages, and presence updates.
 */

type Listener = (msg: any) => void;

class ChatWebSocket {
	private ws: WebSocket | null = null;
	private url: string;
	private listeners = new Set<Listener>();
	private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private explicitlyClosed = false;
	private connectingPromise: Promise<void> | null = null;

	constructor() {
		const proto = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss' : 'ws';
		const host = typeof window !== 'undefined' ? window.location.host : 'localhost:5173';
		this.url = `${proto}://${host}/ws/chat`;
	}

	get isOpen(): boolean {
		return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
	}

	connect(): Promise<void> {
		if (this.isOpen) return Promise.resolve();
		if (this.connectingPromise) return this.connectingPromise;
		this.explicitlyClosed = false;

		this.connectingPromise = new Promise((resolve, reject) => {
			try {
				this.ws = new WebSocket(this.url);
			} catch (e) {
				this.connectingPromise = null;
				reject(e);
				return;
			}

			this.ws.onopen = () => {
				this.reconnectAttempts = 0;
				this.startHeartbeat();
				this.connectingPromise = null;
				resolve();
			};

			this.ws.onmessage = (ev) => {
				try {
					const msg = JSON.parse(ev.data);
					this.listeners.forEach((l) => l(msg));
				} catch {
					// ignore malformed
				}
			};

			this.ws.onclose = () => {
				this.stopHeartbeat();
				this.ws = null;
				this.connectingPromise = null;
				if (!this.explicitlyClosed) this.scheduleReconnect();
			};

			this.ws.onerror = () => {
				// onclose will follow
			};
		});

		return this.connectingPromise;
	}

	close(): void {
		this.explicitlyClosed = true;
		this.stopHeartbeat();
		this.ws?.close();
		this.ws = null;
	}

	send(msg: object): void {
		if (this.isOpen) {
			this.ws!.send(JSON.stringify(msg));
		} else {
			// Fire-and-forget if not open; could enhance with queueing.
			this.connect().then(() => this.ws?.send(JSON.stringify(msg))).catch(() => {});
		}
	}

	on(listener: Listener): () => void {
		this.listeners.add(listener);
		return () => this.listeners.delete(listener);
	}

	private startHeartbeat(): void {
		this.stopHeartbeat();
		this.heartbeatTimer = setInterval(() => {
			if (this.isOpen) this.ws!.send(JSON.stringify({ type: 'heartbeat' }));
		}, 30000);
	}

	private stopHeartbeat(): void {
		if (this.heartbeatTimer) {
			clearInterval(this.heartbeatTimer);
			this.heartbeatTimer = null;
		}
	}

	private scheduleReconnect(): void {
		if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
		const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
		this.reconnectAttempts++;
		setTimeout(() => {
			if (!this.explicitlyClosed) this.connect().catch(() => {});
		}, delay);
	}
}

export const chatWS = new ChatWebSocket();
