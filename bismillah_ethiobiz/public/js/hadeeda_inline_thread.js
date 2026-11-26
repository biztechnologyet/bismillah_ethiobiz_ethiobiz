/* Hadeeda inline-thread enhancement — additive chat-like conversation layer.
   Depends on nothing; enhances the existing ethiobiz_inline_ai.js popup only. */
(function () {
    "use strict";

    var INIT_FLAG = "data-eb-inline-thread-ready";
    var QUICK = [
        "Make it shorter",
        "More professional",
        "Translate into Amharic",
        "Give me bullet points"
    ];

    function el(tag, cls, text) {
        var node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text !== undefined) node.textContent = text;
        return node;
    }

    function nowTime() {
        try {
            return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        } catch (e) {
            return "";
        }
    }

    function scrollThread(thread) {
        if (!thread) return;
        thread.scrollTop = thread.scrollHeight;
    }

    function addMessage(thread, role, text) {
        var msg = el("div", "hadeeda-thread-msg hadeeda-thread-msg--" + role);
        var head = el("div", "hadeeda-thread-head");
        var meta = el("span", "hadeeda-thread-meta", role === "user" ? "You" : "Hadeeda");
        var time = el("span", "hadeeda-thread-time", nowTime());
        head.appendChild(meta);
        head.appendChild(time);
        msg.appendChild(head);

        var body = el("div", "hadeeda-thread-body", String(text || "").trim());
        msg.appendChild(body);

        if (role === "assistant") {
            var actions = el("div", "hadeeda-thread-actions");
            var copyBtn = el("button", "hadeeda-thread-action", "Copy");
            copyBtn.type = "button";
            copyBtn.addEventListener("click", function (e) {
                e.preventDefault();
                var value = body.textContent || "";
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(value);
                }
                copyBtn.textContent = "Copied";
                setTimeout(function () { copyBtn.textContent = "Copy"; }, 1400);
            });
            actions.appendChild(copyBtn);

            var insertBtn = el("button", "hadeeda-thread-action hadeeda-thread-action--insert", "Insert");
            insertBtn.type = "button";
            insertBtn.addEventListener("click", function (e) {
                e.preventDefault();
                var popup = thread.closest(".hadeeda-inline-popup");
                if (!popup) return;
                var preview = popup.querySelector(".hadeeda-result-preview");
                var baseInsert = popup.querySelector(".hadeeda-btn-insert");
                if (preview) preview.textContent = body.textContent || "";
                if (baseInsert) baseInsert.click();
            });
            actions.appendChild(insertBtn);
            msg.appendChild(actions);
        }

        thread.appendChild(msg);
        scrollThread(thread);
    }

    function ensureThread(popup) {
        if (!popup || popup.getAttribute(INIT_FLAG)) return;
        popup.setAttribute(INIT_FLAG, "1");

        var body = popup.querySelector(".hadeeda-inline-body");
        var promptView = popup.querySelector(".hadeeda-view-prompt");
        var resultView = popup.querySelector(".hadeeda-view-result");
        var promptInput = popup.querySelector(".hadeeda-inline-input");
        var sendBtn = popup.querySelector(".hadeeda-inline-submit");
        var resultPreview = popup.querySelector(".hadeeda-result-preview");
        var backBtn = popup.querySelector(".hadeeda-btn-back");
        if (!body || !promptView || !promptInput || !sendBtn) return;

        var threadWrap = el("div", "hadeeda-inline-thread-wrap");
        var threadHead = el("div", "hadeeda-thread-topbar");
        threadHead.appendChild(el("span", "hadeeda-thread-title", "Conversation"));
        var clearBtn = el("button", "hadeeda-thread-clear", "Clear");
        clearBtn.type = "button";
        threadHead.appendChild(clearBtn);
        threadWrap.appendChild(threadHead);

        var thread = el("div", "hadeeda-inline-thread");
        threadWrap.appendChild(thread);
        body.insertBefore(threadWrap, promptView);

        var quickWrap = el("div", "hadeeda-thread-quick");
        QUICK.forEach(function (text) {
            var btn = el("button", "", text);
            btn.type = "button";
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                promptInput.value = text;
                promptInput.dispatchEvent(new Event("input", { bubbles: true }));
                promptInput.focus();
            });
            quickWrap.appendChild(btn);
        });
        body.insertBefore(quickWrap, promptView);

        var follow = el("div", "hadeeda-thread-follow");
        var followInput = el("input", "hadeeda-thread-follow-input");
        followInput.type = "text";
        followInput.placeholder = "Continue conversation...";
        var followBtn = el("button", "hadeeda-thread-follow-send", "Send");
        followBtn.type = "button";
        follow.appendChild(followInput);
        follow.appendChild(followBtn);
        if (resultView && resultView.parentNode) {
            resultView.parentNode.insertBefore(follow, resultView.nextSibling);
        } else {
            body.appendChild(follow);
        }

        function sendFollow() {
            var text = String(followInput.value || "").trim();
            if (!text) return;
            promptInput.value = text;
            promptInput.dispatchEvent(new Event("input", { bubbles: true }));
            followInput.value = "";
            sendBtn.click();
        }

        followBtn.addEventListener("click", function (e) { e.preventDefault(); sendFollow(); });
        followInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") { e.preventDefault(); sendFollow(); }
        });

        clearBtn.addEventListener("click", function (e) {
            e.preventDefault();
            thread.innerHTML = "";
        });

        sendBtn.addEventListener("click", function () {
            var text = String(promptInput.value || "").trim();
            if (text) addMessage(thread, "user", text);
        }, true);

        if (resultPreview) {
            var last = "";
            var obs = new MutationObserver(function () {
                var text = String(resultPreview.textContent || "").trim();
                if (!text || text === last) return;
                last = text;
                addMessage(thread, "assistant", text);
            });
            obs.observe(resultPreview, { childList: true, characterData: true, subtree: true });
        }

        // When user clicks Back to prompt, keep conversation context visible.
        if (backBtn) {
            backBtn.addEventListener("click", function () {
                setTimeout(function () { promptInput.focus(); }, 50);
            });
        }
    }

    function scan() {
        document.querySelectorAll(".hadeeda-inline-popup").forEach(ensureThread);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", scan);
    } else {
        scan();
    }
    new MutationObserver(scan).observe(document.documentElement || document.body, { childList: true, subtree: true });
})();