(function () {
    'use strict';

    if (window.__ethiobizInlineAIInitialized) return;
    if (frappe.session && frappe.session.user === 'Guest') return;

    window.__ethiobizInlineAIInitialized = true;

    let settings = (typeof frappe !== 'undefined' && frappe.boot && frappe.boot.hadeeda_settings) || null;
    const TRIGGER = (settings && settings.trigger_character) || '/';
    const excludedDoctypes = ((settings && settings.excluded_doctypes) || '')
        .split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
    const excludedFields = ((settings && settings.excluded_fields) || '')
        .split(',').map(s => s.trim().toLowerCase()).filter(Boolean);

    let popup = null;
    let targetState = null;
    let generatedResponse = '';

    function getFormContext(el) {
        if (!cur_frm) return '';
        const doc = cur_frm.doc || {};
        const doctype = doc.doctype || '';
        let fieldname = '';

        const fieldEl = el.closest('[data-fieldname]');
        if (fieldEl) {
            fieldname = fieldEl.getAttribute('data-fieldname');
        }

        return JSON.stringify({
            doctype: doctype,
            docname: doc.name || '',
            field: fieldname || '',
        });
    }

    function isExcluded(el) {
        const fieldEl = el.closest('[data-fieldname]');
        if (fieldEl) {
            const fn = fieldEl.getAttribute('data-fieldname');
            if (excludedFields.includes(fn)) return true;
        }
        if (cur_frm && cur_frm.doc) {
            const dt = (cur_frm.doc.doctype || '').toLowerCase();
            if (excludedDoctypes.includes(dt)) return true;
        }
        return false;
    }

    function isEditable(el) {
        if (!el) return false;
        if (el.tagName === 'TEXTAREA') return true;
        if (el.tagName === 'INPUT' && (el.type === 'text' || el.type === 'search' || !el.type)) return true;
        if (el.isContentEditable || el.closest('.ql-editor') || el.closest('.note-editable') || el.closest('[contenteditable="true"]') || el.classList.contains('mentionable')) return true;
        return false;
    }

    function getQuillInstance(el) {
        if (!el) return null;
        // 1. Check Frappe field control dict
        const fieldEl = el.closest('[data-fieldname]');
        if (fieldEl && cur_frm && cur_frm.fields_dict) {
            const fieldname = fieldEl.getAttribute('data-fieldname');
            const ctrl = cur_frm.fields_dict[fieldname];
            if (ctrl && ctrl.quill) return ctrl.quill;
        }
        // 2. Check Quill container __quill property
        const qlContainer = el.closest('.ql-container');
        if (qlContainer && qlContainer.__quill) return qlContainer.__quill;

        // 3. Search sibling/parent elements for Quill instance
        const qlEditor = el.closest('.ql-editor');
        if (qlEditor) {
            const parent = qlEditor.parentElement;
            if (parent && parent.__quill) return parent.__quill;
            if (qlEditor.previousElementSibling && qlEditor.previousElementSibling.__quill) {
                return qlEditor.previousElementSibling.__quill;
            }
        }
        return null;
    }

    function captureTargetState(el) {
        const isInput = el.tagName === 'INPUT' || el.tagName === 'TEXTAREA';
        const quill = getQuillInstance(el);
        let quillRange = null;
        let domRange = null;

        if (quill) {
            try {
                quillRange = quill.getSelection() || { index: Math.max(0, quill.getLength() - 1), length: 0 };
            } catch (e) {
                quillRange = { index: Math.max(0, quill.getLength() - 1), length: 0 };
            }
        } else if (window.getSelection && window.getSelection().rangeCount > 0) {
            try {
                domRange = window.getSelection().getRangeAt(0).cloneRange();
            } catch (e) {
                domRange = null;
            }
        }

        return {
            el: el,
            isInput: isInput,
            start: el.selectionStart || 0,
            end: el.selectionEnd || 0,
            quill: quill,
            quillRange: quillRange,
            domRange: domRange,
        };
    }

    function removeTriggerChar(state) {
        if (!state || !state.el) return;
        const el = state.el;

        if (state.isInput) {
            const val = el.value || '';
            const idx = state.start;
            if (idx > 0 && val.charAt(idx - 1) === TRIGGER) {
                el.value = val.substring(0, idx - 1) + val.substring(idx);
                state.start = Math.max(0, idx - 1);
                state.end = state.start;
                el.selectionStart = el.selectionEnd = state.start;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
            return;
        }

        if (state.quill) {
            try {
                const range = state.quillRange;
                if (range && range.index > 0) {
                    state.quill.deleteText(range.index - 1, 1);
                    state.quillRange.index = Math.max(0, range.index - 1);
                }
            } catch (e) {}
            return;
        }

        if (state.domRange) {
            try {
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(state.domRange);
                if (document.queryCommandSupported && document.queryCommandSupported('delete')) {
                    document.execCommand('delete', false, null);
                } else if (state.domRange.startOffset > 0) {
                    const textNode = state.domRange.startContainer;
                    if (textNode.nodeType === Node.TEXT_NODE && textNode.textContent.endsWith(TRIGGER)) {
                        textNode.textContent = textNode.textContent.slice(0, -1);
                    }
                }
            } catch (e) {}
        }
    }

    function doInsert(text) {
        if (!targetState || !text) return;
        const el = targetState.el;

        // 1. Inputs & Textareas (e.g. Subject, Title, Small Text)
        if (targetState.isInput && el) {
            el.focus();
            const start = targetState.start || 0;
            const end = targetState.end || 0;
            const val = el.value || '';
            el.value = val.substring(0, start) + text + val.substring(end);
            el.selectionStart = el.selectionEnd = start + text.length;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return;
        }

        // 2. Frappe Quill Rich Text Editor (e.g. Task Description, Comments, HTML Editor)
        if (targetState.quill) {
            const q = targetState.quill;
            q.focus();
            let idx = (targetState.quillRange && typeof targetState.quillRange.index === 'number')
                ? targetState.quillRange.index
                : Math.max(0, q.getLength() - 1);

            const formattedHtml = text.replace(/\n/g, '<br>');
            try {
                q.clipboard.dangerouslyPasteHTML(idx, formattedHtml);
                q.setSelection(idx + text.length);
            } catch (e) {
                q.insertText(idx, text);
            }

            if (q.container) {
                q.container.dispatchEvent(new Event('input', { bubbles: true }));
                $(q.container).trigger('change');
            }
            return;
        }

        // 3. Generic ContentEditable / Rich Text / Timeline Comment Editors
        const container = (el && (el.closest('[contenteditable="true"]') || el.closest('.ql-editor') || el.closest('.note-editable'))) || el;
        if (container) {
            container.focus();

            if (targetState.domRange) {
                try {
                    const sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(targetState.domRange);
                } catch (e) {}
            }

            if (document.queryCommandSupported && document.queryCommandSupported('insertHTML')) {
                const formattedHtml = text.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
                document.execCommand('insertHTML', false, formattedHtml);
            } else if (document.queryCommandSupported && document.queryCommandSupported('insertText')) {
                document.execCommand('insertText', false, text);
            } else {
                const sel = window.getSelection();
                if (sel.rangeCount > 0) {
                    const range = sel.getRangeAt(0);
                    range.deleteContents();
                    const fragment = document.createDocumentFragment();
                    const lines = text.split('\n');
                    lines.forEach((line, i) => {
                        if (i > 0) fragment.appendChild(document.createElement('br'));
                        fragment.appendChild(document.createTextNode(line));
                    });
                    range.insertNode(fragment);
                } else {
                    container.innerText += text;
                }
            }
            container.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    function showPopup(el, x, y) {
        if (popup) closePopup();

        targetState = captureTargetState(el);
        removeTriggerChar(targetState);
        generatedResponse = '';

        popup = document.createElement('div');
        popup.className = 'hadeeda-inline-popup';
        popup.innerHTML = `
            <div class="hadeeda-inline-header">
                <div class="hadeeda-inline-brand">
                    <span class="hadeeda-inline-badge">H</span>
                    <span class="hadeeda-inline-title-text">HADEEDA AI Assistant</span>
                </div>
                <button class="hadeeda-inline-close" title="Close (Esc)">&times;</button>
            </div>

            <div class="hadeeda-inline-body">
                <!-- Step 1: Prompt Input View -->
                <div class="hadeeda-view-prompt">
                    <div class="hadeeda-inline-quick-options">
                        <button class="hadeeda-option-btn" data-prompt="Draft a professional response">✍️ Draft</button>
                        <button class="hadeeda-option-btn" data-prompt="Improve clarity and professional tone">⚡ Tone Fix</button>
                        <button class="hadeeda-option-btn" data-prompt="Summarize into key bullet points">📝 Summary</button>
                        <button class="hadeeda-option-btn" data-prompt="Translate text into Amharic">🌐 Amharic</button>
                    </div>
                    <div class="hadeeda-inline-input-wrapper">
                        <textarea class="hadeeda-inline-input" rows="3"
                            placeholder="Type prompt for HADEEDA AI..."></textarea>
                    </div>
                    <div class="hadeeda-prompt-actions">
                        <button class="hadeeda-inline-submit">Generate</button>
                    </div>
                </div>

                <!-- Step 2: Generating Loading View -->
                <div class="hadeeda-view-loading" style="display:none;">
                    <div class="hadeeda-loading-spinner"></div>
                    <div class="hadeeda-loading-text">⚡ HADEEDA AI is generating response...</div>
                </div>

                <!-- Step 3: Response Preview View -->
                <div class="hadeeda-view-result" style="display:none;">
                    <div class="hadeeda-result-label">Generated Response:</div>
                    <div class="hadeeda-result-preview"></div>
                    <div class="hadeeda-result-actions">
                        <button class="hadeeda-btn-insert">📥 Insert</button>
                        <button class="hadeeda-btn-copy">📋 Copy</button>
                        <button class="hadeeda-btn-retry">🔄 Edit Prompt</button>
                    </div>
                </div>

                <div class="hadeeda-inline-status" style="display:none;"></div>
            </div>
        `;

        popup.style.cssText = `
            position: fixed; z-index: 999999;
            background: #0D1117 !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(31, 182, 174, 0.4) !important;
            border-radius: 12px !important;
            box-shadow: 0 12px 36px rgba(0,0,0,0.6), 0 0 24px rgba(31, 182, 174, 0.25) !important;
            width: 440px !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif !important;
            font-size: 13px !important;
            overflow: hidden !important;
            animation: hadeeda-popup-in 0.25s ease-out !important;
        `;

        const rect = el.getBoundingClientRect();
        const popupWidth = 440;
        let left;
        if (typeof x === 'number' && typeof y === 'number') {
            left = x + 12;
        } else {
            left = rect.left;
        }
        if (left + popupWidth > window.innerWidth - 16) {
            left = window.innerWidth - popupWidth - 16;
        }
        if (left < 16) left = 16;

        let top;
        if (typeof x === 'number' && typeof y === 'number') {
            top = y + 12;
        } else {
            top = rect.bottom + 8;
        }
        if (top + 320 > window.innerHeight) {
            if (typeof y === 'number') {
                top = Math.max(16, y - 320);
            } else {
                top = Math.max(16, rect.top - 320);
            }
        }

        popup.style.left = left + 'px';
        popup.style.top = top + 'px';

        document.body.appendChild(popup);

        if (!document.getElementById('hadeeda-inline-styles')) {
            const headerStyle = document.createElement('style');
            headerStyle.id = 'hadeeda-inline-styles';
            headerStyle.textContent = `
                @keyframes hadeeda-popup-in {
                    0% { opacity: 0; transform: translateY(8px) scale(0.96); }
                    100% { opacity: 1; transform: translateY(0) scale(1); }
                }
                @keyframes hadeeda-spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .hadeeda-inline-header {
                    display: flex; justify-content: space-between; align-items: center;
                    padding: 10px 14px; background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%) !important;
                    color: #FFFFFF !important; font-weight: 700; font-size: 13px;
                }
                .hadeeda-inline-brand { display: flex; align-items: center; gap: 8px; }
                .hadeeda-inline-badge {
                    width: 22px; height: 22px; border-radius: 50%;
                    background: rgba(255,255,255,0.25); display: flex;
                    align-items: center; justify-content: center;
                    font-weight: 800; font-size: 12px; color: #fff;
                }
                .hadeeda-inline-close {
                    background: none; border: none; color: #FFFFFF !important; font-size: 20px;
                    cursor: pointer; padding: 0 4px; line-height: 1; opacity: 0.8;
                }
                .hadeeda-inline-close:hover { opacity: 1; }
                .hadeeda-inline-body { padding: 14px; background: #0D1117 !important; }
                .hadeeda-inline-quick-options {
                    display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;
                }
                .hadeeda-option-btn {
                    background: #161B22 !important; border: 1px solid rgba(255,255,255,0.15) !important;
                    color: #E6EDF3 !important; border-radius: 6px !important; padding: 5px 10px !important;
                    font-size: 12px !important; cursor: pointer; transition: all 0.2s ease;
                }
                .hadeeda-option-btn:hover {
                    background: #1FB6AE !important; color: #FFFFFF !important; border-color: #1FB6AE !important;
                }
                .hadeeda-inline-input-wrapper { margin-bottom: 10px; }
                .hadeeda-inline-input {
                    width: 100% !important; box-sizing: border-box !important; padding: 10px 12px !important;
                    border: 1px solid rgba(31, 182, 174, 0.4) !important; border-radius: 8px !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                    font-size: 13px !important; resize: vertical !important;
                    outline: none !important; background: #161B22 !important; color: #FFFFFF !important;
                }
                .hadeeda-inline-input:focus { border-color: #1FB6AE !important; box-shadow: 0 0 0 2px rgba(31, 182, 174, 0.2) !important; }
                .hadeeda-prompt-actions { display: flex; justify-content: flex-end; }
                .hadeeda-inline-submit {
                    padding: 8px 18px !important; background: #1FB6AE !important; color: #FFFFFF !important;
                    border: none !important; border-radius: 8px !important; cursor: pointer;
                    font-size: 13px !important; font-weight: 700 !important;
                    transition: background 0.2s ease;
                }
                .hadeeda-inline-submit:hover { background: #19a095 !important; }

                /* Loading View */
                .hadeeda-view-loading {
                    display: flex; flex-direction: column; align-items: center; justify-content: center;
                    padding: 24px 12px; gap: 12px; text-align: center;
                }
                .hadeeda-loading-spinner {
                    width: 28px; height: 28px; border: 3px solid rgba(31, 182, 174, 0.2);
                    border-top-color: #1FB6AE; border-radius: 50%;
                    animation: hadeeda-spin 0.8s linear infinite;
                }
                .hadeeda-loading-text { color: #1FB6AE; font-weight: 600; font-size: 13px; }

                /* Result Preview View */
                .hadeeda-result-label {
                    font-size: 12px; font-weight: 600; color: #8B949E; margin-bottom: 6px;
                }
                .hadeeda-result-preview {
                    background: #161B22 !important; color: #FFFFFF !important;
                    border: 1px solid rgba(255,255,255,0.15) !important;
                    border-radius: 8px !important; padding: 10px 12px !important;
                    max-height: 220px !important; overflow-y: auto !important;
                    white-space: pre-wrap !important; word-break: break-word !important;
                    font-size: 13px !important; line-height: 1.5 !important; margin-bottom: 12px !important;
                }
                .hadeeda-result-actions { display: flex; gap: 8px; justify-content: flex-end; }
                .hadeeda-btn-insert {
                    padding: 8px 18px !important; background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%) !important;
                    color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
                    cursor: pointer; font-size: 13px !important; font-weight: 700 !important;
                }
                .hadeeda-btn-insert:hover { background: #19a095 !important; }
                .hadeeda-btn-copy, .hadeeda-btn-retry {
                    padding: 8px 12px !important; background: #21262D !important;
                    color: #E6EDF3 !important; border: 1px solid rgba(255,255,255,0.15) !important;
                    border-radius: 8px !important; cursor: pointer; font-size: 12px !important;
                }
                .hadeeda-btn-copy:hover, .hadeeda-btn-retry:hover { background: #30363D !important; }
                .hadeeda-inline-status {
                    margin-top: 10px; padding: 8px 12px; font-size: 12px;
                    border-radius: 6px; background: rgba(31, 182, 174, 0.1);
                    border: 1px solid rgba(31, 182, 174, 0.2); color: #1FB6AE;
                }

                @media (max-width: 600px) {
                    .hadeeda-inline-popup {
                        width: calc(100vw - 24px) !important;
                        left: 12px !important;
                        top: auto !important;
                        bottom: 16px !important;
                        max-height: 80vh !important;
                    }
                }
            `;
            document.head.appendChild(headerStyle);
        }

        const input = popup.querySelector('.hadeeda-inline-input');
        const submit = popup.querySelector('.hadeeda-inline-submit');
        const close = popup.querySelector('.hadeeda-inline-close');
        const status = popup.querySelector('.hadeeda-inline-status');
        const optionBtns = popup.querySelectorAll('.hadeeda-option-btn');

        const viewPrompt = popup.querySelector('.hadeeda-view-prompt');
        const viewLoading = popup.querySelector('.hadeeda-view-loading');
        const viewResult = popup.querySelector('.hadeeda-view-result');
        const resultPreview = popup.querySelector('.hadeeda-result-preview');

        const btnInsert = popup.querySelector('.hadeeda-btn-insert');
        const btnCopy = popup.querySelector('.hadeeda-btn-copy');
        const btnRetry = popup.querySelector('.hadeeda-btn-retry');

        optionBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                input.value = this.getAttribute('data-prompt');
                doSubmit();
            });
        });

        function doSubmit() {
            const promptText = input.value.trim();
            if (!promptText) return;

            viewPrompt.style.display = 'none';
            viewResult.style.display = 'none';
            viewLoading.style.display = 'flex';
            status.style.display = 'none';

            const context = targetState ? getFormContext(targetState.el) : '';

            fetch('/api/method/bismillah_ethiobiz.api.chat_inline', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json; charset=utf-8',
                    'X-Frappe-CSRF-Token': frappe.csrf_token
                },
                body: JSON.stringify({ prompt: promptText, context: context })
            })
            .then(r => r.json())
            .then(data => {
                const reply = (data.message && data.message.reply) || '';
                generatedResponse = reply;

                viewLoading.style.display = 'none';
                if (reply) {
                    resultPreview.textContent = reply;
                    viewResult.style.display = 'block';
                } else {
                    viewPrompt.style.display = 'block';
                    status.style.display = 'block';
                    status.textContent = '⚠️ No response generated. Please try again.';
                }
            })
            .catch(err => {
                console.warn('HADEEDA inline AI error:', err);
                viewLoading.style.display = 'none';
                viewPrompt.style.display = 'block';
                status.style.display = 'block';
                status.textContent = '⚠️ Error connecting to HADEEDA AI. Please try again.';
            });
        }

        submit.addEventListener('click', doSubmit);
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                doSubmit();
            }
            if (e.key === 'Escape') {
                closePopup();
            }
        });

        btnInsert.addEventListener('click', function () {
            if (generatedResponse) {
                doInsert(generatedResponse);
            }
            closePopup();
        });

        btnCopy.addEventListener('click', function () {
            if (generatedResponse) {
                navigator.clipboard.writeText(generatedResponse);
                this.textContent = '✅ Copied!';
                setTimeout(() => { this.textContent = '📋 Copy'; }, 2000);
            }
        });

        btnRetry.addEventListener('click', function () {
            viewResult.style.display = 'none';
            viewPrompt.style.display = 'block';
            setTimeout(() => input.focus(), 80);
        });

        close.addEventListener('click', closePopup);
        setTimeout(function () { input.focus(); }, 80);
    }

    function closePopup() {
        if (popup) {
            popup.remove();
            popup = null;
        }
        targetState = null;
        generatedResponse = '';
    }

    // 1. Desktop Keyboard Trigger Listener (keyup)
    document.addEventListener('keyup', function (e) {
        if (popup && e.key === 'Escape') {
            closePopup();
            return;
        }

        if (e.key === TRIGGER || e.keyCode === 191) {
            const el = e.target;
            if (popup || !isEditable(el) || isExcluded(el)) return;
            showPopup(el);
        }
    });

    // 2. Mobile Soft Keyboard Trigger Listener (input)
    document.addEventListener('input', function (e) {
        if (popup) return;
        const el = e.target;
        if (!isEditable(el) || isExcluded(el)) return;

        let lastChar = '';
        if (e.data) {
            lastChar = e.data;
        } else if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
            const val = el.value || '';
            const pos = el.selectionStart || val.length;
            lastChar = val.charAt(pos - 1);
        } else {
            const sel = window.getSelection();
            if (sel && sel.rangeCount > 0) {
                const text = sel.anchorNode ? sel.anchorNode.textContent : '';
                lastChar = text.charAt(sel.anchorOffset - 1);
            }
        }

        if (lastChar === TRIGGER) {
            showPopup(el);
        }
    });

    // 3. Double-click trigger: open the inline AI popup anywhere, at the cursor position
    document.addEventListener('dblclick', function (e) {
        if (popup) return;
        const el = e.target;
        if (isExcluded(el)) return;
        showPopup(el, e.clientX, e.clientY);
    });

    document.addEventListener('click', function (e) {
        if (popup && !popup.contains(e.target) && targetState && e.target !== targetState.el) {
            closePopup();
        }
    });
})();
