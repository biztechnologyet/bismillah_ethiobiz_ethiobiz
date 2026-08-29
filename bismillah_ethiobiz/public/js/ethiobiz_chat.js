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
        const messages = document.querySelectorAll('.chat-message:not(.chat-message-transparent):not([data-hadeeda-copy]), [class*="_message_"]:not([data-hadeeda-copy])');
        messages.forEach(msg => {
            msg.setAttribute('data-hadeeda-copy', '1');
            const textEl = msg.querySelector('.chat-message-markdown, .chat-message-text, [class*="_markdown_"], p');
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

            msg.style.position = 'relative';
            msg.appendChild(btn);
        });
    }

    /** Ensure Header Title and Close Button are always beautifully visible */
    function fixHeaderTitle(titleText) {
        const headers = document.querySelectorAll('.chat-header, .chat-layout header, [class*="_header_"]');
        headers.forEach(header => {
            if (!header.querySelector('.hadeeda-custom-title-wrapper')) {
                // Look for existing title element or inject clean one
                let titleEl = header.querySelector('.chat-header-title, [class*="_title_"], h1, h2');
                if (titleEl) {
                    titleEl.style.display = 'flex';
                    titleEl.style.alignItems = 'center';
                    titleEl.style.gap = '8px';
                    titleEl.style.color = '#FFFFFF';
                    titleEl.style.fontWeight = '700';
                    titleEl.style.fontSize = '14.5px';
                    if (!titleEl.textContent.trim()) {
                        titleEl.innerHTML = `<img src="/assets/bismillah_ethiobiz/images/hadeeda_logo.png" style="width:22px;height:22px;border-radius:50%;object-fit:cover;" /> <span>${titleText || 'HADEEDA BizAi'}</span>`;
                    }
                } else {
                    const customTitle = document.createElement('div');
                    customTitle.className = 'hadeeda-custom-title-wrapper';
                    customTitle.innerHTML = `<img src="/assets/bismillah_ethiobiz/images/hadeeda_logo.png" style="width:22px;height:22px;border-radius:50%;object-fit:cover;" /> <span style="font-weight:700;font-size:14.5px;color:#FFFFFF;letter-spacing:0.2px;">${titleText || 'HADEEDA BizAi'}</span>`;
                    customTitle.style.cssText = 'display:flex;align-items:center;gap:8px;color:#FFFFFF;flex:1;';
                    header.insertBefore(customTitle, header.firstChild);
                }
            }

            // Ensure prominent Close button is always present in header
            if (!header.querySelector('.hadeeda-chat-close-btn')) {
                const closeBtn = document.createElement('button');
                closeBtn.className = 'chat-header-close hadeeda-chat-close-btn';
                closeBtn.title = 'Close Chat (Collapse)';
                closeBtn.innerHTML = '✕';
                header.appendChild(closeBtn);
            }
        });
    }

    /** Setup Drag-to-Resize for Floating & Inline Chat */
    function setupResizableWindow() {
        const chatWin = document.querySelector('.chat-window-wrapper .chat-window, .chat-window');
        if (!chatWin || chatWin.getAttribute('data-hadeeda-resizable')) return;
        chatWin.setAttribute('data-hadeeda-resizable', '1');

        // Restore saved dimensions
        const savedW = localStorage.getItem('hadeeda_chat_width');
        const savedH = localStorage.getItem('hadeeda_chat_height');
        if (savedW) chatWin.style.width = savedW;
        if (savedH) chatWin.style.height = savedH;

        // Top-Left corner handle (NW)
        const handleNW = document.createElement('div');
        handleNW.className = 'hadeeda-resize-handle hadeeda-resize-nw';
        handleNW.title = 'Drag to resize chat window';
        handleNW.innerHTML = '<svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="1.5"><path d="M1 9L9 1M1 5L5 1M1 1L1 1"/></svg>';

        // Left border handle (W)
        const handleW = document.createElement('div');
        handleW.className = 'hadeeda-resize-handle hadeeda-resize-w';

        // Top border handle (N)
        const handleN = document.createElement('div');
        handleN.className = 'hadeeda-resize-handle hadeeda-resize-n';

        chatWin.appendChild(handleNW);
        chatWin.appendChild(handleW);
        chatWin.appendChild(handleN);

        let isResizing = false;
        let resizeType = null;
        let startX, startY, startWidth, startHeight;

        function onResizeStart(e, type) {
            e.preventDefault();
            e.stopPropagation();
            isResizing = true;
            resizeType = type;
            const clientX = e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;
            const clientY = e.type.startsWith('touch') ? e.touches[0].clientY : e.clientY;
            startX = clientX;
            startY = clientY;
            startWidth = parseInt(document.defaultView.getComputedStyle(chatWin).width, 10);
            startHeight = parseInt(document.defaultView.getComputedStyle(chatWin).height, 10);
            document.body.style.userSelect = 'none';

            function onMove(ev) {
                if (!isResizing) return;
                ev.preventDefault();
                const cx = ev.type.startsWith('touch') ? ev.touches[0].clientX : ev.clientX;
                const cy = ev.type.startsWith('touch') ? ev.touches[0].clientY : ev.clientY;
                const minW = 280, maxW = Math.min(800, window.innerWidth - 10);
                const minH = 300, maxH = Math.min(900, window.innerHeight - 70);

                if (resizeType === 'nw' || resizeType === 'w') {
                    const newW = Math.min(maxW, Math.max(minW, startWidth - (cx - startX)));
                    chatWin.style.width = newW + 'px';
                }
                if (resizeType === 'nw' || resizeType === 'n') {
                    const newH = Math.min(maxH, Math.max(minH, startHeight - (cy - startY)));
                    chatWin.style.height = newH + 'px';
                }
            }

            function onUp() {
                if (isResizing) {
                    isResizing = false;
                    document.body.style.userSelect = '';
                    try {
                        localStorage.setItem('hadeeda_chat_width', chatWin.style.width);
                        localStorage.setItem('hadeeda_chat_height', chatWin.style.height);
                    } catch(ex) {}
                    window.removeEventListener('mousemove', onMove);
                    window.removeEventListener('mouseup', onUp);
                    window.removeEventListener('touchmove', onMove);
                    window.removeEventListener('touchend', onUp);
                }
            }

            window.addEventListener('mousemove', onMove, { passive: false });
            window.addEventListener('mouseup', onUp);
            window.addEventListener('touchmove', onMove, { passive: false });
            window.addEventListener('touchend', onUp);
        }

        handleNW.addEventListener('mousedown', (e) => onResizeStart(e, 'nw'));
        handleNW.addEventListener('touchstart', (e) => onResizeStart(e, 'nw'), { passive: false });
        handleW.addEventListener('mousedown', (e) => onResizeStart(e, 'w'));
        handleW.addEventListener('touchstart', (e) => onResizeStart(e, 'w'), { passive: false });
        handleN.addEventListener('mousedown', (e) => onResizeStart(e, 'n'));
        handleN.addEventListener('touchstart', (e) => onResizeStart(e, 'n'), { passive: false });
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
                    --chat--window--height: min(580px, calc(100vh - 100px)) !important;
                    --chat--window--border-radius: 20px !important;
                    --chat--message--border-radius: 12px !important;
                    --chat--toggle--size: 56px !important;
                    --chat--toggle--background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%) !important;
                    --chat--toggle--hover--background: linear-gradient(135deg, #25c9c1 0%, #19a095 100%) !important;
                    --chat--toggle--active--background: #147974 !important;
                    --chat--toggle--color: #FFFFFF !important;
                    --chat--window--right: 20px !important;
                    --chat--window--bottom: 84px !important;
                    --chat--window--z-index: 99999 !important;
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
                    0%   { opacity: 0; transform: scale(0.94) translateY(16px); }
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
                    display: inline-flex !important; align-items: center !important; justify-content: center !important;
                    animation: hadeeda-toggle-enter 0.7s cubic-bezier(0.34,1.56,0.64,1) both,
                               hadeeda-toggle-glow 3s ease-in-out 0.8s infinite !important;
                    box-shadow: 0 4px 20px rgba(31,182,174,0.35), 0 0 0 2px rgba(13,17,23,0.6) !important;
                    transition: all 0.25s ease !important;
                }

                .chat-window-wrapper .chat-window-toggle::before {
                    content: 'HADEEDA BizAi' !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                    font-weight: 700 !important; font-size: 0.85rem !important;
                    color: #FFFFFF !important; order: 1 !important;
                    pointer-events: none !important;
                    text-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
                }
                .chat-window-wrapper .chat-window-toggle::after {
                    content: '' !important; display: inline-block !important;
                    width: 36px !important; height: 36px !important; border-radius: 50% !important;
                    background-image: url('/assets/bismillah_ethiobiz/images/hadeeda_logo.png') !important;
                    background-size: cover !important; background-position: center !important;
                    background-repeat: no-repeat !important; flex-shrink: 0 !important; order: 0 !important;
                    pointer-events: none !important;
                }
                .chat-window-wrapper .chat-window-toggle:hover {
                    background: linear-gradient(135deg, #25c9c1 0%, #19a095 100%) !important;
                    transform: translateY(-2px) scale(1.04) !important;
                    box-shadow: 0 10px 30px rgba(31,182,174,0.5), 0 0 0 2px rgba(13,17,23,0.6) !important;
                    animation: none !important;
                }

                /* ─── EXPANDED / OPEN STATE (Shows '✕') ─── */
                .chat-window-wrapper.chat-open .chat-window-toggle,
                .chat-window-wrapper.chat-window-open .chat-window-toggle,
                .chat-window-toggle.chat-open,
                .chat-window-toggle.open,
                .chat-window-toggle[aria-expanded="true"] {
                    width: 52px !important; min-width: 52px !important; height: 52px !important;
                    border-radius: 50% !important; padding: 0 !important;
                    background: linear-gradient(135deg, #e11d48 0%, #9f1239 100%) !important;
                    box-shadow: 0 4px 20px rgba(225,29,72,0.55), 0 0 0 2px rgba(13,17,23,0.8) !important;
                    animation: none !important;
                    z-index: 1000001 !important;
                }
                .chat-window-wrapper.chat-open .chat-window-toggle::before,
                .chat-window-wrapper.chat-window-open .chat-window-toggle::before,
                .chat-window-toggle.chat-open::before,
                .chat-window-toggle.open::before,
                .chat-window-toggle[aria-expanded="true"]::before {
                    content: '✕' !important;
                    font-size: 1.35rem !important; font-weight: 900 !important;
                    line-height: 1 !important; color: #FFFFFF !important;
                    order: 0 !important; pointer-events: none !important;
                }
                .chat-window-wrapper.chat-open .chat-window-toggle::after,
                .chat-window-wrapper.chat-window-open .chat-window-toggle::after,
                .chat-window-toggle.chat-open::after,
                .chat-window-toggle.open::after,
                .chat-window-toggle[aria-expanded="true"]::after {
                    display: none !important;
                }

                /* ─── TRANSLUCENT GLASS CHAT WINDOW WITH VERTICAL & HORIZONTAL RESIZE CAPABILITY ─── */
                .chat-window-wrapper .chat-window,
                .chat-window {
                    display: none !important;
                    background: rgba(13, 17, 23, 0.94) !important;
                    backdrop-filter: blur(24px) saturate(180%) !important;
                    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
                    border: 1.5px solid rgba(31, 182, 174, 0.45) !important;
                    border-radius: 20px !important;
                    overflow: hidden !important;
                    box-shadow: 0 16px 48px rgba(0,0,0,0.7), 0 0 24px rgba(31,182,174,0.25) !important;
                    min-width: 300px !important;
                    max-width: min(850px, calc(100vw - 16px)) !important;
                    min-height: 320px !important;
                    max-height: min(900px, calc(100vh - 80px)) !important;
                    width: min(420px, calc(100vw - 24px));
                    height: min(580px, calc(100vh - 100px));
                    position: fixed !important;
                    bottom: 84px !important;
                    right: 20px !important;
                    z-index: 99999 !important;
                }

                .chat-window-wrapper.chat-open .chat-window,
                .chat-window-wrapper.chat-window-open .chat-window,
                .chat-window.chat-window-open,
                .chat-window[data-open="true"],
                .chat-window-wrapper[data-open="true"] .chat-window {
                    display: flex !important;
                    flex-direction: column !important;
                    animation: hadeeda-window-open 0.25s cubic-bezier(0.16, 1, 0.3, 1) both !important;
                }

                /* ─── RESIZE HANDLES (TOP & CORNER FOR VERTICAL/HORIZONTAL RESIZING) ─── */
                .hadeeda-resize-handle {
                    position: absolute !important;
                    z-index: 100000 !important;
                    touch-action: none !important;
                }
                .hadeeda-resize-nw {
                    top: 0 !important; left: 0 !important;
                    width: 32px !important; height: 32px !important;
                    cursor: nwse-resize !important;
                    display: flex !important; align-items: center !important; justify-content: center !important;
                    background: rgba(31, 182, 174, 0.35) !important;
                    border-bottom-right-radius: 12px !important;
                    transition: background 0.2s ease !important;
                }
                .hadeeda-resize-nw:hover, .hadeeda-resize-nw:active {
                    background: rgba(31, 182, 174, 0.7) !important;
                }
                .hadeeda-resize-w {
                    top: 32px !important; left: 0 !important; bottom: 0 !important;
                    width: 10px !important; cursor: ew-resize !important;
                }
                .hadeeda-resize-n {
                    top: 0 !important; left: 32px !important; right: 50px !important;
                    height: 12px !important; cursor: ns-resize !important;
                    background: rgba(31, 182, 174, 0.12) !important;
                }
                .hadeeda-resize-n:hover, .hadeeda-resize-n:active {
                    background: rgba(31, 182, 174, 0.4) !important;
                }

                .chat-layout {
                    display: flex !important;
                    flex-direction: column !important;
                    height: 100% !important;
                    max-height: 100% !important;
                    min-height: 100% !important;
                    width: 100% !important;
                    overflow: hidden !important;
                    position: relative !important;
                    background: transparent !important;
                    flex: 1 1 100% !important;
                }

                /* ─── HEADER WITH PROMINENT VISIBLE TITLE ─── */
                .chat-layout .chat-header,
                .chat-header,
                [class*="_header_"] {
                    flex: 0 0 52px !important;
                    height: 52px !important;
                    min-height: 52px !important;
                    max-height: 52px !important;
                    background: linear-gradient(135deg, rgba(31, 182, 174, 0.98) 0%, rgba(20, 121, 116, 0.98) 100%) !important;
                    color: #FFFFFF !important;
                    position: relative !important;
                    overflow: hidden !important;
                    padding: 0 16px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: space-between !important;
                    box-sizing: border-box !important;
                    border-bottom: 1px solid rgba(255,255,255,0.15) !important;
                }
                .chat-header-title,
                .chat-header-title h1,
                .chat-header h1,
                .chat-header h2,
                .chat-header .chat-title,
                [class*="_title_"],
                .hadeeda-custom-title-wrapper {
                    color: #FFFFFF !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                    font-weight: 700 !important;
                    font-size: 15px !important;
                    display: flex !important;
                    align-items: center !important;
                    gap: 8px !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    text-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
                }
                .chat-header-close,
                .hadeeda-chat-close-btn,
                .chat-header button,
                [class*="_header_"] button {
                    color: #FFFFFF !important;
                    opacity: 0.95 !important;
                    background: rgba(255,255,255,0.2) !important;
                    border: 1px solid rgba(255,255,255,0.3) !important;
                    border-radius: 50% !important;
                    width: 32px !important;
                    height: 32px !important;
                    min-width: 32px !important;
                    cursor: pointer !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    font-size: 16px !important;
                    font-weight: 800 !important;
                    z-index: 1000002 !important;
                    transition: all 0.2s ease !important;
                    margin-left: auto !important;
                }
                .chat-header-close:hover,
                .hadeeda-chat-close-btn:hover,
                .chat-header button:hover,
                [class*="_header_"] button:hover {
                    opacity: 1 !important;
                    background: rgba(225, 29, 72, 0.85) !important;
                    transform: scale(1.1) !important;
                }

                /* ─── CHAT MESSAGES BODY & FULL-CONTENT DISPLAY (NO CUTTING) ─── */
                .chat-layout .chat-body,
                .chat-body,
                .chat-messages-list,
                [class*="_body_"],
                .recycle-scroller,
                .recycle-scroller-wrapper {
                    flex: 1 1 0% !important;
                    min-height: 0 !important;
                    height: auto !important;
                    max-height: none !important;
                    overflow-y: auto !important;
                    overflow-x: hidden !important;
                    background: rgba(13, 17, 23, 0.65) !important;
                    backdrop-filter: blur(16px) !important;
                    -webkit-backdrop-filter: blur(16px) !important;
                    padding: 14px 12px !important;
                    display: flex !important;
                    flex-direction: column !important;
                    gap: 10px !important;
                    box-sizing: border-box !important;
                }


                /* Messages Containers — Full height and word wrapping */
                .chat-message,
                .chat-message-from-bot,
                .chat-message-from-user,
                [class*="_message_"] {
                    max-width: 92% !important;
                    width: fit-content !important;
                    min-width: 60px !important;
                    height: auto !important;
                    min-height: auto !important;
                    max-height: none !important;
                    overflow: visible !important;
                    word-wrap: break-word !important;
                    word-break: break-word !important;
                    overflow-wrap: break-word !important;
                    white-space: normal !important;
                    box-sizing: border-box !important;
                    padding: 10px 14px !important;
                    margin-bottom: 6px !important;
                }

                /* Message inner paragraphs and markdown — Never clip or cut */
                .chat-message-markdown,
                .chat-message-text,
                .chat-message p,
                .chat-message span,
                .chat-message div,
                [class*="_markdown_"],
                [class*="_markdown_"] p,
                [class*="_markdown_"] span,
                .n8n-markdown,
                .n8n-markdown p {
                    white-space: pre-wrap !important;
                    word-break: break-word !important;
                    overflow-wrap: break-word !important;
                    overflow: visible !important;
                    max-height: none !important;
                    height: auto !important;
                    min-height: auto !important;
                    line-height: 1.55 !important;
                    font-size: 13.5px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }

                .chat-message.chat-message-from-bot:not(.chat-message-transparent) {
                    background: rgba(22, 27, 34, 0.92) !important;
                    color: #FFFFFF !important;
                    border: 1px solid rgba(31, 182, 174, 0.3) !important;
                    border-left: 3.5px solid #1FB6AE !important;
                    border-radius: 4px 14px 14px 14px !important;
                    backdrop-filter: blur(8px) !important;
                    position: relative !important;
                    box-shadow: 0 3px 12px rgba(0,0,0,0.3) !important;
                }
                .chat-message.chat-message-from-bot a { color: #1FB6AE !important; }
                .chat-message.chat-message-from-bot a:hover { color: #25c9c1 !important; }

                .chat-message.chat-message-from-user:not(.chat-message-transparent) {
                    background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%) !important;
                    color: #FFFFFF !important;
                    border-radius: 14px 4px 14px 14px !important;
                    box-shadow: 0 3px 12px rgba(31,182,174,0.3) !important;
                    position: relative !important;
                }

                /* ─── TYPING ─── */
                .chat-message-typing-circle { background: #1FB6AE !important; }

                /* ─── P5: FULL-WIDTH FOOTER & INPUT AREA — TWO-ROW COLUMN LAYOUT ─── */
                .chat-layout .chat-footer,
                .chat-footer,
                [class*="_footer_"] {
                    background: rgba(10, 14, 18, 0.98) !important;
                    backdrop-filter: blur(20px) !important;
                    -webkit-backdrop-filter: blur(20px) !important;
                    border: none !important;
                    border-top: 1px solid rgba(31, 182, 174, 0.25) !important;
                    padding: 8px 10px !important;
                    margin: 0 !important;
                    width: 100% !important;
                    max-width: 100% !important;
                    box-sizing: border-box !important;
                    display: flex !important;
                    flex-direction: row !important;
                    align-items: stretch !important;
                    justify-content: stretch !important;
                    flex: 0 0 auto !important;
                    position: relative !important;
                    z-index: 25 !important;
                }

                /* P5: Two-row column layout — textarea on top, controls below right-aligned */
                .chat-inputs,
                .chat-input-wrapper,
                [class*="_inputContainer_"],
                [class*="chat-inputs"] {
                    background: rgba(255, 255, 255, 0.08) !important;
                    border: 1px solid rgba(255, 255, 255, 0.18) !important;
                    border-radius: 16px !important;
                    padding: 8px 10px 6px 10px !important;
                    margin: 0 !important;
                    width: 100% !important;
                    max-width: 100% !important;
                    flex: 1 1 100% !important;
                    box-sizing: border-box !important;
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: stretch !important;
                    flex-wrap: nowrap !important;
                    gap: 4px !important;
                    transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease !important;
                }

                .chat-inputs:focus-within,
                .chat-input-wrapper:focus-within,
                [class*="_inputContainer_"]:focus-within {
                    background: rgba(255, 255, 255, 0.12) !important;
                    border-color: #1FB6AE !important;
                    box-shadow: 0 0 0 2px rgba(31, 182, 174, 0.35) !important;
                }

                /* P5: Textarea input field — full width on top row */
                .chat-input,
                textarea.chat-input,
                input.chat-input,
                .chat-inputs textarea,
                .chat-inputs input,
                [class*="_inputContainer_"] textarea,
                [class*="_inputContainer_"] input {
                    flex: 1 1 auto !important;
                    width: 100% !important;
                    min-width: 0 !important;
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
                    max-height: 140px !important;
                    min-height: 22px !important;
                    margin: 0 !important;
                    box-sizing: border-box !important;
                    order: 1 !important;
                }

                .chat-input::placeholder,
                textarea.chat-input::placeholder {
                    color: rgba(255,255,255,0.5) !important;
                    font-style: italic !important;
                }

                /* P5: Controls container — below textarea, right-aligned */
                .chat-inputs-controls,
                [class*="_buttons_"],
                [class*="chat-inputs-controls"] {
                    display: flex !important;
                    flex-direction: row !important;
                    align-items: center !important;
                    justify-content: flex-end !important;
                    gap: 6px !important;
                    flex-shrink: 0 !important;
                    flex-wrap: nowrap !important;
                    margin: 0 !important;
                    padding: 2px 0 0 0 !important;
                    width: 100% !important;
                    order: 2 !important;
                }

                /* File Upload Button */
                .chat-footer button:not(.chat-input-send-button):not([class*="send"]),
                .chat-file-upload-button,
                button[class*="file-upload"] {
                    flex: 0 0 30px !important;
                    flex-shrink: 0 !important;
                    width: 30px !important;
                    height: 30px !important;
                    min-width: 30px !important;
                    min-height: 30px !important;
                    background: rgba(255,255,255,0.1) !important;
                    color: rgba(255,255,255,0.8) !important;
                    border: 1px solid rgba(255,255,255,0.15) !important;
                    border-radius: 50% !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    cursor: pointer !important;
                    transition: all 0.2s ease !important;
                }

                .chat-footer button:not(.chat-input-send-button):not([class*="send"]):hover,
                .chat-file-upload-button:hover {
                    background: rgba(31,182,174,0.25) !important;
                    color: #1FB6AE !important;
                    border-color: #1FB6AE !important;
                    transform: scale(1.08) !important;
                }

                /* Send Button */
                .chat-input-send-button,
                button.chat-input-send-button,
                button[class*="send-button"],
                button[class*="_button_"][class*="_primary_"] {
                    flex: 0 0 32px !important;
                    flex-shrink: 0 !important;
                    width: 32px !important;
                    height: 32px !important;
                    min-width: 32px !important;
                    min-height: 32px !important;
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
                .chat-message:hover .hadeeda-copy-btn,
                [class*="_message_"]:hover .hadeeda-copy-btn {
                    opacity: 1 !important;
                }
                .hadeeda-copy-btn:hover {
                    background: rgba(31, 182, 174, 0.25) !important;
                    color: #1FB6AE !important;
                }
                .hadeeda-copy-btn.hadeeda-copy-done {
                    color: #1FB6AE !important;
                    opacity: 1 !important;
                }

                /* ─── SCROLLBAR ─── */
                .chat-messages-list::-webkit-scrollbar,
                .chat-body::-webkit-scrollbar { width: 5px !important; }
                .chat-messages-list::-webkit-scrollbar-track,
                .chat-body::-webkit-scrollbar-track { background: transparent !important; }
                .chat-messages-list::-webkit-scrollbar-thumb,
                .chat-body::-webkit-scrollbar-thumb { background: #1FB6AE !important; border-radius: 3px !important; }

                /* ─── P5: MOBILE FULL-SCREEN EXPANSION & TOUCH RESIZING ─── */
                @media (max-width: 600px) {
                    .chat-window-wrapper .chat-window,
                    .chat-window {
                        max-width: calc(100vw - 12px);
                        max-height: calc(100vh - 70px);
                        border-radius: 20px !important;
                        right: 6px !important;
                        bottom: 8px !important;
                    }
                    .hadeeda-resize-nw {
                        width: 32px !important;
                        height: 32px !important;
                        background: rgba(31, 182, 174, 0.45) !important;
                    }
                    .chat-window-wrapper .chat-window-toggle { height: 50px !important; min-width: 50px !important; }
                    .chat-inputs,
                    .chat-input-wrapper,
                    [class*="chat-inputs"] {
                        border-radius: 14px !important;
                        padding: 6px 8px 4px 8px !important;
                    }
                }

                /* ─── LIGHT-MODE VARIANTS ─── */
                [data-theme='light'] .chat-window {
                    background: rgba(255,255,255,0.96) !important;
                    border: 1.5px solid rgba(2,106,110,0.3) !important;
                    box-shadow: 0 16px 48px rgba(0,0,0,0.12), 0 0 24px rgba(31,182,174,0.12) !important;
                    color: #0f172a !important;
                }
                [data-theme='light'] .chat-message.chat-message-from-bot {
                    background: rgba(240,253,250,0.95) !important;
                    color: #0f172a !important;
                    border: 1px solid rgba(2,106,110,0.2) !important;
                    border-left: 3.5px solid #008080 !important;
                }
                [data-theme='light'] .chat-inputs {
                    background: rgba(0,0,0,0.05) !important;
                    border: 1px solid rgba(0,0,0,0.15) !important;
                }
                [data-theme='light'] .chat-input,
                [data-theme='light'] .chat-inputs textarea {
                    color: #0f172a !important;
                }
                [data-theme='light'] .chat-input::placeholder {
                    color: rgba(15,23,42,0.5) !important;
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
                allowFileUploads: true,
                allowedFilesMimeTypes: config.allowed_mime_types || 'image/*,application/pdf,text/*',
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

            // Enforce uncompressed footer, textarea, and send/attach button visibility
            function enforceFooterLayout() {
                const chatWin = document.querySelector('.chat-window, [class*="chat-window"]');
                if (!chatWin) return;

                const chatBody = chatWin.querySelector('.chat-layout .chat-body, .chat-body, .chat-messages-list, [class*="_body_"], [class*="_messages_"]');
                if (chatBody) {
                    chatBody.style.setProperty('flex', '1 1 0%', 'important');
                    chatBody.style.setProperty('min-height', '0px', 'important');
                    chatBody.style.setProperty('height', 'auto', 'important');
                    chatBody.style.setProperty('max-height', 'none', 'important');
                    chatBody.style.setProperty('overflow-y', 'auto', 'important');
                }

                const footer = chatWin.querySelector('.chat-footer, footer, [class*="_footer_"], [class*="chat-footer"]');
                if (footer) {
                    footer.style.setProperty('display', 'flex', 'important');
                    footer.style.setProperty('flex-shrink', '0', 'important');
                    footer.style.setProperty('flex-grow', '0', 'important');
                    footer.style.setProperty('min-height', '60px', 'important');
                    footer.style.setProperty('height', 'auto', 'important');
                    footer.style.setProperty('width', '100%', 'important');
                    footer.style.setProperty('visibility', 'visible', 'important');
                    footer.style.setProperty('opacity', '1', 'important');
                }

                const inputs = chatWin.querySelector('.chat-inputs, .chat-input-wrapper, form, [class*="_inputContainer_"], [class*="chat-inputs"]');
                if (inputs) {
                    inputs.style.setProperty('display', 'flex', 'important');
                    inputs.style.setProperty('flex-direction', 'column', 'important');
                    inputs.style.setProperty('align-items', 'stretch', 'important');
                    inputs.style.setProperty('width', '100%', 'important');
                    inputs.style.setProperty('gap', '4px', 'important');
                    inputs.style.setProperty('min-height', '40px', 'important');
                    inputs.style.setProperty('visibility', 'visible', 'important');
                    inputs.style.setProperty('opacity', '1', 'important');
                }

                const textarea = chatWin.querySelector('.chat-input, textarea.chat-input, textarea, input[type="text"], [class*="_textarea_"]');
                if (textarea) {
                    textarea.style.setProperty('display', 'block', 'important');
                    textarea.style.setProperty('flex', '1 1 auto', 'important');
                    textarea.style.setProperty('width', 'auto', 'important');
                    textarea.style.setProperty('min-width', '50px', 'important');
                    textarea.style.setProperty('min-height', '34px', 'important');
                    textarea.style.setProperty('color', '#FFFFFF', 'important');
                    textarea.style.setProperty('-webkit-text-fill-color', '#FFFFFF', 'important');
                    textarea.style.setProperty('caret-color', '#1FB6AE', 'important');
                    textarea.style.setProperty('visibility', 'visible', 'important');
                    textarea.style.setProperty('opacity', '1', 'important');
                }

                const controls = chatWin.querySelector('.chat-inputs-controls, [class*="chat-inputs-controls"]');
                if (controls) {
                    controls.style.setProperty('display', 'flex', 'important');
                    controls.style.setProperty('flex-direction', 'row', 'important');
                    controls.style.setProperty('align-items', 'center', 'important');
                    controls.style.setProperty('justify-content', 'flex-end', 'important');
                    controls.style.setProperty('gap', '6px', 'important');
                    controls.style.setProperty('flex', '0 0 auto', 'important');
                    controls.style.setProperty('flex-shrink', '0', 'important');
                    controls.style.setProperty('width', '100%', 'important');
                    controls.style.setProperty('visibility', 'visible', 'important');
                    controls.style.setProperty('opacity', '1', 'important');
                }

                // Enforce all buttons in footer (send, attach, file upload)
                const sendBtn = chatWin.querySelector('.chat-input-send-button, button[class*="send-button"], button[type="submit"]');
                if (sendBtn) {
                    sendBtn.style.setProperty('display', 'inline-flex', 'important');
                    sendBtn.style.setProperty('align-items', 'center', 'important');
                    sendBtn.style.setProperty('justify-content', 'center', 'important');
                    sendBtn.style.setProperty('flex', '0 0 34px', 'important');
                    sendBtn.style.setProperty('flex-shrink', '0', 'important');
                    sendBtn.style.setProperty('width', '34px', 'important');
                    sendBtn.style.setProperty('height', '34px', 'important');
                    sendBtn.style.setProperty('min-width', '34px', 'important');
                    sendBtn.style.setProperty('min-height', '34px', 'important');
                    sendBtn.style.setProperty('background', 'linear-gradient(135deg, #1FB6AE 0%, #147974 100%)', 'important');
                    sendBtn.style.setProperty('color', '#FFFFFF', 'important');
                    sendBtn.style.setProperty('visibility', 'visible', 'important');
                    sendBtn.style.setProperty('opacity', '1', 'important');
                    const svg = sendBtn.querySelector('svg');
                    if (svg) {
                        svg.style.setProperty('fill', '#FFFFFF', 'important');
                        svg.style.setProperty('stroke', '#FFFFFF', 'important');
                        svg.style.setProperty('color', '#FFFFFF', 'important');
                        svg.style.setProperty('width', '18px', 'important');
                        svg.style.setProperty('height', '18px', 'important');
                        svg.style.setProperty('display', 'block', 'important');
                    }
                }

                const fileBtn = chatWin.querySelector('.chat-input-file-button, button[class*="file-button"], [data-test-id="chat-attach-file-button"]');
                if (fileBtn) {
                    fileBtn.style.setProperty('display', 'inline-flex', 'important');
                    fileBtn.style.setProperty('align-items', 'center', 'important');
                    fileBtn.style.setProperty('justify-content', 'center', 'important');
                    fileBtn.style.setProperty('flex', '0 0 34px', 'important');
                    fileBtn.style.setProperty('flex-shrink', '0', 'important');
                    fileBtn.style.setProperty('width', '34px', 'important');
                    fileBtn.style.setProperty('height', '34px', 'important');
                    fileBtn.style.setProperty('min-width', '34px', 'important');
                    fileBtn.style.setProperty('min-height', '34px', 'important');
                    fileBtn.style.setProperty('background', 'rgba(31, 182, 174, 0.18)', 'important');
                    fileBtn.style.setProperty('border', '1px solid rgba(31, 182, 174, 0.45)', 'important');
                    fileBtn.style.setProperty('color', '#1FB6AE', 'important');
                    fileBtn.style.setProperty('visibility', 'visible', 'important');
                    fileBtn.style.setProperty('opacity', '1', 'important');
                    const svg = fileBtn.querySelector('svg');
                    if (svg) {
                        svg.style.setProperty('stroke', '#1FB6AE', 'important');
                        svg.style.setProperty('color', '#1FB6AE', 'important');
                        svg.style.setProperty('width', '18px', 'important');
                        svg.style.setProperty('height', '18px', 'important');
                        svg.style.setProperty('display', 'block', 'important');
                    }
                }

            }



            // Continuously enforce copy buttons, resizability, header title, and footer layout
            function setupObservers() {
                injectCopyButtons();
                fixHeaderTitle(config.widget_title);
                setupResizableWindow();
                enforceFooterLayout();

                const chatBody = document.querySelector('.chat-messages-list') || document.querySelector('.chat-body');
                if (chatBody) {
                    const observer = new MutationObserver(() => {
                        injectCopyButtons();
                        fixHeaderTitle(config.widget_title);
                        enforceFooterLayout();
                    });
                    observer.observe(chatBody, { childList: true, subtree: true });
                }
            }

            // Watch for chat window DOM insertion
            const bodyObserver = new MutationObserver(() => {
                setupObservers();
            });
            bodyObserver.observe(document.body, { childList: true, subtree: true });
            setTimeout(setupObservers, 300);
            setTimeout(setupObservers, 800);
            setTimeout(setupObservers, 1500);

            // Toggle handler
            function setupToggleHandler() {
                const wrapper = document.querySelector('.chat-window-wrapper');
                const toggle = document.querySelector('.chat-window-toggle');
                if (!wrapper || !toggle) return false;

                wrapper.classList.remove('chat-open', 'chat-window-open');
                toggle.classList.remove('chat-open', 'open');
                toggle.setAttribute('aria-expanded', 'false');

                function setOpen(isOpen) {
                    const chatWin = wrapper.querySelector('.chat-window');
                    if (isOpen) {
                        wrapper.classList.add('chat-open', 'chat-window-open');
                        toggle.classList.add('chat-open', 'open');
                        toggle.setAttribute('aria-expanded', 'true');
                        if (chatWin) {
                            chatWin.style.setProperty('display', 'flex', 'important');
                            setupResizableWindow();
                            fixHeaderTitle(config.widget_title);
                            enforceFooterLayout();
                            setTimeout(enforceFooterLayout, 100);
                            setTimeout(enforceFooterLayout, 300);
                        }
                    } else {
                        wrapper.classList.remove('chat-open', 'chat-window-open');
                        toggle.classList.remove('chat-open', 'open');
                        toggle.setAttribute('aria-expanded', 'false');
                        if (chatWin) chatWin.style.setProperty('display', 'none', 'important');
                    }
                }


                toggle.addEventListener('click', function (e) {
                    const isCurrentlyOpen = wrapper.classList.contains('chat-open');
                    setOpen(!isCurrentlyOpen);
                });

                function handleCloseClick(e) {
                    if (e.target.closest('.chat-header-close') || e.target.closest('.hadeeda-chat-close-btn') || e.target.closest('[class*="header-close"]') || e.target.closest('.chat-close-button')) {
                        e.preventDefault();
                        e.stopPropagation();
                        setOpen(false);
                    }
                }

                document.addEventListener('click', handleCloseClick);
                document.addEventListener('touchend', handleCloseClick);

                setOpen(false);
                return true;
            }

            if (!setupToggleHandler()) {
                const initObs = new MutationObserver(() => {
                    if (setupToggleHandler()) initObs.disconnect();
                });
                initObs.observe(document.body, { childList: true, subtree: true });
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
