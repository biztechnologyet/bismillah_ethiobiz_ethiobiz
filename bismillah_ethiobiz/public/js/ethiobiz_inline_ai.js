(function () {
    'use strict';

    if (window.__ethiobizInlineAIInitialized) return;
    if (frappe.session.user === 'Guest') return;

    const settings = frappe.boot.hadeeda_settings;
    if (!settings || !settings.enabled || !settings.inline_ai_enabled) return;

    window.__ethiobizInlineAIInitialized = true;

    const TRIGGER = settings.trigger_character || '/';
    const excludedDoctypes = (settings.excluded_doctypes || '')
        .split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
    const excludedFields = (settings.excluded_fields || '')
        .split(',').map(s => s.trim().toLowerCase()).filter(Boolean);

    let popup = null;
    let activeField = null;
    let savedRange = null;

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
        if (el.isContentEditable || el.closest('.ql-editor') || el.closest('.note-editable') || el.closest('[contenteditable="true"]')) return true;
        return false;
    }

    function getQuillInstance(el) {
        const fieldEl = el.closest('[data-fieldname]');
        if (fieldEl && cur_frm) {
            const fieldname = fieldEl.getAttribute('data-fieldname');
            const ctrl = cur_frm.fields_dict && cur_frm.fields_dict[fieldname];
            if (ctrl && ctrl.quill) return ctrl.quill;
        }
        const qlContainer = el.closest('.ql-container');
        if (qlContainer && qlContainer.__quill) return qlContainer.__quill;
        return null;
    }

    function insertTextAtCursor(el, text) {
        // 1. Inputs & Textareas
        if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
            const start = el.selectionStart || 0;
            const end = el.selectionEnd || 0;
            const val = el.value || '';
            el.value = val.substring(0, start) + text + val.substring(end);
            el.selectionStart = el.selectionEnd = start + text.length;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.focus();
            return;
        }

        // 2. Frappe Quill Rich Text Editor
        const quill = getQuillInstance(el);
        if (quill) {
            const range = quill.getSelection() || { index: quill.getLength() - 1, length: 0 };
            const htmlContent = text.replace(/\n/g, '<br>');
            quill.clipboard.dangerouslyPasteHTML(range.index, htmlContent);
            quill.setSelection(range.index + text.length);
            return;
        }

        // 3. Generic ContentEditable / Rich Text Editors
        const editableContainer = el.closest('[contenteditable="true"]') || el.closest('.ql-editor') || el.closest('.note-editable') || el;
        editableContainer.focus();

        if (savedRange) {
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(savedRange);
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
                lines.forEach((line, idx) => {
                    if (idx > 0) fragment.appendChild(document.createElement('br'));
                    fragment.appendChild(document.createTextNode(line));
                });
                range.insertNode(fragment);
            } else {
                editableContainer.innerText += text;
            }
        }
        editableContainer.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function removeTriggerChar(el) {
        if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
            const val = el.value || '';
            const idx = el.selectionStart || val.length;
            if (idx > 0 && val.charAt(idx - 1) === TRIGGER) {
                el.value = val.substring(0, idx - 1) + val.substring(idx);
                el.selectionStart = el.selectionEnd = idx - 1;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
            return;
        }

        const quill = getQuillInstance(el);
        if (quill) {
            const range = quill.getSelection();
            if (range && range.index > 0) {
                quill.deleteText(range.index - 1, 1);
            }
            return;
        }

        // Generic contenteditable trigger removal
        const sel = window.getSelection();
        if (sel.rangeCount > 0) {
            savedRange = sel.getRangeAt(0).cloneRange();
            if (document.queryCommandSupported && document.queryCommandSupported('delete')) {
                document.execCommand('delete', false, null);
            } else if (savedRange.startOffset > 0) {
                const textNode = savedRange.startContainer;
                if (textNode.nodeType === Node.TEXT_NODE && textNode.textContent.endsWith(TRIGGER)) {
                    textNode.textContent = textNode.textContent.slice(0, -1);
                }
            }
        }
    }

    function showPopup(el) {
        if (popup) closePopup();
        activeField = el;

        popup = document.createElement('div');
        popup.className = 'hadeeda-inline-popup';
        popup.innerHTML = `
            <div class="hadeeda-inline-header">
                <div class="hadeeda-inline-brand">
                    <span class="hadeeda-inline-badge">H</span>
                    <span>HADEEDA AI Assistant</span>
                </div>
                <button class="hadeeda-inline-close" title="Close (Esc)">&times;</button>
            </div>
            <div class="hadeeda-inline-body">
                <div class="hadeeda-inline-quick-options">
                    <button class="hadeeda-option-btn" data-prompt="Draft a professional response">✍️ Draft Response</button>
                    <button class="hadeeda-option-btn" data-prompt="Improve clarity and professional tone">⚡ Professional Tone</button>
                    <button class="hadeeda-option-btn" data-prompt="Summarize into key bullet points">📝 Bullet Summary</button>
                    <button class="hadeeda-option-btn" data-prompt="Translate text into Amharic">🌐 Translate Amharic</button>
                </div>
                <div class="hadeeda-inline-input-wrapper">
                    <textarea class="hadeeda-inline-input" rows="2"
                        placeholder="Type prompt for HADEEDA AI or pick an option above..."></textarea>
                    <button class="hadeeda-inline-submit">Generate</button>
                </div>
                <div class="hadeeda-inline-status" style="display:none;"></div>
            </div>
        `;

        popup.style.cssText = `
            position: fixed; z-index: 999999;
            background: #0D1117; color: #F0F4F8;
            border: 1px solid rgba(31, 182, 174, 0.3);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(31, 182, 174, 0.15);
            width: 420px; font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
            font-size: 13px; overflow: hidden;
            animation: hadeeda-popup-in 0.25s ease-out;
        `;

        const rect = el.getBoundingClientRect();
        const popupWidth = 420;
        let left = rect.left;
        if (left + popupWidth > window.innerWidth - 16) {
            left = window.innerWidth - popupWidth - 16;
        }
        if (left < 16) left = 16;

        let top = rect.bottom + 6;
        if (top + 260 > window.innerHeight) {
            top = Math.max(16, rect.top - 260);
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
                .hadeeda-inline-header {
                    display: flex; justify-content: space-between; align-items: center;
                    padding: 10px 14px; background: linear-gradient(135deg, #1FB6AE 0%, #147974 100%);
                    color: #fff; font-weight: 600; font-size: 13px;
                }
                .hadeeda-inline-brand { display: flex; align-items: center; gap: 8px; }
                .hadeeda-inline-badge {
                    width: 22px; height: 22px; border-radius: 50%;
                    background: rgba(255,255,255,0.25); display: flex;
                    align-items: center; justify-content: center;
                    font-weight: 800; font-size: 12px;
                }
                .hadeeda-inline-close {
                    background: none; border: none; color: #fff; font-size: 20px;
                    cursor: pointer; padding: 0 4px; line-height: 1; opacity: 0.8;
                }
                .hadeeda-inline-close:hover { opacity: 1; }
                .hadeeda-inline-body { padding: 12px; }
                .hadeeda-inline-quick-options {
                    display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px;
                }
                .hadeeda-option-btn {
                    background: #161B22; border: 1px solid rgba(255,255,255,0.1);
                    color: #E6EDF3; border-radius: 6px; padding: 4px 10px;
                    font-size: 12px; cursor: pointer; transition: all 0.2s ease;
                }
                .hadeeda-option-btn:hover {
                    background: #1FB6AE; color: #fff; border-color: #1FB6AE;
                }
                .hadeeda-inline-input-wrapper { display: flex; gap: 8px; align-items: flex-end; }
                .hadeeda-inline-input {
                    flex: 1; box-sizing: border-box; padding: 8px 10px;
                    border: 1px solid rgba(255,255,255,0.15); border-radius: 8px;
                    font-family: inherit; font-size: 13px; resize: none;
                    outline: none; background: #161B22; color: #F0F4F8;
                }
                .hadeeda-inline-input:focus { border-color: #1FB6AE; }
                .hadeeda-inline-submit {
                    padding: 8px 16px; background: #1FB6AE; color: #fff;
                    border: none; border-radius: 8px; cursor: pointer;
                    font-size: 13px; font-weight: 600; white-space: nowrap;
                    transition: background 0.2s ease;
                }
                .hadeeda-inline-submit:hover:not(:disabled) { background: #19a095; }
                .hadeeda-inline-submit:disabled { opacity: 0.4; cursor: not-allowed; }
                .hadeeda-inline-status {
                    margin-top: 8px; padding: 8px 12px; font-size: 12px;
                    border-radius: 6px; background: rgba(31, 182, 174, 0.1);
                    border: 1px solid rgba(31, 182, 174, 0.2); color: #1FB6AE;
                }
            `;
            document.head.appendChild(headerStyle);
        }

        const input = popup.querySelector('.hadeeda-inline-input');
        const submit = popup.querySelector('.hadeeda-inline-submit');
        const close = popup.querySelector('.hadeeda-inline-close');
        const status = popup.querySelector('.hadeeda-inline-status');
        const optionBtns = popup.querySelectorAll('.hadeeda-option-btn');

        optionBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                input.value = this.getAttribute('data-prompt');
                doSubmit();
            });
        });

        function doSubmit() {
            const promptText = input.value.trim();
            if (!promptText) return;

            submit.disabled = true;
            status.style.display = 'block';
            status.textContent = '⚡ HADEEDA AI is generating response...';
            input.disabled = true;

            const context = getFormContext(activeField);

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
                if (reply && activeField) {
                    insertTextAtCursor(activeField, reply);
                }
                closePopup();
            })
            .catch(err => {
                console.warn('HADEEDA inline AI error:', err);
                status.textContent = '⚠️ Error connecting to HADEEDA AI. Please try again.';
                submit.disabled = false;
                input.disabled = false;
                input.focus();
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
        close.addEventListener('click', closePopup);

        setTimeout(function () { input.focus(); }, 80);
    }

    function closePopup() {
        if (popup) {
            popup.remove();
            popup = null;
        }
        activeField = null;
        savedRange = null;
    }

    // Global listener for '/' trigger on any editable field
    document.addEventListener('keyup', function (e) {
        if (popup && e.key === 'Escape') {
            closePopup();
            return;
        }

        if (e.key !== TRIGGER) return;

        const el = e.target;
        if (popup || !isEditable(el) || isExcluded(el)) return;

        removeTriggerChar(el);
        showPopup(el);
    });

    document.addEventListener('click', function (e) {
        if (popup && !popup.contains(e.target) && e.target !== activeField) {
            closePopup();
        }
    });
})();
