(function () {
    'use strict';

    if (window.__ethiobizChatInitialized) return;
    if (frappe.session.user === 'Guest') return;

    const settings = frappe.boot.hadeeda_settings;
    if (!settings || !settings.enabled || !settings.chat_enabled) return;

    window.__ethiobizChatInitialized = true;

    /**
     * Parse NDJSON text (from n8n Formatter node) into clean Markdown text.
     * Extracts all type="item" content fields and concatenates them.
     */
    function parseNDJSON(text) {
        if (!text || !text.includes('"type"')) return null;
        let result = '';
        const lines = text.split('\n');
        for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed) continue;
            try {
                const obj = JSON.parse(trimmed);
                if (obj && obj.type === 'item' && obj.content) {
                    result += obj.content;
                } else if (obj && obj.type === 'error' && obj.content) {
                    // Suppress internal n8n errors, return friendly message
                    return '⚠️ I encountered an issue processing your request. Please try again.';
                }
            } catch (e) {
                // Not valid JSON line, skip
            }
        }
        return result || null;
    }

    /**
     * Extract clean output text from any response format.
     * Handles: NDJSON, {"output": "..."}, [{"output": "..."}],
     * {"message": {"output": "..."}}, raw text
     */
    function extractOutput(text) {
        if (!text) return '';

        // 1. Try NDJSON
        const ndjsonResult = parseNDJSON(text);
        if (ndjsonResult) return ndjsonResult;

        // 2. Try JSON
        try {
            const data = JSON.parse(text);

            // Frappe wraps: {"message": {"output": "..."}}
            if (data.message && typeof data.message === 'object' && data.message.output) {
                return data.message.output;
            }
            // Frappe wraps: {"message": "text"}
            if (data.message && typeof data.message === 'string') {
                return data.message;
            }
            // Direct: {"output": "..."}
            if (data.output) return data.output;
            // Array: [{"output": "..."}]
            if (Array.isArray(data) && data.length > 0) {
                const item = data[0];
                if (item.output) return item.output;
                if (item.json && item.json.output) return item.json.output;
                if (item.message) return item.message;
            }
            return text;
        } catch (e) {
            return text;
        }
    }

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

            // Use the server-side proxy URL
            const proxyUrl = window.location.origin + '/api/method/bismillah_ethiobiz.api.chat_webhook_proxy';

            // Intercept fetch calls to the proxy URL so we can guarantee
            // clean output regardless of Frappe response wrapping or NDJSON format
            const originalFetch = window.fetch;
            window.fetch = async function (url, options) {
                const urlStr = typeof url === 'string' ? url : (url && url.url ? url.url : '');

                if (urlStr.includes('chat_webhook_proxy')) {
                    try {
                        const response = await originalFetch.call(window, url, options);
                        const rawText = await response.text();
                        const cleanOutput = extractOutput(rawText);

                        // Return a synthetic Response with the exact format @n8n/chat expects
                        return new Response(JSON.stringify({ output: cleanOutput }), {
                            status: 200,
                            statusText: 'OK',
                            headers: { 'Content-Type': 'application/json' }
                        });
                    } catch (fetchErr) {
                        console.warn('HADEEDA proxy fetch error:', fetchErr);
                        return new Response(JSON.stringify({ output: '⚠️ Connection error. Please try again.' }), {
                            status: 200,
                            headers: { 'Content-Type': 'application/json' }
                        });
                    }
                }

                // All other fetch calls pass through unchanged
                return originalFetch.call(window, url, options);
            };

            // Inject theme CSS — matching biztechnology.et dark theme
            const style = document.createElement('style');
            style.textContent = `
                :root {
                    --chat--color--primary: ${config.widget_primary_color || '#7C3AED'};
                    --chat--color--primary-shade-50: #6D28D9;
                    --chat--color--primary--shade-100: #5B21B6;
                    --chat--color--secondary: #2581CD;
                    --chat--color-secondary-shade-50: #1E6FB5;
                    --chat--color-white: #F0F4F8;
                    --chat--color-light: #161B22;
                    --chat--color-light-shade-50: #1C2333;
                    --chat--color-light-shade-100: #2D333B;
                    --chat--color-medium: #30363D;
                    --chat--color-dark: #0D1117;
                    --chat--color-disabled: #484F58;
                    --chat--color-typing: #8B949E;
                    --chat--window--width: 400px;
                    --chat--window--height: 600px;
                    --chat--window--border-radius: 20px;
                    --chat--message--border-radius: 14px;
                    --chat--toggle--size: 56px;
                    --chat--toggle--background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%);
                    --chat--toggle--hover--background: linear-gradient(135deg, #6D28D9 0%, #4C1D95 100%);
                    --chat--toggle--active--background: #5B21B6;
                    --chat--toggle--color: #FFFFFF;
                    --chat--window--right: var(--chat--spacing);
                    --chat--window--bottom: var(--chat--spacing);
                    --chat--window--z-index: 9999;
                }

                /* ─── KEYFRAMES ─── */
                @keyframes hadeeda-toggle-enter {
                    0%   { opacity: 0; transform: scale(0.3) translateY(40px); }
                    50%  { opacity: 1; transform: scale(1.08) translateY(-4px); }
                    70%  { transform: scale(0.96) translateY(1px); }
                    100% { opacity: 1; transform: scale(1) translateY(0); }
                }
                @keyframes hadeeda-toggle-glow {
                    0%, 100% { box-shadow: 0 4px 20px rgba(124,58,237,0.35), 0 0 0 2px rgba(13,17,23,0.6); }
                    50%      { box-shadow: 0 4px 28px rgba(124,58,237,0.55), 0 0 0 2px rgba(13,17,23,0.6), 0 0 50px rgba(124,58,237,0.12); }
                }
                @keyframes hadeeda-window-open {
                    0%   { opacity: 0; transform: scale(0.88) translateY(20px); }
                    60%  { opacity: 1; transform: scale(1.015) translateY(-2px); }
                    100% { opacity: 1; transform: scale(1) translateY(0); }
                }
                @keyframes hadeeda-msg-in-left {
                    0%   { opacity: 0; transform: translateX(-16px) scale(0.96); }
                    100% { opacity: 1; transform: translateX(0) scale(1); }
                }
                @keyframes hadeeda-msg-in-right {
                    0%   { opacity: 0; transform: translateX(16px) scale(0.96); }
                    100% { opacity: 1; transform: translateX(0) scale(1); }
                }
                @keyframes hadeeda-typing-bounce {
                    0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
                    40% { transform: translateY(-6px); opacity: 1; }
                }
                @keyframes hadeeda-shimmer {
                    0%   { background-position: -200% center; }
                    100% { background-position: 200% center; }
                }
                @keyframes hadeeda-send-glow {
                    0%, 100% { box-shadow: 0 0 0 0 rgba(124,58,237,0); }
                    50%      { box-shadow: 0 0 14px 2px rgba(124,58,237,0.4); }
                }

                /* ─── TOGGLE BUTTON ─── */
                .chat-window-wrapper .chat-window-toggle .chat-icon,
                .chat-window-wrapper .chat-window-toggle svg { display: none !important; }

                .chat-window-wrapper .chat-window-toggle {
                    width: auto !important; min-width: 56px !important; height: 56px !important;
                    border-radius: 28px !important;
                    background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
                    color: #fff !important; padding: 0 1.1rem 0 0.6rem !important;
                    gap: 0.45rem !important; cursor: pointer !important; white-space: nowrap !important;
                    border: none !important; position: relative !important;
                    animation: hadeeda-toggle-enter 0.7s cubic-bezier(0.34,1.56,0.64,1) both,
                               hadeeda-toggle-glow 3s ease-in-out 0.8s infinite !important;
                    box-shadow: 0 4px 20px rgba(124,58,237,0.35), 0 0 0 2px rgba(13,17,23,0.6) !important;
                }
                .chat-window-wrapper .chat-window-toggle::before {
                    content: 'HADEEDA AI' !important;
                    font-family: "Inter","Segoe UI",system-ui,sans-serif !important;
                    font-weight: 700 !important; font-size: 0.8rem !important;
                    color: #fff !important; order: 1 !important;
                    text-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
                }
                .chat-window-wrapper .chat-window-toggle::after {
                    content: 'H' !important; display: inline-flex !important;
                    align-items: center !important; justify-content: center !important;
                    width: 34px !important; height: 34px !important; border-radius: 50% !important;
                    background: rgba(255,255,255,0.18) !important; font-weight: 800 !important;
                    font-size: 16px !important; flex-shrink: 0 !important; order: 0 !important;
                }
                .chat-window-wrapper .chat-window-toggle:hover {
                    transform: translateY(-3px) scale(1.06) !important;
                    box-shadow: 0 10px 40px rgba(124,58,237,0.55), 0 0 0 2px rgba(13,17,23,0.6) !important;
                    animation: none !important;
                }

                /* ─── CHAT WINDOW ─── */
                .chat-window-wrapper .chat-window {
                    background: #0D1117 !important;
                    border: 1px solid rgba(124,58,237,0.12) !important;
                    border-radius: 20px !important; overflow: hidden !important;
                    animation: hadeeda-window-open 0.45s cubic-bezier(0.34,1.56,0.64,1) both !important;
                    box-shadow: 0 0 0 1px rgba(124,58,237,0.08), 0 4px 16px rgba(0,0,0,0.3),
                                0 20px 60px rgba(0,0,0,0.45) !important;
                }

                /* ─── HEADER ─── */
                .chat-layout .chat-header {
                    background: linear-gradient(160deg, #0D1117 0%, #121929 40%, #1a1040 100%) !important;
                    color: #F0F4F8 !important; position: relative !important; overflow: hidden !important;
                }
                .chat-layout .chat-header::after {
                    content: '' !important; position: absolute !important;
                    bottom: 0 !important; left: 0 !important; right: 0 !important; height: 2px !important;
                    background: linear-gradient(90deg, transparent 0%, #7C3AED 20%, #2581CD 50%, #7C3AED 80%, transparent 100%) !important;
                    background-size: 200% 100% !important;
                    animation: hadeeda-shimmer 3s linear infinite !important; z-index: 1 !important;
                }

                /* ─── MESSAGES ─── */
                .chat-layout .chat-body { background: #0D1117 !important; }

                .chat-message.chat-message-from-bot:not(.chat-message-transparent) {
                    background: #161B22 !important; color: #E6EDF3 !important;
                    border: 1px solid rgba(124,58,237,0.06) !important;
                    border-left: 3px solid rgba(124,58,237,0.30) !important;
                    border-radius: 4px 14px 14px 14px !important;
                    animation: hadeeda-msg-in-left 0.4s cubic-bezier(0.34,1.56,0.64,1) both !important;
                }
                .chat-message.chat-message-from-bot a { color: #7C3AED !important; }
                .chat-message.chat-message-from-bot a:hover { color: #2581CD !important; }

                .chat-message.chat-message-from-user:not(.chat-message-transparent) {
                    background: linear-gradient(135deg, #7C3AED 0%, #2581CD 100%) !important;
                    color: #fff !important; border-radius: 14px 4px 14px 14px !important;
                    animation: hadeeda-msg-in-right 0.4s cubic-bezier(0.34,1.56,0.64,1) both !important;
                    box-shadow: 0 2px 12px rgba(124,58,237,0.22) !important;
                }

                /* ─── TYPING ─── */
                .chat-message-typing-circle { background: #7C3AED !important; animation: hadeeda-typing-bounce 1.4s ease-in-out infinite !important; }
                .chat-message-typing-circle:nth-child(2) { animation-delay: 0.16s !important; }
                .chat-message-typing-circle:nth-child(3) { animation-delay: 0.32s !important; }

                /* ─── INPUT ─── */
                .chat-layout .chat-footer { background: #0D1117 !important; border-top: 1px solid rgba(124,58,237,0.08) !important; }
                .chat-input { background: #0D1117 !important; color: #F0F4F8 !important; border: 2px solid transparent !important; border-radius: 12px !important; }
                .chat-input:focus { border-color: rgba(124,58,237,0.3) !important; box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important; }
                .chat-input::placeholder { color: #8B949E !important; }
                .chat-input-send-button {
                    background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
                    color: #fff !important; border: none !important; border-radius: 10px !important;
                }
                .chat-input-send-button:hover { transform: scale(1.08) !important; animation: hadeeda-send-glow 1.5s ease-in-out infinite !important; }

                /* ─── SCROLLBAR ─── */
                .chat-messages-list::-webkit-scrollbar { width: 4px !important; }
                .chat-messages-list::-webkit-scrollbar-track { background: transparent !important; }
                .chat-messages-list::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #7C3AED, #2581CD) !important; border-radius: 2px !important; }

                /* ─── MOBILE ─── */
                @media (max-width: 480px) {
                    .chat-window-wrapper .chat-window { width: calc(100vw - 1rem) !important; height: calc(100vh - 5rem) !important; border-radius: 16px 16px 0 0 !important; }
                    .chat-window-wrapper .chat-window-toggle { height: 50px !important; min-width: 50px !important; }
                }
            `;
            document.head.appendChild(style);

            const initialMessages = (config.initial_messages && config.initial_messages.length > 0)
                ? config.initial_messages
                : ['Selam! 👋', 'I am HADEEDA, your AI Executive Assistant. How can I help you today?'];

            const sessionId = config.session_id || config.username;
            localStorage.setItem('n8n-chat-sessionId', sessionId);

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
