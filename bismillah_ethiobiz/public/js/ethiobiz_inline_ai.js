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

    function getFormContext(el) {
        if (!cur_frm) return '';
        const doc = cur_frm.doc || {};
        const doctype = doc.doctype || '';
        const field = Object.keys(doc).find(k => {
            const f = cur_frm.fields_dict && cur_frm.fields_dict[k];
            return f && f.df && (f.df.fieldname === el.getAttribute('data-fieldname') ||
                   el.closest(`[data-fieldname="${f.df.fieldname}"]`));
        });
        return JSON.stringify({
            doctype: doctype,
            docname: doc.name || '',
            field: field || '',
        });
    }

    function isExcluded(el) {
        const fieldEl = el.closest('[data-fieldname]');
        if (!fieldEl) return false;
        const fieldname = fieldEl.getAttribute('data-fieldname');
        if (excludedFields.includes(fieldname)) return true;
        if (cur_frm && cur_frm.doc) {
            const dt = (cur_frm.doc.doctype || '').toLowerCase();
            if (excludedDoctypes.includes(dt)) return true;
        }
        return false;
    }

    function isEditable(el) {
        if (el.tagName === 'TEXTAREA') return true;
        if (el.tagName === 'INPUT' && el.type === 'text') return true;
        if (el.isContentEditable) return true;
        return false;
    }

    function insertTextAtCursor(el, text) {
        if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
            const start = el.selectionStart;
            const end = el.selectionEnd;
            el.value = el.value.substring(0, start) + text + el.value.substring(end);
            el.selectionStart = el.selectionEnd = start + text.length;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.focus();
        } else if (el.isContentEditable) {
            const sel = window.getSelection();
            if (sel.rangeCount > 0) {
                const range = sel.getRangeAt(0);
                range.deleteContents();
                range.insertNode(document.createTextNode(text));
                range.collapse(false);
                sel.removeAllRanges();
                sel.addRange(range);
            }
        }
    }

    function removeTriggerChar(el) {
        if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
            const val = el.value;
            const idx = el.selectionStart;
            for (let i = idx - 1; i >= Math.max(0, idx - TRIGGER.length); i--) {
                if (val.substring(i, i + TRIGGER.length) === TRIGGER) {
                    el.value = val.substring(0, i) + val.substring(i + TRIGGER.length);
                    el.selectionStart = el.selectionEnd = i;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    break;
                }
            }
        }
    }

    function showPopup(el) {
        if (popup) return;
        activeField = el;

        popup = document.createElement('div');
        popup.className = 'hadeeda-inline-popup';
        popup.innerHTML = `
            <div class="hadeeda-inline-header">
                <span class="hadeeda-inline-title">Ask HADEEDA</span>
                <button class="hadeeda-inline-close">&times;</button>
            </div>
            <div class="hadeeda-inline-body">
                <textarea class="hadeeda-inline-input" rows="2"
                    placeholder="Ask AI to write or edit text..."></textarea>
                <button class="hadeeda-inline-submit" disabled>Generate</button>
            </div>
            <div class="hadeeda-inline-status" style="display:none;"></div>
        `;

        popup.style.cssText = `
            position: fixed; z-index: 10000;
            background: var(--bg, #fff); color: var(--text-color, #333);
            border: 1px solid var(--border-color, #d1d8dd);
            border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            width: 380px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px; overflow: hidden;
        `;

        const rect = el.getBoundingClientRect();
        const popupWidth = 380;
        let left = Math.min(rect.left, window.innerWidth - popupWidth - 16);
        if (left < 8) left = 8;
        popup.style.left = left + 'px';
        popup.style.top = (rect.bottom + 4) + 'px';

        document.body.appendChild(popup);

        const headerStyle = document.createElement('style');
        headerStyle.textContent = `
            .hadeeda-inline-header {
                display: flex; justify-content: space-between; align-items: center;
                padding: 8px 12px; background: #1FB6AE; color: #fff;
                font-weight: 600; font-size: 13px;
            }
            .hadeeda-inline-close {
                background: none; border: none; color: #fff; font-size: 18px;
                cursor: pointer; padding: 0 4px; line-height: 1;
            }
            .hadeeda-inline-body { padding: 10px; }
            .hadeeda-inline-input {
                width: 100%; box-sizing: border-box; padding: 8px 10px;
                border: 1px solid #d1d8dd; border-radius: 6px;
                font-family: inherit; font-size: 13px; resize: none;
                outline: none; background: #fff; color: #333;
            }
            .hadeeda-inline-input:focus { border-color: #1FB6AE; }
            .hadeeda-inline-submit {
                margin-top: 8px; padding: 6px 16px; float: right;
                background: #1FB6AE; color: #fff; border: none; border-radius: 6px;
                cursor: pointer; font-size: 13px; font-weight: 500;
            }
            .hadeeda-inline-submit:disabled { opacity: 0.5; cursor: default; }
            .hadeeda-inline-submit:hover:not(:disabled) { background: #19a095; }
            .hadeeda-inline-status {
                padding: 8px 12px; font-size: 13px; border-top: 1px solid #eee;
                background: #f9f9f9; color: #666;
            }
        `;
        document.head.appendChild(headerStyle);

        const input = popup.querySelector('.hadeeda-inline-input');
        const submit = popup.querySelector('.hadeeda-inline-submit');
        const close = popup.querySelector('.hadeeda-inline-close');
        const status = popup.querySelector('.hadeeda-inline-status');

        input.addEventListener('input', function () {
            submit.disabled = !this.value.trim();
        });

        function doSubmit() {
            const text = input.value.trim();
            if (!text) return;
            submit.disabled = true;
            status.style.display = 'block';
            status.textContent = 'HADEEDA is thinking...';
            input.disabled = true;

            const context = getFormContext(activeField);

            fetch('/api/method/bismillah_ethiobiz.api.chat_inline', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json; charset=utf-8', 'X-Frappe-CSRF-Token': frappe.csrf_token },
                body: JSON.stringify({ prompt: text, context: context })
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
                status.textContent = '⚠️ Error connecting to HADEEDA. Please try again.';
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

        setTimeout(function () { input.focus(); }, 100);
    }

    function closePopup() {
        if (popup) {
            popup.remove();
            popup = null;
        }
        activeField = null;
    }

    document.addEventListener('keydown', function (e) {
        if (popup && e.key === 'Escape') {
            closePopup();
            return;
        }

        const el = e.target;
        if (popup || !isEditable(el) || isExcluded(el)) return;

        if (e.key === TRIGGER.slice(-1)) {
            const val = el.tagName === 'TEXTAREA' || el.tagName === 'INPUT'
                ? el.value : el.textContent || '';
            const selStart = el.selectionStart !== undefined ? el.selectionStart : val.length;

            if (selStart >= TRIGGER.length) {
                const preceding = val.substring(selStart - TRIGGER.length, selStart);
                if (preceding === TRIGGER || preceding === TRIGGER.slice(-1)) {
                    e.preventDefault();
                    removeTriggerChar(el);
                    showPopup(el);
                }
            }
        }
    });

    document.addEventListener('click', function (e) {
        if (popup && !popup.contains(e.target) && e.target !== activeField) {
            closePopup();
        }
    });
})();
