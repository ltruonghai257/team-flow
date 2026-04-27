import { request } from './request';

export const chat = {
    listChannels: () => request('/chat/channels'),
    myChannels: () => request('/chat/channels/my'),
    createChannel: (name: string, description?: string) =>
        request('/chat/channels', {
            method: 'POST',
            body: JSON.stringify({ name, description }),
        }),
};
