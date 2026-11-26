/* Hadeeda standalone chat enhancement — additive UI polish only. */
(function () {
    "use strict";

    var FLAG = "data-eb-chat-enhanced";
    var PROMPTS = [
        "Draft a professional response",
        "Summarize this for me",
        "Translate into Amharic",
        "Give me bullet points"
    ];

    function make(tag, cls, text) {
        var node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text !== undefined) node.textContent = text;
        return node;
    }

    function send(text, input, sendButton) {
        if (!input) return;
        var setter = Object.getOwnPropertyDescriptor(input.constructor.prototype, "value");
        if (setter && setter.set) setter.set.call(input, text);
        else input.value = text;
        input.dispatchEvent(new Event("input", { bubbles: true }));
        if (sendButton) sendButton.click();
        else input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    }

    function fixComposer(win) {
        var inputs = win.querySelectorAll('.chat-inputs, .chat-footer .chat-inputs, .chat-input');
        for (var i=0;i<inputs.length;i++) {
            var c = inputs[i];
            if (c.querySelector && c.querySelector('textarea, input[type="text"]')) {
                c.style.display = 'flex';
                c.style.flexDirection = 'row';
                c.style.alignItems = 'flex-end';
                c.style.gap = '8px';
                c.style.flexWrap = 'nowrap';
            }
        }
        var ta = win.querySelectorAll('.chat-inputs textarea, textarea.chat-input, .chat-input textarea');
        for (var j=0;j<ta.length;j++) { ta[j].style.order='2'; ta[j].style.flex='1 1 auto'; ta[j].style.minWidth='0'; }
        var sends = win.querySelectorAll('.chat-input-send-button, button[type="submit"], .chat-inputs-controls button[type="submit"]');
        for (var k=0;k<sends.length;k++) { sends[k].style.order='3'; sends[k].style.flex='0 0 auto'; }
        var files = win.querySelectorAll('.chat-input-file-button, button[aria-label*="attach" i], button[aria-label*="file" i]');
        for (var m=0;m<files.length;m++) { files[m].style.order='1'; files[m].style.flex='0 0 auto'; }
    }

    function init(win) {
        if (!win) return;
        fixComposer(win);
        if (win.getAttribute(FLAG)) return;
        var footer = win.querySelector(".chat-footer, [class*='chat-footer']");
        var messages = win.querySelector(".chat-messages-list, .chat-body, [class*='chat-messages']");
        var input = win.querySelector("textarea.chat-input, input.chat-input, textarea[class*='chat-input'], .chat-inputs textarea");
        var sendButton = win.querySelector(".chat-input-send-button, button[class*='send']");
        if (!footer && !messages) return;

        win.setAttribute(FLAG, "1");

        if (messages && !messages.querySelector(".hadeeda-chat-day")) {
            var day = make("div", "hadeeda-chat-day", "Today in EthioBiz");
            messages.insertBefore(day, messages.firstChild);
        }

        if (footer && input && !win.querySelector(".hadeeda-chat-quick")) {
            var quick = make("div", "hadeeda-chat-quick");
            quick.setAttribute("role", "group");
            quick.setAttribute("aria-label", "Suggested Hadeeda prompts");
            PROMPTS.forEach(function (label) {
                var btn = make("button", "", label);
                btn.type = "button";
                btn.addEventListener("click", function () { send(label, input, sendButton); });
                quick.appendChild(btn);
            });
            footer.insertBefore(quick, footer.firstChild);
        }

        if (sendButton && !sendButton.getAttribute("aria-label")) {
            sendButton.setAttribute("aria-label", "Send message to Hadeeda");
        }
    }

    function scan() {
        var wins = document.querySelectorAll(".chat-window-wrapper .chat-window, .chat-window");
        for (var i = 0; i < wins.length; i += 1) init(wins[i]);
    }

    function start() {
        scan();
        var observer = new MutationObserver(scan);
        observer.observe(document.body, { childList: true, subtree: true });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start, { once: true });
    } else {
        start();
    }
})();
