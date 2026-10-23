document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const promptInput = document.getElementById('promptInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const quickButtons = document.querySelectorAll('.quick-btn');

    // Auto-scroll helper
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Auto-resize textarea
    promptInput.addEventListener('input', () => {
        promptInput.style.height = 'auto';
        promptInput.style.height = `${Math.min(promptInput.scrollHeight, 120)}px`;
    });

    // Enter to submit (Shift+Enter for newline)
    promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Quick prompt buttons
    quickButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.getAttribute('data-prompt');
            if (prompt) {
                promptInput.value = prompt;
                promptInput.focus();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });

    // Minimal Markdown formatter for safe inline display
    function formatMarkdown(text) {
        if (!text) return '';
        let formatted = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Code blocks: ```...```
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        // Inline code: `...`
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Bold: **...**
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        // Italic: *...*
        formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        // Simple Markdown tables
        if (formatted.includes('|')) {
            const lines = formatted.split('\n');
            let inTable = false;
            let tableHtml = '<table>';
            let processedLines = [];

            for (let line of lines) {
                if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
                    const cells = line.split('|').slice(1, -1).map(c => c.trim());
                    if (cells.every(c => /^[-:]+$/.test(c))) {
                        continue; // table delimiter
                    }
                    if (!inTable) {
                        inTable = true;
                        tableHtml += '<thead><tr>' + cells.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>';
                    } else {
                        tableHtml += '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>';
                    }
                } else {
                    if (inTable) {
                        tableHtml += '</tbody></table>';
                        processedLines.push(tableHtml);
                        inTable = false;
                        tableHtml = '<table>';
                    }
                    processedLines.push(line);
                }
            }
            if (inTable) {
                tableHtml += '</tbody></table>';
                processedLines.push(tableHtml);
            }
            formatted = processedLines.join('\n');
        }

        // Paragraphs / linebreaks
        formatted = formatted.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
        return `<p>${formatted}</p>`;
    }

    // Submit handler
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = promptInput.value.trim();
        if (!message) return;

        // Append user message
        const userMsgDiv = document.createElement('div');
        userMsgDiv.className = 'message user-message';
        userMsgDiv.innerHTML = `<div class="message-content"><p>${formatMarkdown(message)}</p></div>`;
        chatMessages.appendChild(userMsgDiv);

        // Reset input
        promptInput.value = '';
        promptInput.style.height = 'auto';
        promptInput.disabled = true;
        sendBtn.disabled = true;
        scrollToBottom();

        // Create assistant response container
        const assistantMsgDiv = document.createElement('div');
        assistantMsgDiv.className = 'message assistant-message';
        assistantMsgDiv.innerHTML = `
            <div class="message-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
            </div>
            <div class="message-content">
                <div class="stream-text"></div>
                <span class="typing-cursor"></span>
            </div>
        `;
        chatMessages.appendChild(assistantMsgDiv);
        scrollToBottom();

        const streamTextDiv = assistantMsgDiv.querySelector('.stream-text');
        const cursor = assistantMsgDiv.querySelector('.typing-cursor');
        let accumulatedResponse = '';

        try {
            const response = await fetch('/api/v1/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                },
                body: JSON.stringify({ prompt: message })
            });

            if (!response.ok) {
                const errJson = await response.json().catch(() => ({ detail: response.statusText }));
                streamTextDiv.innerHTML = `<p style="color: var(--danger-red);">Error (${response.status}): ${errJson.detail || 'Failed to stream response'}</p>`;
                if (cursor) cursor.remove();
                return;
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    const trimmed = line.trim();
                    if (trimmed.startsWith('data:')) {
                        const rawData = trimmed.slice(5).trim();
                        if (rawData === '[DONE]') {
                            break;
                        }
                        try {
                            const parsed = JSON.parse(rawData);
                            if (parsed.content) {
                                accumulatedResponse += parsed.content;
                                streamTextDiv.innerHTML = formatMarkdown(accumulatedResponse);
                                scrollToBottom();
                            }
                        } catch {
                            // If plain text line
                            accumulatedResponse += rawData;
                            streamTextDiv.innerHTML = formatMarkdown(accumulatedResponse);
                            scrollToBottom();
                        }
                    }
                }
            }

            // Final flush
            if (buffer.trim().startsWith('data:')) {
                const rawData = buffer.trim().slice(5).trim();
                if (rawData && rawData !== '[DONE]') {
                    try {
                        const parsed = JSON.parse(rawData);
                        if (parsed.content) accumulatedResponse += parsed.content;
                    } catch {
                        accumulatedResponse += rawData;
                    }
                }
            }
            streamTextDiv.innerHTML = formatMarkdown(accumulatedResponse);

        } catch (error) {
            console.error('Streaming error:', error);
            streamTextDiv.innerHTML = `<p style="color: var(--danger-red);">Connection error: ${error.message}</p>`;
        } finally {
            if (cursor) cursor.remove();
            promptInput.disabled = false;
            sendBtn.disabled = false;
            promptInput.focus();
            scrollToBottom();
        }
    });
});
