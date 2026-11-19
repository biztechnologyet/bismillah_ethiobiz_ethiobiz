/* EthioBiz master-identity company switcher (TASK-2026-00972, upgraded)
 *
 * One login, many tenants. The selector is injected into the Desk navbar only
 * for users with more than one active company. Selecting a company re-validates
 * access server-side, updates the user's active company default, and pushes the
 * new context into every visible Desk surface (new forms, list/report filters,
 * link-field defaults) without losing unsaved work. Website pages reload so all
 * server-rendered contexts pick up the new company.
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

    function isDesk() {
        try {
            var path = window.location.pathname || '';
            if (path.indexOf('/app') === 0 || path.indexOf('/desk') === 0) return true;
            if (document.body && document.body.classList && document.body.classList.contains('desk')) return true;
        } catch (e) {}
        return false;
    }

    function patchEmployeeLookups() {
        try {
            if (!window.frappe || !frappe.db || typeof frappe.db.get_value !== 'function') return;
            if (frappe.db.__ethioCompanyAwareEmployeeLookup) return;
            var original = frappe.db.get_value;
            frappe.db.get_value = function () {
                var args = Array.prototype.slice.call(arguments);
                var doctype = args[0];
                var filters = args[1];
                if (doctype === 'Employee' && filters && typeof filters === 'object' &&
                    !Array.isArray(filters) && filters.user_id === frappe.session.user &&
                    !filters.company) {
                    var company = window.ethiobizActiveCompany ||
                        (frappe.defaults && frappe.defaults.get_user_default &&
                            frappe.defaults.get_user_default('company'));
                    if (company) {
                        var scoped = {};
                        Object.keys(filters).forEach(function (k) { scoped[k] = filters[k]; });
                        scoped.company = company;
                        args[1] = scoped;
                    }
                }
                return original.apply(frappe.db, args);
            };
            frappe.db.__ethioCompanyAwareEmployeeLookup = true;
        } catch (e) {}
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

    function companyAbbr(company) {
        company = company || {};
        var abbr = String(company.abbr || '').trim();
        if (abbr) return abbr.slice(0, 4).toUpperCase();
        var name = String(company.name || '').trim();
        if (!name) return '•';
        var parts = name.split(/\s+/).filter(function (w) { return w && !/^(and|of|the|plc|ltd|llc|co)$/i.test(w); });
        if (!parts.length) parts = [name];
        return parts.slice(0, 3).map(function (w) { return w.charAt(0).toUpperCase(); }).join('');
    }

    function contextFrom(data) {
        if (!data) return {};
        return (data.context && typeof data.context === 'object') ? data.context : data;
    }

    function companiesFrom(data) {
        var ctx = contextFrom(data);
        return Array.isArray(ctx.companies) ? ctx.companies : [];
    }

    function activeFrom(data) {
        var ctx = contextFrom(data);
        return ctx.active_company || ctx.default_company ||
            (companiesFrom(data)[0] && companiesFrom(data)[0].name) || '';
    }

    function seedFromBoot() {
        try {
            var boot = (window.frappe && frappe.boot) || {};
            var companies = boot.ethiobiz_companies;
            if (Array.isArray(companies) && companies.length) {
                state.companies = companies;
                state.active = boot.ethiobiz_active_company ||
                    (companies[0] && companies[0].name) || '';
                return true;
            }
        } catch (e) {}
        return false;
    }

    function findNavHost() {
        var selectors = [
            '#navbar .navbar-nav',
            '.navbar .navbar-nav',
            'header .navbar-nav',
            '#navbar',
            '.navbar',
            '.navbar-nav',
            'header'
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
        wrap.setAttribute('aria-label', 'Current company');
        wrap.innerHTML =
            '<button type="button" class="ecs-trigger" aria-haspopup="menu" aria-expanded="false" title="Switch company">' +
                '<span class="ecs-mark" data-ecs-mark aria-hidden="true">••</span>' +
                '<span class="ecs-label"><small>Current company</small><strong data-ecs-active>Loading…</strong></span>' +
                '<span class="ecs-caret" aria-hidden="true">▾</span>' +
            '</button>' +
            '<div class="ecs-menu" role="menu" hidden>' +
                '<div class="ecs-menu-head"><span>Your companies</span><span data-ecs-count></span></div>' +
                '<div class="ecs-list" data-ecs-list></div>' +
                '<div class="ecs-sep"></div>' +
                '<button type="button" class="ecs-add" data-ecs-add>＋ Add another company</button>' +
                '<div class="ecs-note">One master login. Everything follows the selected company.</div>' +
            '</div>';
        return wrap;
    }

    function inject() {
        if (state.injected) return;
        var existing = document.querySelector('.ethio-company-switcher');
        if (existing) {
            state.injected = true;
            render();
            return;
        }
        var host = findNavHost();
        var wrap = buildSwitcher();
        if (host) {
            if (host.tagName === 'UL' || host.classList.contains('navbar-nav')) {
                var li = document.createElement('li');
                li.className = 'nav-item ethio-company-switcher-host';
                li.appendChild(wrap);
                host.appendChild(li);
            } else {
                wrap.classList.add('ecs-in-navbar');
                host.appendChild(wrap);
            }
        } else {
            wrap.classList.add('ecs-fixed');
            document.body.appendChild(wrap);
        }
        state.injected = true;
        bindSwitcher(wrap);
        render();
    }

    function render() {
        var wrap = document.querySelector('.ethio-company-switcher');
        if (!wrap) return;

        // Requirement: only users with access to more than one company see this.
        if (state.companies.length < 2) {
            wrap.hidden = true;
            setOpen(false);
            return;
        }
        wrap.hidden = false;

        var activeEl = wrap.querySelector('[data-ecs-active]');
        var markEl = wrap.querySelector('[data-ecs-mark]');
        var listEl = wrap.querySelector('[data-ecs-list]');
        var countEl = wrap.querySelector('[data-ecs-count]');

        var activeCompany = state.companies.filter(function (c) { return c.name === state.active; })[0] || state.companies[0];
        if (activeEl) activeEl.textContent = activeCompany ? activeCompany.name : (state.active || 'Choose company');
        if (markEl) markEl.textContent = companyAbbr(activeCompany || { name: state.active });
        if (countEl) countEl.textContent = state.companies.length + ' active';

        if (!listEl) return;
        listEl.innerHTML = state.companies.map(function (company) {
            var isActive = company.name === (activeCompany && activeCompany.name);
            return '<button type="button" role="menuitemradio" aria-checked="' + (isActive ? 'true' : 'false') +
                '" class="ecs-item' + (isActive ? ' is-active' : '') + '" data-ecs-company="' + escapeHtml(company.name) + '">' +
                '<span class="ecs-avatar">' + escapeHtml(companyAbbr(company)) + '</span>' +
                '<span class="ecs-item-copy"><strong>' + escapeHtml(company.name) + '</strong>' +
                '<small>' + (company.is_default ? 'Default · ' : '') +
                escapeHtml(company.currency || 'Active access') + '</small></span>' +
                '<span class="ecs-check" aria-hidden="true">' + (isActive ? '✓' : '') + '</span>' +
            '</button>';
        }).join('');
    }

    function loadCompanies() {
        if (state.loading) return Promise.resolve();
        state.loading = true;
        var seeded = seedFromBoot();
        if (seeded) render();
        return call(API.myCompanies, {}, 'GET').then(function (data) {
            state.companies = companiesFrom(data);
            state.active = activeFrom(data);
            state.loading = false;
            render();
        }).catch(function (err) {
            state.loading = false;
            console.warn('[EthioBiz] Company switcher load failed', err);
            if (!seeded) {
                var listEl = document.querySelector('.ethio-company-switcher [data-ecs-list]');
                if (listEl) listEl.innerHTML = '<div class="ecs-empty">Could not load companies. Try refreshing.</div>';
            }
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

    function hasCompanyField(doctype) {
        if (!doctype || !window.frappe) return false;
        try {
            var meta = frappe.get_meta && frappe.get_meta(doctype);
            if (meta && meta.fields) {
                return meta.fields.some(function (f) { return f.fieldname === 'company'; });
            }
        } catch (e) {}
        return false;
    }

    function applyToOpenForms(company) {
        var forms = [];
        try { if (window.cur_frm) forms.push(window.cur_frm); } catch (e) {}
        forms.forEach(function (frm) {
            try {
                var doc = frm.doc || {};
                var hasField = hasCompanyField(doc.doctype) || !!(frm.fields_dict && frm.fields_dict.company);
                if (!hasField) return;
                var isNew = (typeof frm.is_new === 'function') ? frm.is_new() : !doc.name;
                if (!isNew) return;
                if (typeof frm.set_value === 'function') frm.set_value('company', company);
                else doc.company = company;
                if (typeof frm.refresh_fields === 'function') frm.refresh_fields();
                else if (typeof frm.refresh_field === 'function') frm.refresh_field('company');
            } catch (e) {}
        });
    }

    function applyToCurrentLists(company) {
        var views = [];
        try { if (window.cur_list) views.push(window.cur_list); } catch (e) {}
        try { if (window.cur_report) views.push(window.cur_report); } catch (e) {}
        views.forEach(function (view) {
            try {
                if (!view.doctype || !hasCompanyField(view.doctype) || !view.filter_area) return;
                try { view.filter_area.remove('company'); } catch (e) {}
                try {
                    view.filter_area.add(view.doctype, 'company', '=', company);
                } catch (err) {
                    try { view.filter_area.add([[view.doctype, 'company', '=', company]]); } catch (e2) {}
                }
            } catch (e) {}
        });
    }

    function applyClientCompanyContext(company, previous) {
        try {
            if (window.frappe) {
                if (!frappe.boot) frappe.boot = {};
                if (!frappe.boot.user) frappe.boot.user = {};
                if (!frappe.boot.user.defaults) frappe.boot.user.defaults = {};
                frappe.boot.user.defaults.company = company;
                if (typeof frappe.defaults === 'object' && typeof frappe.defaults.set_user_default_local === 'function') {
                    frappe.defaults.set_user_default_local('company', company);
                }
                if (typeof frappe.defaults === 'object' && typeof frappe.defaults.update_user_permissions === 'function') {
                    frappe.defaults.update_user_permissions();
                }
                frappe.boot.ethiobiz_active_company = company;
                if (frappe.session) frappe.session.company = company;
            }
        } catch (e) {}

        try { localStorage.setItem('ethiobiz_active_company', company); } catch (e) {}
        try { document.documentElement.setAttribute('data-ethiobiz-company', company); } catch (e) {}
        window.ethiobizActiveCompany = company;

        applyToOpenForms(company);
        applyToCurrentLists(company);

        var detail = { company: company, previous: previous || '' };
        try {
            window.dispatchEvent(new CustomEvent('ethiobiz:company-changed', { detail: detail }));
        } catch (e) {
            try { window.dispatchEvent(new Event('ethiobiz:company-changed')); } catch (e2) {}
        }
        try {
            if (window.jQuery && jQuery(document).trigger) {
                jQuery(document).trigger('ethiobiz:company-changed', [detail]);
            }
        } catch (e) {}
    }

    function refreshVisibleViews() {
        setTimeout(function () {
            try { if (window.cur_list && typeof cur_list.refresh === 'function') cur_list.refresh(); } catch (e) {}
            try { if (window.cur_report && typeof cur_report.refresh === 'function') cur_report.refresh(); } catch (e) {}
            try { if (window.cur_frm && typeof cur_frm.refresh_fields === 'function') cur_frm.refresh_fields(); } catch (e) {}
        }, 80);
    }

    function successNotice(company) {
        try {
            if (window.frappe && typeof frappe.show_alert === 'function') {
                frappe.show_alert({ message: 'Now viewing ' + company, indicator: 'green' }, 4);
            } else if (window.frappe && typeof frappe.msgprint === 'function') {
                frappe.msgprint({ title: 'Company switched', indicator: 'green', message: 'Now viewing ' + escapeHtml(company) });
            }
        } catch (e) {}
    }

    function switchTo(company) {
        if (!company || company === state.active) {
            setOpen(false);
            return;
        }
        var wrap = document.querySelector('.ethio-company-switcher');
        if (wrap) wrap.classList.add('is-busy');
        call(API.switchCompany, { company: company }, 'POST').then(function (data) {
            var previous = state.active;
            var ctx = contextFrom(data);
            if (companiesFrom(data).length) state.companies = companiesFrom(data);
            state.active = ctx.active_company || company;

            applyClientCompanyContext(state.active, previous);
            render();
            setOpen(false);
            if (wrap) wrap.classList.remove('is-busy');

            if (isDesk()) {
                refreshVisibleViews();
                successNotice(state.active);
            } else {
                window.location.reload();
            }
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
            closeModal();
            if (submit) { submit.disabled = false; submit.textContent = 'Create company'; }
            switchTo(company);
        }).catch(function (err) {
            if (submit) { submit.disabled = false; submit.textContent = 'Create company'; }
            if (error) {
                error.hidden = false;
                error.textContent = (err && err.message) ? err.message : 'Could not create the company.';
            }
        });
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

    function ensureStyles() {
        if (document.getElementById('ethio-company-switcher-css')) return;
        var style = document.createElement('style');
        style.id = 'ethio-company-switcher-css';
        style.textContent = [
            '.ethio-company-switcher{position:relative;display:inline-flex;align-items:center;margin:0 6px;font-family:inherit;z-index:1030}',
            '.ethio-company-switcher[hidden]{display:none!important}',
            '.ethio-company-switcher.ecs-in-navbar{margin-left:auto;margin-right:10px}',
            '.ethio-company-switcher.ecs-fixed{position:fixed;top:10px;right:14px;margin:0;z-index:1035}',
            '.ecs-trigger{display:inline-flex;align-items:center;gap:8px;min-height:36px;max-width:260px;padding:5px 10px;border:1px solid rgba(94,234,212,.28);border-radius:12px;background:rgba(2,13,16,.62);color:#ecfffb;cursor:pointer;font:inherit;transition:.18s ease;box-shadow:0 4px 16px rgba(0,0,0,.18)}',
            '.ecs-trigger:hover,.ethio-company-switcher.is-open .ecs-trigger{border-color:rgba(94,234,212,.65);background:rgba(20,184,166,.18)}',
            '.ecs-mark{width:30px;height:30px;display:grid;place-items:center;border-radius:9px;background:linear-gradient(135deg,#14b8a6,#0f766e);color:#fff;font-size:10px;font-weight:900;letter-spacing:.04em;flex:none}',
            '.ecs-label{display:grid;min-width:0;line-height:1.15;text-align:left}',
            '.ecs-label small{font-size:8px;text-transform:uppercase;letter-spacing:.11em;color:#9fd8cf;font-weight:800}',
            '.ecs-label strong{font-size:11px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:170px}',
            '.ecs-caret{font-size:10px;color:#9fd8cf}',
            '.ecs-menu{position:absolute;top:calc(100% + 8px);right:0;width:310px;max-width:calc(100vw - 20px);padding:9px;border:1px solid rgba(94,234,212,.25);border-radius:16px;background:#04191d;box-shadow:0 24px 70px rgba(0,0,0,.5);z-index:1200;color:#ecfffb}',
            '.ecs-menu[hidden]{display:none!important}',
            '.ecs-menu-head{display:flex;justify-content:space-between;gap:8px;padding:4px 7px 8px;font-size:9px;text-transform:uppercase;letter-spacing:.12em;color:#9fd8cf;font-weight:900}',
            '.ecs-list{display:grid;gap:3px;max-height:290px;overflow:auto}',
            '.ecs-item{display:flex;align-items:center;gap:9px;width:100%;padding:8px;border:1px solid transparent;border-radius:11px;background:transparent;color:#ecfffb;text-align:left;cursor:pointer;font:inherit}',
            '.ecs-item:hover,.ecs-item:focus-visible{background:rgba(94,234,212,.08);border-color:rgba(94,234,212,.2);outline:none}',
            '.ecs-item.is-active{background:rgba(20,184,166,.14);border-color:rgba(94,234,212,.34)}',
            '.ecs-avatar{width:30px;height:30px;display:grid;place-items:center;border-radius:9px;background:rgba(94,234,212,.12);color:#5eead4;font-weight:900;font-size:10px;flex:none}',
            '.ecs-item-copy{display:grid;min-width:0;flex:1;line-height:1.2}',
            '.ecs-item-copy strong{font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
            '.ecs-item-copy small{font-size:9px;color:#9fd8cf;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
            '.ecs-check{color:#5eead4;font-weight:900;font-size:12px}',
            '.ecs-sep{height:1px;margin:8px 4px;background:rgba(94,234,212,.14)}',
            '.ecs-add{width:100%;padding:9px;border:1px dashed rgba(94,234,212,.35);border-radius:11px;background:rgba(94,234,212,.05);color:#5eead4;font:inherit;font-size:11px;font-weight:800;cursor:pointer}',
            '.ecs-add:hover{background:rgba(94,234,212,.11)}',
            '.ecs-note{padding:7px 7px 2px;font-size:9px;color:#9fd8cf;text-align:center;line-height:1.4}',
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
            '@media(max-width:767px){',
                '.ethio-company-switcher,.ethio-company-switcher.ecs-in-navbar{margin:0 4px}',
                '.ecs-trigger{min-height:32px;max-width:none;padding:4px 7px;gap:5px;border-radius:10px}',
                '.ecs-label{display:none}',
                '.ecs-mark{width:26px;height:26px;font-size:9px;border-radius:8px}',
                '.ecs-caret{font-size:9px}',
                '.ecs-menu{position:fixed;top:auto;bottom:8px;left:8px;right:8px;width:auto;max-width:none;max-height:72vh;overflow:auto;border-radius:16px}',
                '.ethio-company-switcher.ecs-fixed{top:auto;bottom:70px;right:10px}',
                '.ecs-modal{padding:10px}',
                '.ecs-modal-card{padding:16px;border-radius:16px}',
            '}'
        ].join('\n');
        document.head.appendChild(style);
    }

    function boot() {
        if (isGuest()) return;
        patchEmployeeLookups();
        ensureStyles();
        seedFromBoot();
        inject();
        loadCompanies();
        var observer = new MutationObserver(function () {
            if (!document.querySelector('.ethio-company-switcher')) {
                state.injected = false;
                inject();
                if (state.companies.length) loadCompanies();
            } else {
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
    document.addEventListener('frappe:ready', function () {
        if (!state.injected) boot();
    });
})();
