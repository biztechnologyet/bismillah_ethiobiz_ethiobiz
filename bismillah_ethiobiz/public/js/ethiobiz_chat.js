(function () {
    'use strict';

    if (window.__ethiobizChatInitialized) return;
    if (frappe.session.user === 'Guest') return;

    const settings = frappe.boot.hadeeda_settings;
    if (!settings || !settings.enabled || !settings.chat_enabled) return;

    window.__ethiobizChatInitialized = true;

    async function initChat() {
        try {
            const resp = await fetch('/api/method/bismillah_ethiobiz.api.get_chat_config');
            const json = await resp.json();
            const config = json.message || json;

            if (!config.enabled) return;

            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdn.jsdelivr.net/npm/@n8n/chat/dist/style.css';
            document.head.appendChild(link);

            const { createChat } = await import('https://cdn.jsdelivr.net/npm/@n8n/chat/dist/chat.bundle.es.js');

            const style = document.createElement('style');
            style.textContent = `
                :root {
                    --chat--color--primary: ${config.widget_primary_color};
                    --chat--color--secondary: ${config.widget_primary_color};
                    --chat--toggle--background: ${config.widget_primary_color};
                    --chat--window--right: var(--chat--spacing);
                    --chat--window--bottom: var(--chat--spacing);
                    --chat--window--z-index: 9999;
                }
            `;
            document.head.appendChild(style);

            const initialMessages = (config.initial_messages && config.initial_messages.length > 0)
                ? config.initial_messages
                : ['Selam! 👋', 'I am HADEEDA, your AI Executive Assistant. How can I help you today?'];

            const sessionId = config.session_id || config.username;

            localStorage.setItem('n8n-chat-sessionId', sessionId);

            createChat({
                webhookUrl: config.webhook_url,
                webhookConfig: {
                    headers: {
                        'X-Frappe-User': config.username,
                        'X-Frappe-Company': config.company,
                    }
                },
                mode: config.widget_mode || 'window',
                chatSessionKey: 'sessionId',
                chatInputKey: 'chatInput',
                loadPreviousSession: true,
                showWelcomeScreen: false,
                defaultLanguage: config.default_language || 'en',
                initialMessages: initialMessages,
                allowFileUploads: config.allow_file_uploads,
                allowedFilesMimeTypes: config.allowed_mime_types || '',
                metadata: {
                    username: config.username,
                    full_name: config.full_name,
                    email: config.email,
                    company: config.company,
                    api_key: config.api_key,
                    api_secret: config.api_secret,
                    source: 'widget',
                },
                i18n: {
                    en: {
                        title: config.widget_title || 'HADEEDA AI Assistant',
                        subtitle: config.widget_subtitle || '',
                        footer: '',
                        getStarted: 'New Conversation',
                        inputPlaceholder: 'Type your message...',
                    },
                },
            });
        } catch (e) {
            console.warn('HADEEDA Chat init failed:', e);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChat);
    } else {
        initChat();
    }
})();
