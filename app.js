document.addEventListener('DOMContentLoaded', () => {
    const nodes = document.querySelectorAll('.node');
    const terminal = document.querySelector('.terminal');
    const values = document.querySelectorAll('.stat-card .value');
    
    let rowsProcessed = 1400000;
    const formatRows = (num) => (num / 1000000).toFixed(2) + 'M';

    // Simulate flow
    let currentNode = 0;
    const animateFlow = () => {
        // Reset all nodes
        nodes.forEach(n => n.style.boxShadow = 'none');
        
        // Highlight current node
        if (nodes[currentNode]) {
            nodes[currentNode].style.boxShadow = '0 0 20px rgba(56, 189, 248, 0.6)';
            nodes[currentNode].style.transition = 'box-shadow 0.3s ease';
        }

        currentNode++;
        if (currentNode >= nodes.length) {
            currentNode = 0;
            // Update stats when cycle completes
            rowsProcessed += Math.floor(Math.random() * 5000);
            values[0].innerText = formatRows(rowsProcessed);
            values[1].innerText = Math.floor(Math.random() * 20 + 35) + 'ms';
        }
    };

    setInterval(animateFlow, 800);

    // Simulate logs
    const logMessages = [
        "[INFO] Extracted 5000 records from Salesforce.",
        "[INFO] Cleaning step: 20 records filtered out.",
        "[WARN] Transformation latency spike: 52ms.",
        "[INFO] Masking PII fields (email, phone).",
        "[SUCCESS] Batch written to s3://datalake-prod/crm/"
    ];

    const generateLog = () => {
        const msg = logMessages[Math.floor(Math.random() * logMessages.length)];
        let statusClass = 'info';
        if(msg.includes('[WARN]')) statusClass = 'warn';
        if(msg.includes('[SUCCESS]')) statusClass = 'success';

        const p = document.createElement('p');
        const timestamp = new Date().toISOString().split('T')[1].substring(0,8);
        p.innerHTML = `<span class="time">${timestamp}</span> <span class="${statusClass}">${msg.split(' ')[0]}</span> ${msg.substring(msg.indexOf(' ')+1)}`;
        p.style.animation = 'fadeIn 0.5s ease-in';
        
        terminal.appendChild(p);
        
        // Scroll to bottom
        terminal.scrollTop = terminal.scrollHeight;

        if (terminal.children.length > 8) {
            terminal.removeChild(terminal.firstChild);
        }
    };

    setInterval(generateLog, 1500);
});
