/**
 * Data Pipeline Visualizer — Frontend Logic
 *
 * - Node flow animation (sequential highlight through pipeline stages)
 * - Dynamic ETL log stream with timestamps
 * - "New Pipeline" button opens a creation modal
 * - Sidebar job items are clickable (switch active pipeline)
 * - Stats (rows processed, latency) update in real-time
 */

document.addEventListener('DOMContentLoaded', () => {
    const rand = (min, max) => Math.random() * (max - min) + min;

    // ── DOM refs ───────────────────────────────────────────────────────────────
    const nodes       = document.querySelectorAll('.node');
    const terminal    = document.querySelector('.terminal');
    const statCards   = document.querySelectorAll('.stat-card .value');
    const jobItems    = document.querySelectorAll('.job-list li');
    const btnNew      = document.getElementById('btn-new-pipeline');
    const modal       = document.getElementById('pipeline-modal');
    const modalClose  = document.getElementById('pipeline-modal-close');
    const modalCreate = document.getElementById('pipeline-modal-create');
    const pipelineName= document.getElementById('pipeline-name-input');
    const pipelineTitle = document.querySelector('.header-row h1');

    // ── Pipeline names per sidebar item ────────────────────────────────────────
    const PIPELINE_NAMES = [
        'Pipeline: CRM to Data Lake',
        'Pipeline: Sales API Sync',
        'Pipeline: Legacy DB Export',
        'Pipeline: Analytics Aggregation',
    ];

    // ── Sidebar job selection ──────────────────────────────────────────────────
    jobItems.forEach((li, idx) => {
        li.style.cursor = 'pointer';
        li.addEventListener('click', () => {
            jobItems.forEach(j => j.classList.remove('active'));
            li.classList.add('active');
            pipelineTitle.textContent = PIPELINE_NAMES[idx] || 'Pipeline: Unnamed';
            addLog('[INFO] Pipeline switched → ' + PIPELINE_NAMES[idx]);
        });
    });

    // ── State ──────────────────────────────────────────────────────────────────
    let rowsProcessed = 1_400_000;
    let currentNode   = 0;
    const CONSOLE_MAX  = 8;

    // ── Node flow animation ────────────────────────────────────────────────────
    const animateFlow = () => {
        nodes.forEach(n => {
            n.style.boxShadow = 'none';
            n.style.transform = 'scale(1)';
        });

        if (nodes[currentNode]) {
            nodes[currentNode].style.boxShadow = '0 0 22px rgba(56, 189, 248, 0.65)';
            nodes[currentNode].style.transform = 'scale(1.04)';
            nodes[currentNode].style.transition = 'all 0.3s ease';
        }

        currentNode++;
        if (currentNode >= nodes.length) {
            currentNode = 0;
            rowsProcessed += Math.floor(rand(3000, 8000));
            statCards[0].textContent = (rowsProcessed / 1_000_000).toFixed(2) + 'M';
            statCards[1].textContent = Math.floor(rand(35, 65)) + 'ms';
        }
    };

    setInterval(animateFlow, 900);

    // ── Log helpers ────────────────────────────────────────────────────────────
    const addLog = (msg) => {
        const ts  = new Date().toISOString().split('T')[1].substring(0, 8);
        let statusClass = 'info';
        if (msg.includes('[WARN]'))    statusClass = 'warn';
        if (msg.includes('[SUCCESS]')) statusClass = 'success';
        if (msg.includes('[ERROR]'))   statusClass = 'warn';

        const parts = msg.match(/^(\[[A-Z]+\])\s(.+)$/);
        const p = document.createElement('p');
        p.style.animation = 'fadeIn 0.4s ease-in';

        if (parts) {
            p.innerHTML = `<span class="time">${ts}</span> <span class="${statusClass}">${parts[1]}</span> ${parts[2]}`;
        } else {
            p.innerHTML = `<span class="time">${ts}</span> ${msg}`;
        }

        terminal.appendChild(p);
        terminal.scrollTop = terminal.scrollHeight;

        while (terminal.children.length > CONSOLE_MAX) {
            terminal.removeChild(terminal.firstChild);
        }
    };

    const LOG_POOL = [
        '[INFO] Extracted 5,200 records from Salesforce API.',
        '[INFO] Cleaning step: 18 records filtered — missing email.',
        '[WARN] Transformation latency spike: 58ms.',
        '[INFO] Masking PII fields (email, phone, tax_id).',
        '[SUCCESS] Batch written to s3://datalake-prod/crm/',
        '[INFO] Schema validation passed for all 5,200 records.',
        '[INFO] Deduplication complete — 3 duplicates removed.',
        '[INFO] Partition checkpoint created.',
    ];

    setInterval(() => {
        addLog(LOG_POOL[Math.floor(rand(0, LOG_POOL.length))]);
    }, 1600);

    // ── New Pipeline Modal ─────────────────────────────────────────────────────
    btnNew.addEventListener('click', () => {
        modal.style.display = 'flex';
        pipelineName.focus();
    });

    const closeModal = () => { modal.style.display = 'none'; };
    modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });

    modalCreate.addEventListener('click', () => {
        const name = pipelineName.value.trim() || 'New Pipeline';
        // Add to sidebar
        const li = document.createElement('li');
        li.innerHTML = `<span class="status healthy"></span> ${name}`;
        li.style.cursor = 'pointer';
        li.addEventListener('click', () => {
            jobItems.forEach(j => j.classList.remove('active'));
            document.querySelectorAll('.job-list li').forEach(j => j.classList.remove('active'));
            li.classList.add('active');
            pipelineTitle.textContent = 'Pipeline: ' + name;
        });
        document.querySelector('.job-list').appendChild(li);

        pipelineTitle.textContent = 'Pipeline: ' + name;
        addLog(`[SUCCESS] Pipeline "${name}" created and activated.`);
        pipelineName.value = '';
        closeModal();
    });

    // Allow Enter key to create
    pipelineName.addEventListener('keydown', e => {
        if (e.key === 'Enter') modalCreate.click();
    });
});
