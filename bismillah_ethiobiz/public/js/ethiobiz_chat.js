(function () {
    'use strict';

    if (window.__ethiobizChatInitialized) return;

    window.__ethiobizChatInitialized = true;

    /**
     * Parse NDJSON text (from n8n Formatter node) into clean Markdown text.
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
            } catch (e) {}
        }
        return result || null;
    }

    function extractOutput(text) {
        if (!text) return '';
        if (text.includes('CSRFTokenError') || text.includes('exc_type') || text.includes('Invalid Request')) {
            return 'As-salamu alaykum! I am ready to assist you. Please send your message again, InshaAllah!';
        }
        const ndjsonResult = parseNDJSON(text);
        if (ndjsonResult) return ndjsonResult;
        try {
            const data = JSON.parse(text);
            if (data.message && typeof data.message === 'object' && data.message.output) return data.message.output;
            if (data.message && typeof data.message === 'string') return data.message;
            if (data.output) return data.output;
            if (Array.isArray(data) && data.length > 0) {
                const item = data[0];
                if (item.output) return item.output;
                if (item.json && item.json.output) return item.json.output;
                if (item.message) return item.message;
            }
            return text;
        } catch (e) { return text; }
    }

    /** Inject copy buttons into chat messages */
    function injectCopyButtons() {
        const messages = document.querySelectorAll('.chat-message:not(.chat-message-transparent):not([data-hadeeda-copy])');
        messages.forEach(msg => {
            msg.setAttribute('data-hadeeda-copy', '1');
            const textEl = msg.querySelector('.chat-message-markdown, .chat-message-text, p');
            if (!textEl) return;

            const btn = document.createElement('button');
            btn.className = 'hadeeda-copy-btn';
            btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
            btn.title = 'Copy';
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                const text = textEl.innerText || textEl.textContent || '';
                navigator.clipboard.writeText(text.trim()).then(() => {
                    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
                    btn.classList.add('hadeeda-copy-done');
                    setTimeout(() => {
                        btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
                        btn.classList.remove('hadeeda-copy-done');
                    }, 2000);
                });
            });

            // Wrap message content for relative positioning
            msg.style.position = 'relative';
            msg.appendChild(btn);
        });
    }

    async function initChat() {
        try {
            const resp = await fetch('/api/method/bismillah_ethiobiz.api.get_chat_config');
            const json = await resp.json();
            const config = json.message || json;

            if (!config.enabled) return;

            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdn.jsdelivr.net/npm/@n8n/chat@1.30.2/dist/style.css';
            document.head.appendChild(link);

            const { createChat } = await import('https://cdn.jsdelivr.net/npm/@n8n/chat@1.30.2/dist/chat.bundle.es.js');

            const proxyUrl = window.location.origin + '/api/method/bismillah_ethiobiz.api.chat_webhook_proxy';

            const originalFetch = window.fetch;
            window.fetch = async function (url, options) {
                const urlStr = typeof url === 'string' ? url : (url && url.url ? url.url : '');
                if (urlStr.includes('chat_webhook_proxy')) {
                    try {
                        const opts = options || {};
                        opts.credentials = 'same-origin';
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
                            status: 200, statusText: 'OK',
                            headers: { 'Content-Type': 'application/json' }
                        });
                    } catch (fetchErr) {
                        console.warn('HADEEDA proxy fetch error:', fetchErr);
                        return new Response(JSON.stringify({ output: 'As-salamu alaykum! Please try again, InshaAllah!' }), {
                            status: 200, headers: { 'Content-Type': 'application/json' }
                        });
                    }
                }
                return originalFetch.call(window, url, options);
            };

            const style = document.createElement('style');
            style.textContent = `
                :root {
                    --chat--color--primary: ${config.widget_primary_color || '#1FB6AE'} !important;
                    --chat--color--primary-shade-50: #19a095 !important;
                    --chat--color--primary--shade-100: #147974 !important;
                    --chat--color--secondary: #1FB6AE !important;
                    --chat--color-secondary-shade-50: #19a095 !important;
                    --chat--color-white: #FFFFFF !important;
                    --chat--color-light: rgba(22, 27, 34, 0.85) !important;
                    --chat--color-light-shade-50: rgba(28, 35, 51, 0.85) !important;
                    --chat--color-light-shade-100: rgba(45, 51, 59, 0.85) !important;
                    --chat--color-medium: #30363D !important;
                    --chat--color-dark: rgba(13, 17, 23, 0.75) !important;
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
                    content: '' !important; display: inline-block !important;
                    width: 36px !important; height: 36px !important; border-radius: 50% !important;
                    background-image: url('/assets/bismillah_ethiobiz/images/hadeeda_logo.png') !important;
                    background-size: cover !important; background-position: center !important;
                    background-repeat: no-repeat !important; flex-shrink: 0 !important; order: 0 !important;
                }
                .chat-window-wrapper .chat-window-toggle:hover {
                    background: linear-gradient(135deg, #25c9c1 0%, #19a095 100%) !important;
                    transform: translateY(-2px) scale(1.04) !important;
                    box-shadow: 0 10px 30px rgba(31,182,174,0.5), 0 0 0 2px rgba(13,17,23,0.6) !important;
                    animation: none !important;
                }

                /* ─── TRANSLUCENT GLASS CHAT WINDOW ─── */
                .chat-window-wrapper .chat-window,
                .chat-layout {
                    background: rgba(13, 17, 23, 0.75) !important;
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
                    background: linear-gradient(135deg, rgba(31, 182, 174, 0.95) 0%, rgba(20, 121, 116, 0.95) 100%) !important;
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

                /* ─── MESSAGES BODY TRANSLUCENT ─── */
                .chat-layout .chat-body,
                .chat-body,
                .chat-messages-list {
                    background: rgba(13, 17, 23, 0.65) !important;
                    backdrop-filter: blur(16px) !important;
                    -webkit-backdrop-filter: blur(16px) !important;
                }

                .chat-message.chat-message-from-bot:not(.chat-message-transparent) {
                    background: rgba(22, 27, 34, 0.88) !important; color: #FFFFFF !important;
                    border: 1px solid rgba(31, 182, 174, 0.25) !important;
                    border-left: 3px solid #1FB6AE !important;
                    border-radius: 4px 12px 12px 12px !important;
                    line-height: 1.5 !important; font-size: 13px !important;
                    backdrop-filter: blur(8px) !important;
                    position: relative !important;
                }
                .chat-message.chat-message-from-bot a { color: #1FB6AE !important; }
                .chat-message.chat-message-from-bot a:hover { color: #25c9c1 !important; }

                .chat-message.chat-message-from-user:not(.chat-message-transparent) {
                    background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%) !important;
                    color: #FFFFFF !important; border-radius: 12px 4px 12px 12px !important;
                    line-height: 1.5 !important; font-size: 13px !important;
                    box-shadow: 0 2px 10px rgba(31,182,174,0.25) !important;
                    position: relative !important;
                }

                /* ─── TYPING ─── */
                .chat-message-typing-circle { background: #1FB6AE !important; }

                                /* ─── HADEEDA CHAT FOOTER & INPUT AREA ─── */
                .chat-footer,
                [class*="chat-footer"] {
                    background: rgba(13, 17, 23, 0.95) !important;
                    backdrop-filter: blur(16px) !important;
                    -webkit-backdrop-filter: blur(16px) !important;
                    border: none !important;
                    border-top: 1px solid rgba(255,255,255,0.08) !important;
                    padding: 8px 10px !important;
                    margin: 0 !important;
                    width: 100% !important;
                    box-sizing: border-box !important;
                    overflow: hidden !important;
                    display: flex !important;
                    align-items: center !important;
                }

                /* Container pill wrapping file upload, text input, send button */
                .chat-inputs,
                .chat-input-wrapper,
                [class*="chat-inputs"],
                [class*="chat-input-wrapper"] {
                    background: rgba(255, 255, 255, 0.07) !important;
                    border: 1px solid rgba(255, 255, 255, 0.15) !important;
                    border-radius: 22px !important;
                    padding: 4px 6px 4px 10px !important;
                    margin: 0 !important;
                    width: 100% !important;
                    max-width: 100% !important;
                    box-sizing: border-box !important;
                    display: flex !important;
                    align-items: center !important;
                    gap: 6px !important;
                    overflow: hidden !important;
                    transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease !important;
                }

                .chat-inputs:focus-within,
                .chat-input-wrapper:focus-within,
                [class*="chat-inputs"]:focus-within,
                [class*="chat-input-wrapper"]:focus-within {
                    background: rgba(255, 255, 255, 0.10) !important;
                    border-color: #1FB6AE !important;
                    box-shadow: 0 0 0 2px rgba(31, 182, 174, 0.25) !important;
                }

                /* Textarea input field */
                .chat-input,
                textarea.chat-input,
                input.chat-input,
                .chat-inputs textarea,
                .chat-inputs input,
                [class*="chat-input"]:not(button):not([class*="send"]):not([class*="upload"]) {
                    flex: 1 1 0% !important;
                    width: 0 !important;
                    min-width: 0 !important;
                    max-width: 100% !important;
                    background: transparent !important;
                    color: #FFFFFF !important;
                    border: none !important;
                    outline: none !important;
                    padding: 6px 4px !important;
                    font-size: 13.5px !important;
                    line-height: 1.4 !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                    box-shadow: none !important;
                    resize: none !important;
                    overflow-y: auto !important;
                    max-height: 80px !important;
                    margin: 0 !important;
                }

                .chat-input:focus,
                textarea.chat-input:focus,
                input.chat-input:focus {
                    background: transparent !important;
                    color: #FFFFFF !important;
                    border: none !important;
                    outline: none !important;
                    box-shadow: none !important;
                }

                .chat-input::placeholder,
                textarea.chat-input::placeholder,
                [class*="chat-input"]::placeholder {
                    color: rgba(255,255,255,0.45) !important;
                    font-style: italic !important;
                }

                /* File Upload / Attachment Button */
                .chat-footer button:not(.chat-input-send-button),
                .chat-file-upload-button,
                button[class*="file-upload"] {
                    flex: 0 0 32px !important;
                    flex-shrink: 0 !important;
                    width: 32px !important;
                    height: 32px !important;
                    min-width: 32px !important;
                    background: transparent !important;
                    color: rgba(255,255,255,0.6) !important;
                    border: none !important;
                    border-radius: 50% !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    cursor: pointer !important;
                    transition: all 0.2s ease !important;
                }

                .chat-footer button:not(.chat-input-send-button):hover,
                .chat-file-upload-button:hover,
                button[class*="file-upload"]:hover {
                    background: rgba(31,182,174,0.2) !important;
                    color: #1FB6AE !important;
                    transform: scale(1.1) !important;
                }

                .chat-footer button:not(.chat-input-send-button) svg,
                .chat-file-upload-button svg,
                button[class*="file-upload"] svg {
                    width: 17px !important;
                    height: 17px !important;
                }

                /* Send Button */
                .chat-input-send-button,
                button.chat-input-send-button,
                button[class*="send-button"] {
                    flex: 0 0 34px !important;
                    flex-shrink: 0 !important;
                    width: 34px !important;
                    height: 34px !important;
                    min-width: 34px !important;
                    background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%) !important;
                    color: #FFFFFF !important;
                    border: none !important;
                    border-radius: 50% !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    cursor: pointer !important;
                    box-shadow: 0 2px 8px rgba(31,182,174,0.4) !important;
                    transition: all 0.2s ease !important;
                }

                .chat-input-send-button:hover,
                button.chat-input-send-button:hover {
                    background: linear-gradient(135deg, #25c9c1 0%, #19a095 100%) !important;
                    color: #FFFFFF !important;
                    transform: scale(1.08) !important;
                    box-shadow: 0 3px 12px rgba(31,182,174,0.6) !important;
                }

                .chat-input-send-button:disabled,
                button.chat-input-send-button:disabled {
                    background: rgba(255,255,255,0.15) !important;
                    color: rgba(255,255,255,0.3) !important;
                    box-shadow: none !important;
                    cursor: not-allowed !important;
                    transform: none !important;
                }

                .chat-input-send-button svg,
                button.chat-input-send-button svg,
                button[class*="send-button"] svg {
                    width: 16px !important;
                    height: 16px !important;
                }

                /* ─── COPY BUTTON ON EACH MESSAGE ─── */
                .hadeeda-copy-btn {
                    position: absolute !important;
                    bottom: 6px !important; right: 6px !important;
                    background: rgba(255,255,255,0.08) !important;
                    color: rgba(255,255,255,0.45) !important;
                    border: none !important; border-radius: 6px !important;
                    width: 26px !important; height: 26px !important;
                    display: flex !important; align-items: center !important; justify-content: center !important;
                    cursor: pointer !important; padding: 0 !important;
                    opacity: 0 !important; transition: all 0.2s ease !important;
                    z-index: 5 !important;
                }
                .chat-message:hover .hadeeda-copy-btn {
                    opacity: 1 !important;
                }
                .hadeeda-copy-btn:hover {
                    background: rgba(31, 182, 174, 0.25) !important;
                    color: #1FB6AE !important;
                    border: none !important;
                }
                .hadeeda-copy-btn.hadeeda-copy-done {
                    color: #1FB6AE !important;
                    opacity: 1 !important;
                }

                /* ─── OVERRIDE PINK ACCENTS ─── */
                a:hover,
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

                /* ─── MOBILE ─── */
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
                    user_id: config.username,
                    full_name: config.full_name,
                    email: config.email,
                    company: config.company,
                    department: config.department || '',
                    designation: config.designation || '',
                    language: config.language || config.default_language || 'en',
                    source: 'widget',
                    api_key: config.api_key,
                    api_secret: config.api_secret,
                    industry: config.industry || '',
                    religion: config.religion || '',
                    user_behaviour: config.user_behaviour || '',
                    company_industry: config.company_industry || '',
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

            // Robust copy button injection: observe the whole chat wrapper
            // so we catch messages whether the window is already open or opened later
            function setupCopyObserver() {
                injectCopyButtons();
                const chatBody = document.querySelector('.chat-messages-list') || document.querySelector('.chat-body');
                if (chatBody) {
                    const observer = new MutationObserver(() => { injectCopyButtons(); });
                    observer.observe(chatBody, { childList: true, subtree: true });
                    return true;
                }
                return false;
            }
            // Try immediately, retry on toggle click and via interval
            if (!setupCopyObserver()) {
                // Watch for the chat window to appear in DOM
                const wrapperObserver = new MutationObserver(() => {
                    if (setupCopyObserver()) wrapperObserver.disconnect();
                });
                wrapperObserver.observe(document.body, { childList: true, subtree: true });
                // Also retry on toggle click
                document.addEventListener('click', function onToggle(e) {
                    if (e.target.closest('.chat-window-toggle') || e.target.closest('[class*="toggle"]')) {
                        setTimeout(() => {
                            if (setupCopyObserver()) document.removeEventListener('click', onToggle);
                        }, 500);
                    }
                });
            }

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
