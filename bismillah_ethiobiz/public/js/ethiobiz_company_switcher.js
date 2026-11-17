/* EthioBiz master-identity company switcher (TASK-2026-00972)
 *
 * One login, many tenants.  The switcher is injected into the Desk navbar or
 * the website navbar; if neither exists it falls back to a compact fixed pill.
 * All switches are re-validated server-side by company_api.switch_company.
 */
(function () {
    'use strict';

    if (window.__ethioCompanySwitcherLoaded) return;
    window.__ethioCompanySwitcherLoaded = true;

    var API = {
        myCompanies: 'bismillah_ethiobiz.company_api.get_my_companies',
        switchCompany: 'bismillah_ethiobiz.company_api.switch_company',
        addCompany: 'bismillah_ethiobiz.company_api.add_company',
        industries: 'bismillah_ethiobiz.home_api.get_dobiz_industries'
    };

    var state = {
        companies: [],
        active: '',
        loading: false,
        injected: false,
        menuOpen: false
    };

    function isGuest() {
        try {
            return !window.frappe || !frappe.session || !frappe.session.user ||
                frappe.session.user === 'Guest';
        } catch (e) {
            return true;
        }
    }

    function csrfToken() {
        try {
            return (window.frappe && (frappe.csrf_token || (frappe.session && frappe.session.csrf_token)))
                || window.csrf_token
                || (document.querySelector('meta[name="csrf-token"]') || {}).content
                || '';
        } catch (e) {
            return '';
        }
    }

    function call(method, args, type) {
        if (window.frappe && typeof frappe.call === 'function') {
            return new Promise(function (resolve, reject) {
                frappe.call({
                    method: method,
                    args: args || {},
                    type: type || 'POST',
                    callback: function (r) { resolve(r && r.message); },
                    error: function (err) { reject(err); }
                });
            });
        }
        var headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' };
        var token = csrfToken();
        if (token) headers['X-Frappe-CSRF-Token'] = token;
        var options = {
            method: type || 'POST',
            credentials: 'same-origin',
            headers: headers
        };
        var url = '/api/method/' + method;
        if ((type || 'POST') === 'GET') {
            var qs = Object.keys(args || {}).map(function (k) {
                return encodeURIComponent(k) + '=' + encodeURIComponent(args[k]);
            }).join('&');
            if (qs) url += '?' + qs;
        } else {
            options.body = JSON.stringify(args || {});
        }
        return fetch(url, options).then(function (r) {
            return r.json().then(function (data) {
                if (!r.ok) {
                    var msg = (data && (data.exception || data._server_messages)) || 'Request failed';
                    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
                }
                return data && data.message;
            });
        });
    }

    function escapeHtml(value) {
        return String(value == null ? '' : value).replace(/[&<>"']/g, function (ch) {
            return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch];
        });
    }

    function companyInitial(name) {
        var text = String(name || '').trim();
        return text ? text.charAt(0).toUpperCase() : '•';
    }

    function findNavHost() {
        var selectors = [
            '.navbar .navbar-nav',
            '.navbar .navbar-collapse .navbar-nav',
            '.navbar-nav',
            'header .navbar-nav',
            '.navbar .container-fluid'
        ];
        for (var i = 0; i < selectors.length; i++) {
            var el = document.querySelector(selectors[i]);
            if (el) return el;
        }
        return null;
    }

    function buildSwitcher() {
        var wrap = document.createElement('div');
        wrap.className = 'ethio-company-switcher';
        wrap.innerHTML =
            '<button type="button" class="ecs-trigger" aria-haspopup="menu" aria-expanded="false" title="Switch company">' +
                '<span class="ecs-mark" aria-hidden="true">🏢</span>' +
                '<span class="ecs-label"><small>Company</small><strong data-ecs-active>Loading…</strong></span>' +
                '<span class="ecs-caret" aria-hidden="true">▾</span>' +
            '</button>' +
            '<div class="ecs-menu" role="menu" hidden>' +
                '<div class="ecs-menu-head"><span>Your companies</span><span data-ecs-count></span></div>' +
                '<div class="ecs-list" data-ecs-list></div>' +
                '<div class="ecs-sep"></div>' +
                '<button type="button" class="ecs-add" data-ecs-add>＋ Add another company</button>' +
                '<div class="ecs-note">One master login. Switch anytime.</div>' +
            '</div>';
        return wrap;
    }

    function inject() {
        if (state.injected) return;
        if (document.querySelector('.ethio-company-switcher')) {
            state.injected = true;
            return;
        }
        var host = findNavHost();
        var wrap = buildSwitcher();
        if (host) {
            if (host.tagName === 'UL') {
                var li = document.createElement('li');
                li.className = 'nav-item ethio-company-switcher-host';
                li.appendChild(wrap);
                host.appendChild(li);
            } else {
                host.appendChild(wrap);
            }
        } else {
            wrap.classList.add('ecs-fixed');
            document.body.appendChild(wrap);
        }
        state.injected = true;
        bindSwitcher(wrap);
    }

    function render() {
        var wrap = document.querySelector('.ethio-company-switcher');
        if (!wrap) return;
        var activeEl = wrap.querySelector('[data-ecs-active]');
        var listEl = wrap.querySelector('[data-ecs-list]');
        var countEl = wrap.querySelector('[data-ecs-count]');
        if (activeEl) activeEl.textContent = state.active || 'Choose company';
        if (countEl) countEl.textContent = state.companies.length ? (state.companies.length + ' active') : '';
        if (!listEl) return;
        if (!state.companies.length) {
            listEl.innerHTML = '<div class="ecs-empty">No company access found. Contact support.</div>';
            return;
        }
        listEl.innerHTML = state.companies.map(function (company) {
            var isActive = company.name === state.active;
            return '<button type="button" role="menuitemradio" aria-checked="' + (isActive ? 'true' : 'false') +
                '" class="ecs-item' + (isActive ? ' is-active' : '') + '" data-ecs-company="' + escapeHtml(company.name) + '">' +
                '<span class="ecs-avatar">' + escapeHtml(companyInitial(company.name)) + '</span>' +
                '<span class="ecs-item-copy"><strong>' + escapeHtml(company.name) + '</strong>' +
                '<small>' + (company.is_default ? 'Default · ' : '') + 'Active access</small></span>' +
                '<span class="ecs-check" aria-hidden="true">' + (isActive ? '✓' : '') + '</span>' +
            '</button>';
        }).join('');
    }

    function loadCompanies() {
        if (state.loading) return Promise.resolve();
        state.loading = true;
        return call(API.myCompanies, {}, 'GET').then(function (data) {
            var context = data || {};
            state.companies = Array.isArray(context.companies) ? context.companies : [];
            state.active = context.active_company || context.default_company || (state.companies[0] && state.companies[0].name) || '';
            state.loading = false;
            render();
        }).catch(function (err) {
            state.loading = false;
            console.warn('[EthioBiz] Company switcher load failed', err);
            var listEl = document.querySelector('.ethio-company-switcher [data-ecs-list]');
            if (listEl) listEl.innerHTML = '<div class="ecs-empty">Could not load companies. Try refreshing.</div>';
        });
    }

    function setOpen(open) {
        var wrap = document.querySelector('.ethio-company-switcher');
        if (!wrap) return;
        var menu = wrap.querySelector('.ecs-menu');
        var trigger = wrap.querySelector('.ecs-trigger');
        state.menuOpen = !!open;
        if (menu) menu.hidden = !open;
        if (trigger) trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
        wrap.classList.toggle('is-open', !!open);
        if (open) {
            var first = wrap.querySelector('.ecs-item');
            if (first) { try { first.focus(); } catch (e) {} }
        }
    }

    function bindSwitcher(wrap) {
        var trigger = wrap.querySelector('.ecs-trigger');
        if (trigger) {
            trigger.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                setOpen(!state.menuOpen);
            });
        }
        wrap.addEventListener('click', function (e) {
            var item = e.target.closest && e.target.closest('[data-ecs-company]');
            if (item) {
                e.preventDefault();
                switchTo(item.getAttribute('data-ecs-company'));
                return;
            }
            var add = e.target.closest && e.target.closest('[data-ecs-add]');
            if (add) {
                e.preventDefault();
                setOpen(false);
                openAddCompany();
            }
        });
        document.addEventListener('click', function (e) {
            if (!state.menuOpen) return;
            if (wrap.contains(e.target)) return;
            setOpen(false);
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && state.menuOpen) setOpen(false);
        });
    }

    function switchTo(company) {
        if (!company || company === state.active) {
            setOpen(false);
            return;
        }
        var wrap = document.querySelector('.ethio-company-switcher');
        if (wrap) wrap.classList.add('is-busy');
        call(API.switchCompany, { company: company }, 'POST').then(function () {
            window.location.reload();
        }).catch(function (err) {
            if (wrap) wrap.classList.remove('is-busy');
            notify('Could not switch company', err);
        });
    }

    function notify(title, err) {
        var message = err && err.message ? err.message : String(err || '');
        if (window.frappe && typeof frappe.msgprint === 'function') {
            frappe.msgprint({ title: title, indicator: 'red', message: escapeHtml(message) });
        } else {
            window.alert(title + '\n\n' + message);
        }
    }

    function ensureModal() {
        var existing = document.getElementById('ethio-company-add-modal');
        if (existing) return existing;
        var modal = document.createElement('div');
        modal.id = 'ethio-company-add-modal';
        modal.className = 'ecs-modal';
        modal.hidden = true;
        modal.innerHTML =
            '<div class="ecs-modal-backdrop" data-ecs-modal-close></div>' +
            '<div class="ecs-modal-card" role="dialog" aria-modal="true" aria-labelledby="ecs-modal-title">' +
                '<div class="ecs-modal-head">' +
                    '<div><h3 id="ecs-modal-title">Add another company</h3>' +
                    '<p>Use the same master login. No new password is created.</p></div>' +
                    '<button type="button" class="ecs-modal-x" data-ecs-modal-close aria-label="Close">✕</button>' +
                '</div>' +
                '<form data-ecs-add-form>' +
                    '<label class="ecs-field"><span>Company name</span>' +
                        '<input type="text" name="company_name" maxlength="120" required placeholder="e.g. Addis Coffee Trading PLC">' +
                    '</label>' +
                    '<label class="ecs-field"><span>Industry</span>' +
                        '<select name="industry" required data-ecs-industries><option value="">Loading industries…</option></select>' +
                    '</label>' +
                    '<label class="ecs-check-row"><input type="checkbox" name="make_default" value="1"> ' +
                        '<span>Make this the default company after creating it</span></label>' +
                    '<div class="ecs-form-error" data-ecs-form-error hidden></div>' +
                    '<div class="ecs-modal-actions">' +
                        '<button type="button" class="ecs-btn-ghost" data-ecs-modal-close>Cancel</button>' +
                        '<button type="submit" class="ecs-btn-primary" data-ecs-submit>Create company</button>' +
                    '</div>' +
                '</form>' +
            '</div>';
        document.body.appendChild(modal);
        modal.addEventListener('click', function (e) {
            if (e.target.closest('[data-ecs-modal-close]')) closeModal();
        });
        var form = modal.querySelector('[data-ecs-add-form]');
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            submitAddCompany(form);
        });
        return modal;
    }

    function loadIndustryOptions(select) {
        if (!select || select.getAttribute('data-loaded') === '1') return;
        call(API.industries, {}, 'GET').then(function (data) {
            var rows = (data && data.industries) || [];
            if (!rows.length) {
                select.innerHTML = '<option value="">No industries enabled</option>';
                return;
            }
            select.innerHTML = '<option value="">Choose an industry</option>' + rows.map(function (row) {
                return '<option value="' + escapeHtml(row.canonical_label || row.label) + '">' +
                    escapeHtml(row.icon ? row.icon + ' ' + row.label : row.label) + '</option>';
            }).join('');
            select.setAttribute('data-loaded', '1');
        }).catch(function () {
            select.innerHTML = '<option value="">Could not load industries</option>';
        });
    }

    function openAddCompany() {
        var modal = ensureModal();
        var form = modal.querySelector('[data-ecs-add-form]');
        var select = modal.querySelector('[data-ecs-industries]');
        var error = modal.querySelector('[data-ecs-form-error]');
        if (form) form.reset();
        if (error) { error.hidden = true; error.textContent = ''; }
        modal.hidden = false;
        document.body.classList.add('ecs-modal-open');
        loadIndustryOptions(select);
        setTimeout(function () {
            var input = modal.querySelector('input[name="company_name"]');
            if (input) input.focus();
        }, 30);
    }

    function closeModal() {
        var modal = document.getElementById('ethio-company-add-modal');
        if (modal) modal.hidden = true;
        document.body.classList.remove('ecs-modal-open');
    }

    function submitAddCompany(form) {
        var modal = document.getElementById('ethio-company-add-modal');
        var error = modal.querySelector('[data-ecs-form-error]');
        var submit = modal.querySelector('[data-ecs-submit]');
        var data = new FormData(form);
        var payload = {
            company_name: (data.get('company_name') || '').trim(),
            industry: data.get('industry') || '',
            make_default: data.get('make_default') ? 1 : 0
        };
        if (!payload.company_name || !payload.industry) {
            if (error) { error.hidden = false; error.textContent = 'Enter a company name and choose an industry.'; }
            return;
        }
        if (submit) { submit.disabled = true; submit.textContent = 'Creating…'; }
        call(API.addCompany, payload, 'POST').then(function (result) {
            var company = (result && result.company) || payload.company_name;
            return call(API.switchCompany, { company: company }, 'POST').then(function () {
                window.location.reload();
            });
        }).catch(function (err) {
            if (submit) { submit.disabled = false; submit.textContent = 'Create company'; }
            if (error) {
                error.hidden = false;
                error.textContent = (err && err.message) ? err.message : 'Could not create the company.';
            }
        });
    }

    function ensureStyles() {
        if (document.getElementById('ethio-company-switcher-css')) return;
        var style = document.createElement('style');
        style.id = 'ethio-company-switcher-css';
        style.textContent = [
            '.ethio-company-switcher{position:relative;display:inline-flex;align-items:center;margin:0 6px;font-family:inherit;z-index:1025}',
            '.ethio-company-switcher.ecs-fixed{position:fixed;top:10px;right:14px;margin:0;z-index:1035}',
            '.ecs-trigger{display:inline-flex;align-items:center;gap:8px;min-height:36px;max-width:250px;padding:5px 10px;border:1px solid rgba(94,234,212,.24);border-radius:12px;background:rgba(2,13,16,.55);color:#ecfffb;cursor:pointer;font:inherit;transition:.18s ease}',
            '.ecs-trigger:hover,.ethio-company-switcher.is-open .ecs-trigger{border-color:rgba(94,234,212,.6);background:rgba(20,184,166,.16)}',
            '.ecs-mark{width:24px;height:24px;display:grid;place-items:center;border-radius:8px;background:linear-gradient(135deg,#14b8a6,#0f766e);font-size:13px;flex:none}',
            '.ecs-label{display:grid;min-width:0;line-height:1.15;text-align:left}',
            '.ecs-label small{font-size:8px;text-transform:uppercase;letter-spacing:.12em;color:#9fd8cf;font-weight:800}',
            '.ecs-label strong{font-size:11px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:160px}',
            '.ecs-caret{font-size:10px;color:#9fd8cf}',
            '.ecs-menu{position:absolute;top:calc(100% + 8px);right:0;width:300px;max-width:calc(100vw - 20px);padding:9px;border:1px solid rgba(94,234,212,.22);border-radius:16px;background:#04191d;box-shadow:0 24px 70px rgba(0,0,0,.5);z-index:1200}',
            '.ecs-menu[hidden]{display:none!important}',
            '.ecs-menu-head{display:flex;justify-content:space-between;gap:8px;padding:4px 7px 8px;font-size:9px;text-transform:uppercase;letter-spacing:.12em;color:#9fd8cf;font-weight:900}',
            '.ecs-list{display:grid;gap:3px;max-height:290px;overflow:auto}',
            '.ecs-item{display:flex;align-items:center;gap:9px;width:100%;padding:8px;border:1px solid transparent;border-radius:11px;background:transparent;color:#ecfffb;text-align:left;cursor:pointer;font:inherit}',
            '.ecs-item:hover,.ecs-item:focus-visible{background:rgba(94,234,212,.08);border-color:rgba(94,234,212,.2);outline:none}',
            '.ecs-item.is-active{background:rgba(20,184,166,.14);border-color:rgba(94,234,212,.34)}',
            '.ecs-avatar{width:28px;height:28px;display:grid;place-items:center;border-radius:9px;background:rgba(94,234,212,.12);color:#5eead4;font-weight:900;font-size:12px;flex:none}',
            '.ecs-item-copy{display:grid;min-width:0;flex:1;line-height:1.2}',
            '.ecs-item-copy strong{font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
            '.ecs-item-copy small{font-size:9px;color:#9fd8cf;margin-top:2px}',
            '.ecs-check{color:#5eead4;font-weight:900;font-size:12px}',
            '.ecs-sep{height:1px;margin:8px 4px;background:rgba(94,234,212,.14)}',
            '.ecs-add{width:100%;padding:9px;border:1px dashed rgba(94,234,212,.35);border-radius:11px;background:rgba(94,234,212,.05);color:#5eead4;font:inherit;font-size:11px;font-weight:800;cursor:pointer}',
            '.ecs-add:hover{background:rgba(94,234,212,.11)}',
            '.ecs-note{padding:7px 7px 2px;font-size:9px;color:#9fd8cf;text-align:center}',
            '.ecs-empty{padding:14px 9px;font-size:11px;color:#9fd8cf;text-align:center}',
            '.ethio-company-switcher.is-busy{opacity:.55;pointer-events:none}',
            '.ecs-modal[hidden]{display:none!important}',
            '.ecs-modal{position:fixed;inset:0;z-index:2000;display:grid;place-items:center;padding:16px}',
            '.ecs-modal-backdrop{position:absolute;inset:0;background:rgba(0,8,10,.72);backdrop-filter:blur(4px)}',
            '.ecs-modal-card{position:relative;width:min(460px,100%);max-height:92vh;overflow:auto;padding:20px;border:1px solid rgba(94,234,212,.24);border-radius:20px;background:#04191d;color:#ecfffb;box-shadow:0 30px 90px rgba(0,0,0,.6)}',
            '.ecs-modal-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:14px}',
            '.ecs-modal-head h3{margin:0;font-size:18px;letter-spacing:-.02em}',
            '.ecs-modal-head p{margin:5px 0 0;font-size:11px;color:#9fd8cf;line-height:1.5}',
            '.ecs-modal-x{width:30px;height:30px;border:1px solid rgba(94,234,212,.2);border-radius:9px;background:transparent;color:#ecfffb;cursor:pointer;flex:none}',
            '.ecs-field{display:grid;gap:6px;margin-bottom:12px;font-size:10px;font-weight:800;color:#ecfffb}',
            '.ecs-field input,.ecs-field select{width:100%;min-height:40px;padding:9px 11px;border:1px solid rgba(94,234,212,.22);border-radius:11px;background:rgba(2,13,16,.6);color:#ecfffb;font:inherit;font-size:12px;color-scheme:dark}',
            '.ecs-field input:focus,.ecs-field select:focus{outline:2px solid rgba(94,234,212,.45);outline-offset:1px}',
            '.ecs-check-row{display:flex;gap:8px;align-items:flex-start;font-size:10px;color:#9fd8cf;line-height:1.45;margin:4px 0 10px}',
            '.ecs-form-error{padding:8px 10px;margin-bottom:10px;border-radius:9px;background:rgba(251,113,133,.12);border:1px solid rgba(251,113,133,.35);color:#fecdd3;font-size:10px;line-height:1.45}',
            '.ecs-form-error[hidden]{display:none!important}',
            '.ecs-modal-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:6px}',
            '.ecs-btn-ghost,.ecs-btn-primary{min-height:38px;padding:8px 14px;border-radius:11px;font:inherit;font-size:11px;font-weight:800;cursor:pointer}',
            '.ecs-btn-ghost{border:1px solid rgba(94,234,212,.2);background:transparent;color:#ecfffb}',
            '.ecs-btn-primary{border:1px solid rgba(94,234,212,.5);background:linear-gradient(135deg,#14b8a6,#0f766e);color:#fff}',
            '.ecs-btn-primary:disabled{opacity:.55;cursor:not-allowed}',
            'body.ecs-modal-open{overflow:hidden}',
            '@media(max-width:600px){.ethio-company-switcher{margin:0}.ecs-label strong{max-width:110px}.ecs-menu{position:fixed;top:auto;bottom:12px;left:10px;right:10px;width:auto;max-height:70vh;overflow:auto}.ethio-company-switcher.ecs-fixed{top:auto;bottom:70px;right:10px}}'
        ].join('\n');
        document.head.appendChild(style);
    }

    function boot() {
        if (isGuest()) return;
        ensureStyles();
        inject();
        loadCompanies();
        // Frappe's navbar can be re-rendered after route changes; re-inject if
        // our switcher disappeared, but never duplicate it.
        var observer = new MutationObserver(function () {
            if (!document.querySelector('.ethio-company-switcher')) {
                state.injected = false;
                inject();
                render();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
    // Desk emits this after the session/navbar is ready.
    document.addEventListener('frappe:ready', function () {
        if (!state.injected) boot();
    });
})();
