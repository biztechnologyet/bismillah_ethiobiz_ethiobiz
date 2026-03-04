/**
 * EthioBiz Embedding Block for Editor.js
 * Bismillah Ar-Rahman Ar-Rahim
 * 
 * Super Nuclear Interceptor: Manual DOM injection fallback for Dagu LMS.
 */

class Embedding {
    static get toolbox() {
        return {
            title: 'Embedding',
            icon: '<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M15.8 10.5l-2.8 3.1c-.2.2-.5.3-.7.3s-.5-.1-.7-.3c-.4-.4-.4-1 0-1.4l1.4-1.5H7c-.6 0-1-.4-1-1s.4-1 1-1h6l-1.4-1.5c-.4-.4-.4-1 0-1.4.4-.4 1-.4 1.4 0l2.8 3.1c.4.4.4 1 0 1.4zM4.2 9.5l2.8-3.1c.2-.2.5-.3.7-.3s.5.1.7.3c.4.4.4 1 0 1.4L7 9.3h6c.6 0 1 .4 1 1s-.4 1-1 1H7l1.4 1.5c.4.4.4 1 0 1.4-.4.4-1 .4-1.4 0L4.2 10.9c-.4-.4-.4-1 0-1.4z"/></svg>'
        };
    }

    constructor({ data, api, config }) {
        this.api = api;
        this.data = {
            url: data.url || '',
            caption: data.caption || ''
        };
        this.wrapper = undefined;
    }

    render() {
        this.wrapper = document.createElement('div');
        this.wrapper.classList.add('ethiobiz-embed-wrapper');

        if (this.data && this.data.url) {
            this._showEmbed(this.data.url);
        } else {
            this._showInput();
        }

        return this.wrapper;
    }

    _showInput() {
        this.wrapper.innerHTML = '';
        const container = document.createElement('div');
        container.classList.add('ethiobiz-embed-input-container');
        container.style.padding = '10px';
        container.style.border = '1px solid #ddd';
        container.style.borderRadius = '8px';
        container.style.background = '#f9f9f9';

        const input = document.createElement('input');
        input.placeholder = 'Paste URL or <iframe> here...';
        input.value = this.data.url || '';
        input.style.width = '100%';
        input.style.padding = '8px';
        input.style.marginBottom = '10px';
        input.style.border = '1px solid #ccc';
        input.style.borderRadius = '4px';

        const button = document.createElement('button');
        button.innerText = 'Embed Content';
        button.style.padding = '8px 15px';
        button.style.background = '#1FB6AE';
        button.style.color = 'white';
        button.style.border = 'none';
        button.style.borderRadius = '4px';
        button.style.cursor = 'pointer';

        button.onclick = () => {
            let val = input.value.trim();
            if (val) {
                if (val.includes('<iframe')) {
                    const match = val.match(/src="([^"]+)"/);
                    if (match && match[1]) { val = match[1]; }
                }
                this.data.url = val;
                this._showEmbed(val);
            }
        };

        container.appendChild(input);
        container.appendChild(button);
        this.wrapper.appendChild(container);
    }

    _showEmbed(url) {
        this.wrapper.innerHTML = '';
        const container = document.createElement('div');
        container.style.position = 'relative';
        container.style.paddingBottom = '56.25%';
        container.style.height = '0';
        container.style.overflow = 'hidden';
        container.style.borderRadius = '8px';
        container.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';

        const iframe = document.createElement('iframe');
        iframe.src = url;
        iframe.style.position = 'absolute';
        iframe.style.top = '0';
        iframe.style.left = '0';
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = '0';
        iframe.setAttribute('allowfullscreen', 'true');

        const editBtn = document.createElement('button');
        editBtn.innerHTML = '✎ Change';
        editBtn.style.position = 'absolute';
        editBtn.style.top = '10px';
        editBtn.style.right = '10px';
        editBtn.style.zIndex = '10';
        editBtn.onclick = () => this._showInput();

        container.appendChild(iframe);
        this.wrapper.appendChild(container);
        this.wrapper.appendChild(editBtn);
    }

    save(blockContent) { return this.data; }
}

// ============================================
// SUPER NUCLEAR INTERCEPTOR - BISMALLAH
// ============================================

