/* Hadeeda inline-thread enhancement — chat-like continuous conversation. */
(function () {
    "use strict";

    var INIT_FLAG = "data-eb-inline-thread-ready";
    var QUICK = [
        "Make it shorter",
        "More professional",
        "Translate into Amharic",
        "Give me bullet points",
        "Summarize this page"
    ];

    function el(tag, cls, text) {
        var node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text !== undefined && text !== null) node.textContent = text;
        return node;
    }

    function escapeHtml(s) {
        return String(s || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function renderMarkdown(text) {
        var src = String(text || "").replace(/\r\n/g, "\n").trim();
        if (!src) return "";
        // Escape first, then apply a safe subset of markdown.
        var s = escapeHtml(src);

        // Code blocks ``` ```
        s = s.replace(/```([\s\S]*?)```/g, function (_, code) {
            return '<pre class="hadeeda-md-code"><code>' + code.trim() + '</code></pre>';
        });
        // Inline code
        s = s.replace(/`([^`]+)`/g, '<code class="hadeeda-md-inline">$1</code>');
        // Headings
        s = s.replace(/^###\s+(.+)$/gm, '<h4 class="hadeeda-md-h">$1</h4>');
        s = s.replace(/^##\s+(.+)$/gm, '<h3 class="hadeeda-md-h">$1</h3>');
        s = s.replace(/^#\s+(.+)$/gm, '<h2 class="hadeeda-md-h">$1</h2>');
        // Bold / italic
        s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        s = s.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');

        // Lists: group consecutive list items
        var lines = s.split('\n');
        var out = [], inUl = false, inOl = false;
        function closeLists() { if (inUl) { out.push('</ul>'); inUl = false; } if (inOl) { out.push('</ol>'); inOl = false; } }
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            var ul = line.match(/^\s*[-*]\s+(.*)$/);
            var ol = line.match(/^\s*\d+\.\s+(.*)$/);
            if (ul) { if (inOl) { out.push('</ol>'); inOl = false; } if (!inUl) { out.push('<ul class="hadeeda-md-list">'); inUl = true; } out.push('<li>' + ul[1] + '</li>'); continue; }
            if (ol) { if (inUl) { out.push('</ul>'); inUl = false; } if (!inOl) { out.push('<ol class="hadeeda-md-list">'); inOl = true; } out.push('<li>' + ol[1] + '</li>'); continue; }
            closeLists();
            if (!line.trim()) { out.push(''); continue; }
            if (/^<h[234] class="hadeeda-md-h">/.test(line) || /^<pre class="hadeeda-md-code">/.test(line)) { out.push(line); continue; }
            out.push('<p class="hadeeda-md-p">' + line + '</p>');
        }
        closeLists();
        return out.join('\n').replace(/(<\/pre>)\n/g, '$1');
    }

    function nowTime() {
        try { return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); }
        catch (e) { return ""; }
    }

    function scrollThread(thread) {
        if (!thread) return;
        requestAnimationFrame(function () { thread.scrollTop = thread.scrollHeight; });
    }

    function addMessage(thread, role, text, opts) {
        opts = opts || {};
        var msg = el("div", "hadeeda-thread-msg hadeeda-thread-msg--" + role);
        var head = el("div", "hadeeda-thread-head");
        head.appendChild(el("span", "hadeeda-thread-meta", role === "user" ? "You" : "Hadeeda"));
        head.appendChild(el("span", "hadeeda-thread-time", nowTime()));
        msg.appendChild(head);

        var body = el("div", "hadeeda-thread-body");
        if (role === "assistant") body.innerHTML = renderMarkdown(text);
        else body.textContent = String(text || "").trim();
        msg.appendChild(body);

        if (role === "assistant") {
            var actions = el("div", "hadeeda-thread-actions");
            function addAction(label, cls, fn) {
                var btn = el("button", "hadeeda-thread-action " + (cls || ""), label);
                btn.type = "button";
                btn.addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); fn(btn); });
                actions.appendChild(btn);
            }
            addAction("Copy", "", function (btn) {
                var value = body.innerText || body.textContent || "";
                if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(value);
                var old = btn.textContent; btn.textContent = "Copied"; setTimeout(function () { btn.textContent = old; }, 1400);
            });
            addAction("Insert", "hadeeda-thread-action--insert", function () {
                var popup = thread.closest(".hadeeda-inline-popup");
                if (!popup) return;
                var preview = popup.querySelector(".hadeeda-result-preview");
                var baseInsert = popup.querySelector(".hadeeda-btn-insert");
                if (preview) preview.textContent = body.innerText || body.textContent || "";
                if (baseInsert) baseInsert.click();
            });
            addAction("Shorter", "", function () { if (opts.onQuick) opts.onQuick("Make it shorter"); });
            addAction("Professional", "", function () { if (opts.onQuick) opts.onQuick("More professional"); });
            addAction("Amharic", "", function () { if (opts.onQuick) opts.onQuick("Translate into Amharic"); });
            addAction("Bullets", "", function () { if (opts.onQuick) opts.onQuick("Give me bullet points"); });
            msg.appendChild(actions);
        }

        thread.appendChild(msg);
        scrollThread(thread);
        return msg;
    }

    function ensureThread(popup) {
        if (!popup || popup.getAttribute(INIT_FLAG)) return;
        popup.setAttribute(INIT_FLAG, "1");

        var bodyWrap = popup.querySelector(".hadeeda-inline-body");
        var promptView = popup.querySelector(".hadeeda-view-prompt");
        var resultView = popup.querySelector(".hadeeda-view-result");
        var promptInput = popup.querySelector(".hadeeda-inline-input");
        var sendBtn = popup.querySelector(".hadeeda-inline-submit");
        var resultPreview = popup.querySelector(".hadeeda-result-preview");
        if (!bodyWrap || !promptView || !promptInput || !sendBtn) return;

        var threadWrap = el("div", "hadeeda-inline-thread-wrap");
        var threadHead = el("div", "hadeeda-thread-topbar");
        threadHead.appendChild(el("span", "hadeeda-thread-title", "Conversation"));
        var clearBtn = el("button", "hadeeda-thread-clear", "Clear");
        clearBtn.type = "button";
        threadHead.appendChild(clearBtn);
        threadWrap.appendChild(threadHead);
        var thread = el("div", "hadeeda-inline-thread");
        threadWrap.appendChild(thread);
        bodyWrap.insertBefore(threadWrap, promptView);

        var quickWrap = el("div", "hadeeda-thread-quick");
        QUICK.forEach(function (text) {
            var btn = el("button", "", text);
            btn.type = "button";
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                promptInput.value = text;
                promptInput.dispatchEvent(new Event("input", { bubbles: true }));
                sendBtn.click();
            });
            quickWrap.appendChild(btn);
        });
        bodyWrap.insertBefore(quickWrap, promptView);

        var follow = el("div", "hadeeda-thread-follow");
        var followInput = el("input", "hadeeda-thread-follow-input");
        followInput.type = "text";
        followInput.placeholder = "Continue conversation...";
        var followBtn = el("button", "hadeeda-thread-follow-send", "Send");
        followBtn.type = "button";
        follow.appendChild(followInput);
        follow.appendChild(followBtn);
        if (resultView && resultView.parentNode) resultView.parentNode.insertBefore(follow, resultView.nextSibling);
        else bodyWrap.appendChild(follow);

        function sendFollow(text) {
            var msg = String(text || followInput.value || "").trim();
            if (!msg) return;
            promptInput.value = msg;
            promptInput.dispatchEvent(new Event("input", { bubbles: true }));
            followInput.value = "";
            sendBtn.click();
        }

        followBtn.addEventListener("click", function (e) { e.preventDefault(); sendFollow(); });
        followInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") { e.preventDefault(); sendFollow(); }
        });
        clearBtn.addEventListener("click", function (e) { e.preventDefault(); thread.innerHTML = ""; });

        sendBtn.addEventListener("click", function () {
            var text = String(promptInput.value || "").trim();
            if (text) addMessage(thread, "user", text, { onQuick: sendFollow });
        }, true);

        if (resultPreview) {
            var last = "";
            var obs = new MutationObserver(function () {
                var text = String(resultPreview.textContent || "").trim();
                if (!text || text === last) return;
                last = text;
                addMessage(thread, "assistant", text, { onQuick: sendFollow });
            });
            obs.observe(resultPreview, { childList: true, characterData: true, subtree: true });
        }
    }

    function scan() { document.querySelectorAll(".hadeeda-inline-popup").forEach(ensureThread); }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", scan); else scan();
    new MutationObserver(scan).observe(document.documentElement || document.body, { childList: true, subtree: true });
})();