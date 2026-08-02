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
                    return 'As-salamu alaykum! I am currently synchronizing my AI workflow. Please try again in a moment, InshaAllah!';
                }
            } catch (e) {
                // Not valid JSON line, skip
            }
        }
        return result || null;
    }

    /**
     * Extract clean output text from any response format.
     */
    function extractOutput(text) {
        if (!text) return '';

        // Catch CSRF or Frappe error responses gracefully
        if (text.includes('CSRFTokenError') || text.includes('exc_type') || text.includes('Invalid Request')) {
            return 'As-salamu alaykum! I am ready to assist you. Please send your message again, InshaAllah!';
        }

        const ndjsonResult = parseNDJSON(text);
        if (ndjsonResult) return ndjsonResult;

        try {
            const data = JSON.parse(text);

            if (data.message && typeof data.message === 'object' && data.message.output) {
                return data.message.output;
            }
            if (data.message && typeof data.message === 'string') {
                return data.message;
            }
            if (data.output) return data.output;
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

            const proxyUrl = window.location.origin + '/api/method/bismillah_ethiobiz.api.chat_webhook_proxy';

            // Intercept fetch calls to the proxy URL and inject CSRF token header
            const originalFetch = window.fetch;
            window.fetch = async function (url, options) {
                const urlStr = typeof url === 'string' ? url : (url && url.url ? url.url : '');

                if (urlStr.includes('chat_webhook_proxy')) {
                    try {
                        const opts = options || {};
                        opts.headers = opts.headers || {};
                        if (frappe && frappe.csrf_token) {
                            if (opts.headers instanceof Headers) {
                                opts.headers.set('X-Frappe-CSRF-Token', frappe.csrf_token);
                            } else {
                                opts.headers['X-Frappe-CSRF-Token'] = frappe.csrf_token;
                            }
                        }

                        const response = await originalFetch.call(window, url, opts);
                        const rawText = await response.text();
                        const cleanOutput = extractOutput(rawText);

                        return new Response(JSON.stringify({ output: cleanOutput }), {
                            status: 200,
                            statusText: 'OK',
                            headers: { 'Content-Type': 'application/json' }
                        });
                    } catch (fetchErr) {
                        console.warn('HADEEDA proxy fetch error:', fetchErr);
                        return new Response(JSON.stringify({ output: 'As-salamu alaykum! I am ready to assist you. Please try again, InshaAllah!' }), {
                            status: 200,
                            headers: { 'Content-Type': 'application/json' }
                        });
                    }
                }

                return originalFetch.call(window, url, options);
            };

            // Inject theme CSS — modern, simple translucent glassmorphism theme
            const style = document.createElement('style');
            style.textContent = `
                :root {
                    --chat--color--primary: ${config.widget_primary_color || '#1FB6AE'} !important;
                    --chat--color--primary-shade-50: #19a095 !important;
                    --chat--color--primary--shade-100: #147974 !important;
                    --chat--color--secondary: #1FB6AE !important;
                    --chat--color-secondary-shade-50: #19a095 !important;
                    --chat--color-white: #FFFFFF !important;
                    --chat--color-light: #161B22 !important;
                    --chat--color-light-shade-50: #1C2333 !important;
                    --chat--color-light-shade-100: #2D333B !important;
                    --chat--color-medium: #30363D !important;
                    --chat--color-dark: #0D1117 !important;
                    --chat--color-disabled: #484F58 !important;
                    --chat--color-typing: #1FB6AE !important;
                    --chat--window--width: 420px !important;
                    --chat--window--height: 620px !important;
                    --chat--window--border-radius: 18px !important;
                    --chat--message--border-radius: 12px !important;
                    --chat--toggle--size: 56px !important;
                    --chat--toggle--background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%) !important;
                    --chat--toggle--hover--background: linear-gradient(135deg, #25c9c1 0%, #19a095 100%) !important;
                    --chat--toggle--active--background: #147974 !important;
                    --chat--toggle--color: #FFFFFF !important;
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
                    0%, 100% { box-shadow: 0 4px 20px rgba(31,182,174,0.35), 0 0 0 2px rgba(13,17,23,0.6); }
                    50%      { box-shadow: 0 4px 28px rgba(31,182,174,0.55), 0 0 0 2px rgba(13,17,23,0.6), 0 0 50px rgba(31,182,174,0.15); }
                }
                @keyframes hadeeda-window-open {
                    0%   { opacity: 0; transform: scale(0.92) translateY(16px); }
                    100% { opacity: 1; transform: scale(1) translateY(0); }
                }

                /* ─── TOGGLE BUTTON ─── */
                .chat-window-wrapper .chat-window-toggle .chat-icon,
                .chat-window-wrapper .chat-window-toggle svg { display: none !important; }

                .chat-window-wrapper .chat-window-toggle {
                    width: auto !important; min-width: 56px !important; height: 56px !important;
                    border-radius: 28px !important;
                    background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%) !important;
                    color: #FFFFFF !important; padding: 0 1.1rem 0 0.6rem !important;
                    gap: 0.45rem !important; cursor: pointer !important; white-space: nowrap !important;
                    border: none !important; position: relative !important;
                    animation: hadeeda-toggle-enter 0.7s cubic-bezier(0.34,1.56,0.64,1) both,
                               hadeeda-toggle-glow 3s ease-in-out 0.8s infinite !important;
                    box-shadow: 0 4px 20px rgba(31,182,174,0.35), 0 0 0 2px rgba(13,17,23,0.6) !important;
                }
                .chat-window-wrapper .chat-window-toggle::before {
                    content: 'HADEEDA AI' !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                    font-weight: 700 !important; font-size: 0.85rem !important;
                    color: #FFFFFF !important; order: 1 !important;
                    text-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
                }
                .chat-window-wrapper .chat-window-toggle::after {
                    content: 'H' !important; display: inline-flex !important;
                    align-items: center !important; justify-content: center !important;
                    width: 34px !important; height: 34px !important; border-radius: 50% !important;
                    background: rgba(255,255,255,0.22) !important; font-weight: 800 !important;
                    font-size: 16px !important; flex-shrink: 0 !important; order: 0 !important;
                    color: #FFFFFF !important;
                }
                .chat-window-wrapper .chat-window-toggle:hover {
                    background: linear-gradient(135deg, #25c9c1 0%, #19a095 100%) !important;
                    transform: translateY(-2px) scale(1.04) !important;
                    box-shadow: 0 10px 30px rgba(31,182,174,0.5), 0 0 0 2px rgba(13,17,23,0.6) !important;
                    animation: none !important;
                }

                /* ─── MODERN TRANSLUCENT GLASS CHAT WINDOW ─── */
                .chat-window-wrapper .chat-window {
                    background: rgba(13, 17, 23, 0.92) !important;
                    backdrop-filter: blur(20px) saturate(180%) !important;
                    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                    border: 1px solid rgba(31, 182, 174, 0.35) !important;
                    border-radius: 18px !important; overflow: hidden !important;
                    animation: hadeeda-window-open 0.3s ease-out both !important;
                    box-shadow: 0 16px 48px rgba(0,0,0,0.65), 0 0 24px rgba(31,182,174,0.18) !important;
                }

                /* ─── HEADER ─── */
                .chat-layout .chat-header,
                .chat-header {
                    background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%) !important;
                    color: #FFFFFF !important; position: relative !important; overflow: hidden !important;
                    padding: 12px 16px !important;
                }
                .chat-layout .chat-header h1,
                .chat-layout .chat-header .chat-title,
                .chat-header h1,
                .chat-header .chat-title {
                    color: #FFFFFF !important; font-weight: 700 !important; font-size: 14.5px !important;
                }
                .chat-header-close,
                .chat-header button {
                    color: #FFFFFF !important; opacity: 0.85 !important;
                    background: transparent !important; border: none !important;
                }
                .chat-header-close:hover,
                .chat-header button:hover {
                    opacity: 1 !important; color: #FFFFFF !important; background: rgba(255,255,255,0.2) !important;
                    border-radius: 50% !important;
                }

                /* ─── MESSAGES BODY ─── */
                .chat-layout .chat-body,
                .chat-body,
                .chat-messages-list {
                    background: transparent !important;
                }

                .chat-message.chat-message-from-bot:not(.chat-message-transparent) {
                    background: #161B22 !important; color: #FFFFFF !important;
                    border: 1px solid rgba(31, 182, 174, 0.25) !important;
                    border-left: 3px solid #1FB6AE !important;
                    border-radius: 4px 12px 12px 12px !important;
                    line-height: 1.5 !important; font-size: 13px !important;
                }
                .chat-message.chat-message-from-bot a { color: #1FB6AE !important; }
                .chat-message.chat-message-from-bot a:hover { color: #25c9c1 !important; }

                .chat-message.chat-message-from-user:not(.chat-message-transparent) {
                    background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%) !important;
                    color: #FFFFFF !important; border-radius: 12px 4px 12px 12px !important;
                    line-height: 1.5 !important; font-size: 13px !important;
                    box-shadow: 0 2px 10px rgba(31,182,174,0.25) !important;
                }

                /* ─── TYPING ─── */
                .chat-message-typing-circle { background: #1FB6AE !important; }

                /* ─── HIGH-CONTRAST TEXTBOX INPUT & FOOTER ─── */
                .chat-layout .chat-footer,
                .chat-footer,
                .chat-inputs,
                .chat-input-wrapper {
                    background: #0D1117 !important;
                    border-top: 1px solid rgba(31, 182, 174, 0.25) !important;
                    padding: 10px 14px !important;
                }

                .chat-input,
                textarea.chat-input,
                input.chat-input,
                .chat-inputs textarea,
                .chat-inputs input {
                    background: #161B22 !important;
                    color: #FFFFFF !important;
                    border: 1px solid rgba(31, 182, 174, 0.4) !important;
                    border-radius: 10px !important;
                    padding: 10px 12px !important;
                    font-size: 13px !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                }
                .chat-input:focus,
                textarea.chat-input:focus,
                input.chat-input:focus {
                    background: #1C2333 !important;
                    color: #FFFFFF !important;
                    border-color: #1FB6AE !important;
                    box-shadow: 0 0 0 3px rgba(31, 182, 174, 0.25) !important;
                    outline: none !important;
                }
                .chat-input::placeholder,
                textarea.chat-input::placeholder { color: #8B949E !important; }

                /* ─── SEND BUTTON & OVERRIDE PINK ACCENTS ─── */
                .chat-input-send-button,
                button.chat-input-send-button {
                    background: #1FB6AE !important;
                    color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
                }
                .chat-input-send-button:hover,
                button.chat-input-send-button:hover,
                .chat-input-send-button:focus,
                .chat-input-send-button:active {
                    background: #19a095 !important;
                    color: #FFFFFF !important;
                    transform: scale(1.04) !important;
                    box-shadow: 0 0 10px rgba(31, 182, 174, 0.4) !important;
                }

                /* ─── OVERRIDE ALL PINK HOVER ACCENTS FROM N8N CHAT ─── */
                a:hover,
                button:hover,
                .chat-action-button:hover,
                .chat-chip:hover,
                .chat-welcome-button:hover {
                    color: #1FB6AE !important;
                    border-color: #1FB6AE !important;
                }

                /* ─── SCROLLBAR ─── */
                .chat-messages-list::-webkit-scrollbar { width: 5px !important; }
                .chat-messages-list::-webkit-scrollbar-track { background: transparent !important; }
                .chat-messages-list::-webkit-scrollbar-thumb { background: #1FB6AE !important; border-radius: 3px !important; }

                /* ─── MOBILE RESPONSIVE ─── */
                @media (max-width: 480px) {
                    .chat-window-wrapper .chat-window {
                        width: calc(100vw - 1rem) !important;
                        height: calc(100vh - 5rem) !important;
                        border-radius: 16px 16px 0 0 !important;
                    }
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
