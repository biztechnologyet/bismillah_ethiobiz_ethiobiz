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

            // Load @n8n/chat stylesheet
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdn.jsdelivr.net/npm/@n8n/chat@1.30.2/dist/style.css';
            document.head.appendChild(link);

            // Import createChat from @n8n/chat bundle
            const { createChat } = await import('https://cdn.jsdelivr.net/npm/@n8n/chat@1.30.2/dist/chat.bundle.es.js');

            // Inject theme CSS + Typography & Line Break Formatting
            const style = document.createElement('style');
            style.textContent = `
                :root {
                    --chat--color--primary: ${config.widget_primary_color || '#1FB6AE'};
                    --chat--color--secondary: ${config.widget_primary_color || '#1FB6AE'};
                    --chat--toggle--background: ${config.widget_primary_color || '#1FB6AE'};
                    --chat--window--right: var(--chat--spacing);
                    --chat--window--bottom: var(--chat--spacing);
                    --chat--window--z-index: 9999;
                }

                /* Ensure line breaks (\\n) and whitespace formatting render smoothly */
                .chat-message,
                .chat-message-from-bot,
                .chat-message-from-user,
                .chat-message-text,
                .chat-message-content,
                .chat-message-body {
                    white-space: pre-wrap !important;
                    word-break: break-word !important;
                    line-height: 1.6 !important;
                    font-size: 14px !important;
                }

                .chat-message-from-bot {
                    background: #161B22 !important;
                    color: #E6EDF3 !important;
                    border: 1px solid rgba(31, 182, 174, 0.2) !important;
                    border-left: 3px solid #1FB6AE !important;
                    border-radius: 4px 14px 14px 14px !important;
                    padding: 12px 14px !important;
                }

                .chat-message-from-user {
                    background: linear-gradient(135deg, #1FB6AE 0%, #178a84 100%) !important;
                    color: #FFFFFF !important;
                    border-radius: 14px 4px 14px 14px !important;
                    padding: 12px 14px !important;
                }
            `;
            document.head.appendChild(style);

            const initialMessages = (config.initial_messages && config.initial_messages.length > 0)
                ? config.initial_messages
                : ['Selam! 👋', 'I am HADEEDA, your AI Executive Assistant. How can I help you today?'];

            const sessionId = config.session_id || config.username;
            localStorage.setItem('n8n-chat-sessionId', sessionId);

            // Proxy URL for server-side response parsing
            const proxyUrl = window.location.origin + '/api/method/bismillah_ethiobiz.api.chat_webhook_proxy';

            createChat({
                webhookUrl: proxyUrl,
                mode: config.widget_mode || 'window',
                chatSessionKey: 'sessionId',
                chatInputKey: 'chatInput',
                loadPreviousSession: false,
                enableStreaming: false,
                showWelcomeScreen: false,
                defaultLanguage: config.default_language || 'en',
                initialMessages: initialMessages,
                allowFileUploads: Boolean(config.allow_file_uploads),
                allowedFilesMimeTypes: config.allowed_mime_types || '',
                metadata: {
                    username: config.username,
                    full_name: config.full_name,
                    email: config.email,
                    company: config.company,
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