(function () {
    console.log('[EthioBiz] Super Nuclear Interceptor initializing...');

    const TOOL_NAME = 'embedding';
    const TOOL_TITLE = 'Embedding';
    const TOOL_ICON = '<svg width="20" height="20" viewBox="0 0 20 20"><path d="M15.8 10.5l-2.8 3.1c-.2.2-.5.3-.7.3s-.5-.1-.7-.3c-.4-.4-.4-1 0-1.4l1.4-1.5H7c-.6 0-1-.4-1-1s.4-1 1-1h6l-1.4-1.5c-.4-.4-.4-1 0-1.4.4-.4 1-.4 1.4 0l2.8 3.1c.4.4.4 1 0 1.4zM4.2 9.5l2.8-3.1c.2-.2.5-.3.7-.3s.5.1.7.3c.4.4.4 1 0 1.4L7 9.3h6c.6 0 1 .4 1 1s-.4 1-1 1H7l1.4 1.5c.4.4.4 1 0 1.4-.4.4-1 .4-1.4 0L4.2 10.9c-.4-.4-.4-1 0-1.4z"/></svg>';

    // --- STRATEGY 1: DOM Injection (MutationObserver) ---
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) {
                        // Check for Editor.js toolbox or popover
                        if (node.classList.contains('ce-popover') ||
                            node.querySelector('.ce-popover') ||
                            node.classList.contains('ce-toolbox')) {
                            injectToolManually(node);
                        }
                    }
                });
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    function injectToolManually(container) {
        // Find the list of tools
        const toolList = container.querySelector('.ce-popover__items') ||
            container.querySelector('.ce-toolbox__items') ||
            container;

        if (toolList && !toolList.querySelector(`[data-tool="${TOOL_NAME}"]`)) {
            console.log('[EthioBiz] Manually injecting tool into DOM');

            const item = document.createElement('div');
            item.className = 'ce-popover__item';
            item.setAttribute('data-tool', TOOL_NAME);
            item.style.cursor = 'pointer';

            item.innerHTML = `
                <div class="ce-popover__item-icon">${TOOL_ICON}</div>
                <div class="ce-popover__item-label">${TOOL_TITLE}</div>
            `;

            item.onclick = function (e) {
                e.preventDefault();
                e.stopPropagation();
                insertEmbeddingBlock();
                // Close toolbox
                const closeBtn = document.querySelector('.ce-toolbar__settings-btn');
                if (closeBtn) closeBtn.click();
            };

            toolList.appendChild(item);
        }
    }

    function insertEmbeddingBlock() {
        // Try to find the EditorJS instance
        const editorInstance = findEditorInstance();
        if (editorInstance && editorInstance.blocks) {
            editorInstance.blocks.insert(TOOL_NAME);
        } else {
            console.error('[EthioBiz] Could not find EditorJS instance to insert block');
            // Fallback: Notify user or try standard Frappe injection
            if (typeof frappe !== 'undefined' && frappe.show_alert) {
                frappe.show_alert({ message: 'Embedding tool failed to find editor instance', indicator: 'orange' });
            }
        }
    }

    function findEditorInstance() {
        // Search global variables
        for (let key in window) {
            if (window[key] && typeof window[key] === 'object' && window[key].blocks && window[key].save) {
                return window[key];
            }
        }
        // Search inside frappe.ui.Editor instances
        if (typeof frappe !== 'undefined' && frappe.ui && frappe.ui.instances) {
            for (let inst of frappe.ui.instances) {
                if (inst.editor && inst.editor.blocks) return inst.editor;
            }
        }
        return null;
    }

    // --- STRATEGY 2: Global Configuration Patching ---
    function patchConfig(config) {
        if (!config) return config;
        config.tools = config.tools || {};
        if (!config.tools[TOOL_NAME]) {
            config.tools[TOOL_NAME] = {
                class: Embedding,
                inlineToolbar: true
            };
        }
        return config;
    }

    // Patch known constructors
    if (typeof EditorJS !== 'undefined') {
        const Original = EditorJS;
        window.EditorJS = function (cfg) { return new Original(patchConfig(cfg)); };
        window.EditorJS.prototype = Original.prototype;
    }

    if (typeof frappe !== 'undefined' && frappe.ui && frappe.ui.Editor) {
        const Original = frappe.ui.Editor;
        frappe.ui.Editor = function (opts) {
            if (opts.options) opts.options = patchConfig(opts.options);
            return new Original(opts);
        };
        frappe.ui.Editor.prototype = Original.prototype;
    }

})();
