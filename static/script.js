/**
 * ═══════════════════════════════════════════════════════════════
 * Adaptive AI Mentor System v2.0 — Frontend Controller
 * ═══════════════════════════════════════════════════════════════
 *
 * Manages:
 *  1. Dual-mode adaptive chat (Discovery / Guided) w/ open-text
 *  2. RIASEC, Big Five, Aptitude question routing
 *  3. Results dashboard: RIASEC chart, Big Five bars, aptitude,
 *     CSS breakdown, roadmaps, location intelligence, community
 *
 * Pure vanilla JS — no external libraries.
 * ═══════════════════════════════════════════════════════════════
 */
(function () {
    'use strict';

    // ─────────────────────────────────────────
    // STATE
    // ─────────────────────────────────────────
    const state = {
        responses: [],
        currentQuestion: null,
        isProcessing: false,
        completedPhases: new Set(),
    };

    const delay = ms => new Promise(r => setTimeout(r, ms));

    function scrollToBottom() {
        const c = document.querySelector('.chat-main');
        if (c) c.scrollTo({ top: c.scrollHeight, behavior: 'smooth' });
    }

    async function apiPost(url, data) {
        const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        return r.json();
    }

    // RIASEC colors for charts
    const RIASEC_COLORS = { R: '#ff6b6b', I: '#7c5cfc', A: '#ff6b9d', S: '#00e5c7', E: '#ffb547', C: '#40c4ff' };
    const RIASEC_LABELS = { R: 'Realistic', I: 'Investigative', A: 'Artistic', S: 'Social', E: 'Enterprising', C: 'Conventional' };
    const BIG5_COLORS = { O: '#7c5cfc', C: '#00e5c7', E: '#ffb547', A: '#ff6b9d', N: '#40c4ff' };
    const BIG5_LABELS = { O: 'Openness', C: 'Conscientiousness', E: 'Extraversion', A: 'Agreeableness', N: 'Neuroticism' };
    const CSS_COLORS = ['#7c5cfc', '#00e5c7', '#ff6b9d', '#ffb547', '#40c4ff'];

    // ═══════════════════════════════════════════
    // CHAT PAGE
    // ═══════════════════════════════════════════
    const chatMessages = document.getElementById('chatMessages');

    if (chatMessages) {
        // Show user greeting
        const user = JSON.parse(sessionStorage.getItem('user') || '{}');
        const greet = document.getElementById('userGreeting');
        if (greet && user.name) greet.textContent = `Hello, ${user.name}`;

        initChat();
    }

    async function initChat() {
        addBotMessage(
            "Welcome to the AI Career Mentor psychometric assessment! ",
            "This system uses Holland's RIASEC, Big Five personality, and multi-aptitude models to map your career DNA."
        );
        await delay(700);
        addBotMessage(
            "The assessment has 18 adaptive questions across 6 phases. Let's begin!",
            "All recommendations will be computed from your responses — nothing is random."
        );
        await delay(500);

        const result = await apiPost('/api/question', { responses: [] });
        if (result.status === 'question') displayQuestion(result.question);
    }

    function addBotMessage(text, subtext) {
        const d = document.createElement('div');
        d.className = 'message message-bot';
        d.innerHTML = `<div class="message-avatar"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><path d="M8 16h.01"/><path d="M16 16h.01"/></svg></div><div class="message-body"><div class="message-bubble">${text}</div>${subtext ? `<div class="message-subtext">${subtext}</div>` : ''}</div>`;
        chatMessages.appendChild(d);
        scrollToBottom();
    }

    function addUserMessage(text) {
        const d = document.createElement('div');
        d.className = 'message message-user';
        // Truncate very long text for display
        const displayText = text.length > 200 ? text.substring(0, 200) + '...' : text;
        d.innerHTML = `<div class="message-avatar">👤</div><div class="message-body"><div class="message-bubble">${displayText}</div></div>`;
        chatMessages.appendChild(d);
        scrollToBottom();
    }

    function showTyping() {
        const d = document.createElement('div');
        d.className = 'message message-bot'; d.id = 'typingIndicator';
        d.innerHTML = `<div class="message-avatar"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><path d="M8 16h.01"/><path d="M16 16h.01"/></svg></div><div class="message-body"><div class="message-bubble typing-indicator"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div></div>`;
        chatMessages.appendChild(d);
        scrollToBottom();
    }

    function hideTyping() {
        const t = document.getElementById('typingIndicator');
        if (t) t.remove();
    }

    function displayQuestion(question) {
        state.currentQuestion = question;
        updateSidebar(question);
        updateProgress(question);

        const d = document.createElement('div');
        d.className = 'message message-bot';

        let inputHTML = '';

        if (question.type === 'open_text') {
            // Open-text input with textarea
            const placeholder = question.placeholder || 'Type your response here...';
            inputHTML = `
                <div class="text-input-area">
                    <textarea id="openTextInput" placeholder="${placeholder}" maxlength="1500"></textarea>
                    <div class="text-submit-row">
                        <span class="char-count" id="charCount">0 / 1500</span>
                        <button class="text-submit-btn" id="textSubmitBtn" onclick="window.__submitText()">Submit Response →</button>
                    </div>
                </div>`;
        } else {
            // Choice options
            inputHTML = '<div class="options-grid">';
            question.options.forEach(opt => {
                const safeLabel = opt.label.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                inputHTML += `
                    <button class="option-btn" data-value="${opt.value}" onclick="window.__selectOption('${opt.value}', '${safeLabel}')">
                        ${opt.icon ? `<span class="option-icon">${opt.icon}</span>` : ''}
                        <span>${opt.label}</span>
                    </button>`;
            });
            inputHTML += '</div>';
        }

        d.innerHTML = `
            <div class="message-avatar">🧠</div>
            <div class="message-body">
                <div class="message-bubble">${question.text}</div>
                ${question.subtext ? `<div class="message-subtext">${question.subtext}</div>` : ''}
                ${inputHTML}
            </div>`;

        chatMessages.appendChild(d);
        scrollToBottom();

        // Wire up open-text character counter with multiple event sources
        if (question.type === 'open_text') {
            const ta = document.getElementById('openTextInput');
            const cc = document.getElementById('charCount');
            if (ta) {
                ta.focus();
                const updateCount = () => {
                    cc.textContent = `${ta.value.length} / 1500`;
                };
                ta.addEventListener('input', updateCount);
                ta.addEventListener('keyup', updateCount);
                ta.addEventListener('change', updateCount);
                ta.addEventListener('paste', () => setTimeout(updateCount, 50));
                // Polling fallback for programmatic text insertion
                const poll = setInterval(() => {
                    if (!document.getElementById('openTextInput')) { clearInterval(poll); return; }
                    updateCount();
                }, 500);
            }
        }
    }

    // ── Handle choice selection ───────────────
    window.__selectOption = async function (value, label) {
        if (state.isProcessing) return;
        state.isProcessing = true;

        // Disable all buttons
        chatMessages.querySelectorAll('.option-btn').forEach(b => {
            b.style.pointerEvents = 'none';
            if (b.dataset.value === value) b.classList.add('selected');
        });

        await delay(200);
        addUserMessage(label);
        state.responses.push({ question_id: state.currentQuestion.id, answer: value });
        state.completedPhases.add(state.currentQuestion.phase);

        await advanceToNext();
        state.isProcessing = false;
    };

    // ── Handle open-text submission ───────────
    window.__submitText = async function () {
        if (state.isProcessing) return;
        state.isProcessing = true;

        const ta = document.getElementById('openTextInput');
        const text = ta ? ta.value.trim() : '';
        if (text.length < 10) {
            // Show brief validation hint
            if (ta) { ta.style.borderColor = 'var(--accent-tertiary)'; }
            state.isProcessing = false;
            return;
        }

        // Disable input
        if (ta) ta.disabled = true;
        const sb = document.getElementById('textSubmitBtn');
        if (sb) { sb.disabled = true; sb.textContent = 'Submitted ✓'; }

        await delay(200);
        addUserMessage(text);
        state.responses.push({ question_id: state.currentQuestion.id, answer: text });
        state.completedPhases.add(state.currentQuestion.phase);

        await advanceToNext();
        state.isProcessing = false;
    };

    async function advanceToNext() {
        await delay(400);
        showTyping();
        await delay(500 + Math.random() * 400);

        const result = await apiPost('/api/question', { responses: state.responses });
        hideTyping();

        if (result.status === 'question') {
            const prevPhase = state.currentQuestion.phase;
            if (result.question.phase !== prevPhase) {
                await delay(300);
                const msgs = {
                    interest: "Now let's map your interests using Holland's RIASEC framework.",
                    personality: "Excellent! Moving to Big Five personality assessment — 5 scenario-based questions.",
                    opentext: "Now I'd like to hear from you in your own words. Your text is analyzed for personality markers (weighted 1.5× MCQ).",
                    aptitude: "Time for the aptitude battery — logical, creative, and verbal reasoning tests.",
                    behavioral: "Almost done! One final question about your career growth preferences.",
                };
                if (msgs[result.question.phase]) {
                    addBotMessage(msgs[result.question.phase]);
                    await delay(500);
                }
            }
            displayQuestion(result.question);
        } else if (result.status === 'complete') {
            await handleComplete();
        }
    }

    async function handleComplete() {
        addBotMessage("Assessment complete! ", "Running the full psychometric analysis pipeline...");
        await delay(600);

        const overlay = document.getElementById('loadingOverlay');
        const lt = document.getElementById('loadingText');
        overlay.classList.add('active');

        const phases = [
            "Computing Holland's RIASEC interest vector...",
            "Scoring Big Five personality dimensions...",
            "Analyzing open-text responses (keyword extraction)...",
            "Evaluating aptitude battery results...",
            "Checking behavioral consistency flags...",
            "Computing Career Suitability Scores (CSS)...",
            "Generating personalized roadmaps...",
            "Loading Pune/Maharashtra intelligence...",
            "Preparing your intelligence report...",
        ];
        for (const p of phases) { lt.textContent = p; await delay(400 + Math.random() * 300); }

        try {
            const res = await apiPost('/api/analyze', { responses: state.responses });
            if (res.status === 'success') {
                sessionStorage.setItem('careerResults', JSON.stringify(res));
                window.location.href = '/result';
            } else {
                overlay.classList.remove('active');
                addBotMessage("Analysis error: " + (res.message || "Unknown"));
            }
        } catch (e) {
            overlay.classList.remove('active');
            addBotMessage("Connection error. Please try again.");
        }
    }

    function updateSidebar(q) {
        document.querySelectorAll('.phase-item').forEach(item => {
            const phase = item.dataset.phase;
            item.classList.remove('active');
            if (state.completedPhases.has(phase) && phase !== q.phase) item.classList.add('completed');
            if (phase === q.phase) item.classList.add('active');
        });
    }

    function updateProgress(q) {
        const step = q.step || 1, total = q.total_steps || 18;
        const pct = Math.round((step / total) * 100);
        const pf = document.getElementById('progressFill');
        const pp = document.getElementById('progressPercent');
        const qc = document.getElementById('questionCount');
        if (pf) pf.style.width = pct + '%';
        if (pp) pp.textContent = pct + '%';
        if (qc) qc.textContent = `${step} of ${total} questions`;
    }


    // ═══════════════════════════════════════════
    // RESULTS PAGE
    // ═══════════════════════════════════════════
    const resultPage = document.getElementById('resultPage');
    const noDataState = document.getElementById('noDataState');

    if (resultPage && noDataState) initResults();

    function initResults() {
        const raw = sessionStorage.getItem('careerResults');
        if (!raw) { resultPage.style.display = 'none'; noDataState.style.display = 'block'; return; }
        noDataState.style.display = 'none';
        const data = JSON.parse(raw);
        renderRIASEC(data.profile.riasec);
        renderBig5(data.profile.big5);
        renderAptitude(data.profile.aptitudes, data.profile.behavioral);
        renderCareerCards(data.results);
        renderAllScores(data.all_scores);
        renderCommunity(data.community);
        renderMeta(data.metadata, data.profile);
    }

    // ── RIASEC Bar Chart ──────────────────────
    function renderRIASEC(riasec) {
        const el = document.getElementById('riasecChart');
        if (!el) return;
        const dims = ['R', 'I', 'A', 'S', 'E', 'C'];
        el.innerHTML = dims.map(d => {
            const val = riasec[d] || 0;
            const pct = (val / 10) * 100;
            return `
                <div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:6px;">
                    <div style="font-size:0.85rem; font-weight:700; color:${RIASEC_COLORS[d]}">${val}</div>
                    <div style="width:100%; height:160px; background:rgba(255,255,255,0.03); border-radius:8px; display:flex; align-items:flex-end; overflow:hidden;">
                        <div style="width:100%; height:${pct}%; background:${RIASEC_COLORS[d]}; border-radius:8px 8px 0 0; transition:height 1.5s ease; opacity:0.85;"></div>
                    </div>
                    <div style="font-size:0.72rem; font-weight:600; color:${RIASEC_COLORS[d]}; text-transform:uppercase; letter-spacing:0.05em;">${d}</div>
                    <div style="font-size:0.7rem; color:var(--text-muted);">${RIASEC_LABELS[d]}</div>
                </div>`;
        }).join('');
    }

    // ── Big Five Bars ─────────────────────────
    function renderBig5(big5) {
        const el = document.getElementById('big5Chart');
        if (!el) return;
        const dims = ['O', 'C', 'E', 'A', 'N'];
        el.innerHTML = dims.map(d => {
            const val = big5[d] || 5;
            const pct = (val / 10) * 100;
            return `
                <div style="margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="font-size:0.82rem; color:${BIG5_COLORS[d]}; font-weight:500;">${BIG5_LABELS[d]}</span>
                        <span style="font-size:0.82rem; font-weight:600; color:${BIG5_COLORS[d]}">${val}/10</span>
                    </div>
                    <div style="height:6px; background:rgba(255,255,255,0.04); border-radius:99px; overflow:hidden;">
                        <div style="height:100%; width:${pct}%; background:${BIG5_COLORS[d]}; border-radius:99px; transition:width 1.2s ease; opacity:0.8;"></div>
                    </div>
                </div>`;
        }).join('');
    }

    // ── Aptitude + Behavioral ─────────────────
    function renderAptitude(aptitudes, behavioral) {
        const el = document.getElementById('aptChart');
        if (!el) return;
        const aptDims = [
            { key: 'logical', label: 'Logical', color: '#7c5cfc' },
            { key: 'creative', label: 'Creative', color: '#ff6b9d' },
            { key: 'verbal', label: 'Verbal', color: '#00e5c7' },
        ];
        let html = aptDims.map(d => {
            const val = aptitudes[d.key] || 5;
            const pct = (val / 10) * 100;
            return `
                <div style="margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="font-size:0.82rem; color:${d.color}; font-weight:500;">${d.label} Aptitude</span>
                        <span style="font-size:0.82rem; font-weight:600; color:${d.color}">${val}/10</span>
                    </div>
                    <div style="height:6px; background:rgba(255,255,255,0.04); border-radius:99px; overflow:hidden;">
                        <div style="height:100%; width:${pct}%; background:${d.color}; border-radius:99px; transition:width 1.2s ease; opacity:0.8;"></div>
                    </div>
                </div>`;
        }).join('');

        // Behavioral
        html += `
            <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border-subtle);">
                <div style="font-size:0.82rem; font-weight:600; color:var(--text-muted); margin-bottom:10px; text-transform:uppercase; letter-spacing:0.05em;">Behavioral Signals</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                    <div style="padding:10px; background:var(--bg-glass); border-radius:8px; text-align:center;">
                        <div style="font-size:1.1rem; font-weight:700; color:${behavioral.consistency_score >= 7 ? 'var(--accent-success)' : 'var(--accent-warning)'}">${behavioral.consistency_score}/10</div>
                        <div style="font-size:0.72rem; color:var(--text-muted);">Consistency</div>
                    </div>
                    <div style="padding:10px; background:var(--bg-glass); border-radius:8px; text-align:center;">
                        <div style="font-size:1.1rem; font-weight:700; color:var(--accent-info)">${behavioral.confidence_level}/10</div>
                        <div style="font-size:0.72rem; color:var(--text-muted);">Confidence</div>
                    </div>
                </div>
                <div style="margin-top:8px; font-size:0.78rem; color:${behavioral.consistency_score >= 7 ? 'var(--accent-success)' : 'var(--accent-warning)'};">
                    ${behavioral.alignment_status}
                </div>
            </div>`;
        el.innerHTML = html;
    }

    // ── Career Cards ──────────────────────────
    function renderCareerCards(results) {
        const el = document.getElementById('careerCards');
        if (!el) return;
        el.innerHTML = results.map((r, idx) => {
            const rank = idx + 1;
            const rc = rank <= 3 ? `rank-${rank}` : 'rank-other';
            const sc = r.css >= 70 ? '#00e676' : (r.css >= 55 ? '#ffb547' : '#ff6b9d');
            const bd = r.breakdown;

            return `
            <div class="glass-card career-card fade-in fade-in-delay-${idx + 1}" onclick="window.__toggleDetail('det-${idx}')" id="card-${idx}">
                <div class="career-card-header">
                    <div class="career-rank ${rc}">#${rank}</div>
                    <div class="career-info">
                        <h3>
                            <span>${r.icon}</span> ${r.title}
                            <span class="badge ${r.css >= 70 ? 'badge-success' : (r.css >= 55 ? 'badge-warning' : 'badge-danger')}">${r.css >= 70 ? 'Strong Fit' : (r.css >= 55 ? 'Good Potential' : 'Exploratory')}</span>
                        </h3>
                        <p class="career-desc">${r.description}</p>
                        <div class="career-meta">
                            <span class="badge badge-primary"> ${r.salary_range}</span>
                            <span class="badge ${r.growth_outlook === 'Very High' ? 'badge-success' : 'badge-primary'}"> ${r.growth_outlook}</span>
                            <span class="badge badge-warning">🏷️ ${r.category}</span>
                        </div>
                        <!-- CSS Breakdown mini bars -->
                        <div class="css-breakdown">
                            ${['Interest', 'Aptitude', 'Traits', 'Behavioral', 'Stage'].map((label, i) => {
                                const keys = ['interest_match', 'aptitude_match', 'traits_match', 'behavioral', 'stage_fit'];
                                const v = bd[keys[i]];
                                return `<div class="css-dim">
                                    <span class="css-dim-label">${label}</span>
                                    <div class="css-dim-bar"><div class="css-dim-fill" style="width:${v}%;background:${CSS_COLORS[i]}"></div></div>
                                    <span class="css-dim-val">${v}%</span>
                                </div>`;
                            }).join('')}
                        </div>
                        <!-- Explanations -->
                        <div class="explanation-list">
                            ${r.explanations.map(e => `
                                <div class="explanation-item ${e.type}">
                                    <span>${e.type === 'strength' ? '✅' : (e.type === 'gap' ? '⚠️' : (e.type === 'insight' ? '💡' : (e.type === 'flag' ? '🚩' : '📌')))}</span>
                                    <span><strong>${e.cat}:</strong> ${e.text}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="career-score-display">
                        <div class="score-big" style="color:${sc}">${r.css}</div>
                        <div class="score-label">CSS / 100</div>
                    </div>
                </div>

                <!-- Expandable Detail -->
                <div class="career-detail" id="det-${idx}">
                    <div class="detail-tabs">
                        <button class="detail-tab active" onclick="event.stopPropagation(); window.__switchTab('det-${idx}', 'roadmap-${idx}', this)"> Roadmap</button>
                        <button class="detail-tab" onclick="event.stopPropagation(); window.__switchTab('det-${idx}', 'gaps-${idx}', this)"> Skill Gaps</button>
                        <button class="detail-tab" onclick="event.stopPropagation(); window.__switchTab('det-${idx}', 'location-${idx}', this)">📍 Pune Info</button>
                    </div>

                    <!-- Roadmap Tab -->
                    <div class="tab-content active" id="roadmap-${idx}">
                        <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:var(--space-md);">
                            Starting level: <strong style="color:var(--accent-primary)">${r.roadmap.starting_level}</strong> │ Estimated duration: <strong>${r.roadmap.total_duration}</strong>
                        </p>
                        <table class="roadmap-table">
                            <thead><tr><th>Stage</th><th>Key Skills</th><th>Tools</th><th>Projects</th><th>Duration</th></tr></thead>
                            <tbody>
                                ${r.roadmap.stages.map(s => `
                                    <tr>
                                        <td><span class="roadmap-table .stage-badge stage-${s.level.toLowerCase()}" style="display:inline-block;padding:3px 10px;border-radius:99px;font-size:0.72rem;font-weight:600;background:rgba(var(--accent-primary-rgb),0.12);color:var(--accent-primary);">${s.level}${s.is_starting ? ' ★' : ''}</span></td>
                                        <td><div class="skills-tags">${s.skills.map(sk => `<span class="skill-tag">${sk}</span>`).join('')}</div></td>
                                        <td><div class="skills-tags">${s.tools.map(t => `<span class="tool-tag">${t}</span>`).join('')}</div></td>
                                        <td style="font-size:0.82rem;">${s.projects.join(', ')}</td>
                                        <td style="font-size:0.82rem; white-space:nowrap;">${s.duration}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                        ${r.roadmap.stages.some(s => s.certs && s.certs.length) ? `
                            <div style="margin-top:var(--space-md);">
                                <div style="font-size:0.82rem; font-weight:600; color:var(--text-muted); margin-bottom:6px;">🏅 Recommended Certifications</div>
                                <div class="skills-tags">${r.roadmap.stages.flatMap(s => s.certs || []).map(c => `<span class="badge badge-success" style="text-transform:none;">${c}</span>`).join('')}</div>
                            </div>
                        ` : ''}
                    </div>

                    <!-- Skill Gaps Tab -->
                    <div class="tab-content" id="gaps-${idx}">
                        <div class="skill-gap-bars">
                            ${r.skill_gaps.map(g => {
                                const uPct = (g.user_level / 10) * 100;
                                const rPct = (g.required / 10) * 100;
                                const cls = g.status === 'surplus' ? 'surplus' : (g.status === 'adequate' ? 'adequate' : 'gap-bar');
                                const vc = g.status === 'surplus' ? 'positive' : (g.status === 'adequate' ? 'neutral' : 'negative');
                                const txt = g.status === 'surplus' ? `+${g.surplus}` : (g.status === 'adequate' ? '≈' : `-${g.gap}`);
                                return `
                                    <div class="skill-gap-row">
                                        <span class="skill-gap-name">${g.skill}</span>
                                        <div class="skill-bar-container">
                                            <div class="skill-bar-required" style="width:${rPct}%"></div>
                                            <div class="skill-bar-user ${cls}" style="width:${uPct}%"></div>
                                        </div>
                                        <span class="skill-gap-value ${vc}">${txt}</span>
                                    </div>`;
                            }).join('')}
                        </div>
                        <div style="margin-top:var(--space-md); font-size:0.82rem; color:var(--text-muted);">
                            <em>Bars: colored = your level, faded = required level. Negative values indicate gaps.</em>
                        </div>
                    </div>

                    <!-- Location Tab -->
                    <div class="tab-content" id="location-${idx}">
                        <div class="location-panel">
                            <h4>📍 ${r.location.city || 'Pune'} — Institutions & Opportunities</h4>
                            <ul class="inst-list">
                                ${(r.location.institutions || []).map(inst => `
                                    <li class="inst-item">
                                        <div>
                                            <span class="inst-name">${inst.name}</span>
                                            <span class="inst-focus"> — ${inst.focus}</span>
                                        </div>
                                        <span class="badge badge-primary" style="font-size:0.65rem;">${inst.type}</span>
                                    </li>
                                `).join('')}
                            </ul>
                            ${r.location.career_data ? `
                                <div class="pune-stats">
                                    <div class="pune-stat">
                                        <div class="val gradient-text">${r.location.career_data.jobs_per_year || '—'}+</div>
                                        <div class="lbl">Jobs/Year in Pune</div>
                                    </div>
                                    <div class="pune-stat">
                                        <div class="val" style="color:var(--accent-success)">${r.location.career_data.avg_entry_salary || '—'}</div>
                                        <div class="lbl">Avg Entry Salary</div>
                                    </div>
                                    <div class="pune-stat">
                                        <div class="val" style="color:var(--accent-info)">${(r.location.career_data.companies || []).length}</div>
                                        <div class="lbl">Top Companies</div>
                                    </div>
                                </div>
                                ${(r.location.career_data.companies || []).length ? `
                                    <div style="margin-top:var(--space-md); font-size:0.82rem; color:var(--text-secondary);">
                                        <strong>Key employers:</strong> ${r.location.career_data.companies.join(', ')}
                                    </div>
                                ` : ''}
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>`;
        }).join('');
    }

    window.__toggleDetail = function (id) {
        const d = document.getElementById(id);
        if (d) d.classList.toggle('visible');
    };

    window.__switchTab = function (detailId, tabId, btn) {
        const detail = document.getElementById(detailId);
        if (!detail) return;
        detail.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        detail.querySelectorAll('.detail-tab').forEach(t => t.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        btn.classList.add('active');
    };

    // ── All Scores Chart ──────────────────────
    function renderAllScores(scores) {
        const el = document.getElementById('allScoresChart');
        if (!el) return;
        const max = Math.max(...scores.map(s => s.css));
        el.innerHTML = `<div style="display:flex;flex-direction:column;gap:10px;">
            ${scores.map((s, i) => {
                const w = (s.css / max) * 100;
                const color = i < 3 ? 'var(--gradient-primary)' : (i < 5 ? 'var(--gradient-cool)' : 'linear-gradient(90deg, rgba(255,255,255,0.08), rgba(255,255,255,0.15))');
                const tc = i < 3 ? 'var(--accent-primary)' : (i < 5 ? 'var(--accent-secondary)' : 'var(--text-muted)');
                return `<div style="display:grid;grid-template-columns:200px 1fr 60px;gap:12px;align-items:center;">
                    <span style="font-size:0.84rem;color:${tc};font-weight:${i < 5 ? '600' : '400'};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                        ${i < 3 ? ['🥇','🥈','🥉'][i] : ''} ${s.title}
                    </span>
                    <div style="height:8px;background:rgba(255,255,255,0.04);border-radius:99px;overflow:hidden;">
                        <div style="height:100%;width:${w}%;background:${color};border-radius:99px;transition:width 1.2s ease ${i*0.05}s;"></div>
                    </div>
                    <span style="font-size:0.82rem;color:${tc};font-weight:600;text-align:right;">${s.css}</span>
                </div>`;
            }).join('')}
        </div>`;
    }

    // ── Community ─────────────────────────────
    function renderCommunity(community) {
        const el = document.getElementById('communityGrid');
        if (!el) return;
        const tops = community.top_careers || [];
        el.innerHTML = `
            <div class="community-stat">
                <div class="big-num gradient-text">${community.total_users || 0}</div>
                <div class="stat-desc">Total Assessments</div>
            </div>
            <div class="community-stat">
                <div class="big-num" style="color:var(--accent-secondary);">${tops.length}</div>
                <div class="stat-desc">Trending Careers</div>
            </div>
            <div class="community-stat">
                <div class="big-num" style="color:var(--accent-tertiary);">
                    ${Object.keys(community.stage_distribution || {}).length}
                </div>
                <div class="stat-desc">User Stages Represented</div>
            </div>
            ${tops.length ? `<div style="grid-column:1/-1;margin-top:var(--space-md);">
                <h4 style="font-size:0.9rem;font-weight:600;margin-bottom:var(--space-md);color:var(--text-muted);">Trending Career Recommendations</h4>
                <ul class="popular-careers">
                    ${tops.map((c, i) => {
                        const title = Array.isArray(c) ? c[0].replace(/_/g,' ').replace(/\b\w/g,l=>l.toUpperCase()) : (c.title||c.id);
                        const count = Array.isArray(c) ? c[1] : c.count;
                        return `<li class="popular-career-item">
                            <span style="font-size:0.88rem;font-weight:500;">${['🥇','🥈','🥉','4️⃣','5️⃣'][i]||''} ${title}</span>
                            <span style="font-size:0.8rem;color:var(--text-muted);">${count} rec${count===1?'':'s'}</span>
                        </li>`;
                    }).join('')}
                </ul>
            </div>` : ''}`;
    }

    // ── Metadata ──────────────────────────────
    function renderMeta(meta, profile) {
        const el = document.getElementById('metaFooter');
        if (!el || !meta) return;
        el.innerHTML = `
            <p>Analysis generated at ${new Date(meta.timestamp).toLocaleString()} │ Model v${meta.model_version}</p>
            <p>Scoring: <code style="background:var(--bg-glass);padding:2px 8px;border-radius:4px;font-family:var(--font-mono);font-size:0.78rem;">${meta.scoring_formula}</code></p>
            <p style="margin-top:4px;">Models: ${meta.psychometric_models.join(' │ ')} │ Mode: ${profile.mode} │ Stage: ${profile.stage.replace(/_/g,' ')}</p>
        `;
    }

})();
