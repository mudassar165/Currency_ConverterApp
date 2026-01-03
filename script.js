console.log('Script loaded');

const API = "http://127.0.0.1:5000/api";
let lineChart = null;
let pieChart = null;
let history = [];

// Tab Switching
document.querySelectorAll('.menu-item').forEach(btn => {
    btn.onclick = function() {
        console.log('Tab clicked:', this.getAttribute('data-tab'));
        document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        
        this.classList.add('active');
        const tabId = this.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
        
        if(tabId === 'wallet-tab') loadWalletCharts();
    }
});

const currencyNames = {
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'JPY': 'Japanese Yen',
    'PKR': 'Pakistani Rupee',
    'INR': 'Indian Rupee',
    'CAD': 'Canadian Dollar',
    'AUD': 'Australian Dollar',
    'CHF': 'Swiss Franc',
    'CNY': 'Chinese Yuan',
    // Add more as needed
};

async function init() {
    try {
        console.log('Initializing app...');
        const res = await fetch(`${API}/init-data`);
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        console.log('Data received:', data);
        
        if (data.error) {
            console.error('Backend error:', data.error);
            alert('Error loading data: ' + data.error);
            return;
        }
        
        // Currencies
        const f = document.getElementById('fromCurr');
        const t = document.getElementById('toCurr');
        if (data.currencies) {
            Object.keys(data.currencies).sort().forEach(c => {
                const name = currencyNames[c] || c;
                f.add(new Option(`${c} - ${name}`, c));
                t.add(new Option(`${c} - ${name}`, c));
            });
            f.value = "USD"; 
            t.value = "PKR";
            console.log('Currencies loaded:', Object.keys(data.currencies).length);
        } else {
            console.error('No currencies data');
        }

        // Crypto
        const grid = document.getElementById('crypto-grid');
        if (data.crypto) {
            for(let id in data.crypto) {
                grid.innerHTML += `
                    <div class="glass-card">
                        <h4>${id.toUpperCase()}</h4>
                        <h2>$${data.crypto[id].usd.toLocaleString()}</h2>
                        <p style="color:${data.crypto[id].usd_24h_change > 0 ? '#00ffcc' : '#ff4d4d'}">
                            ${data.crypto[id].usd_24h_change.toFixed(2)}%
                        </p>
                    </div>
                `;
            }
            console.log('Crypto loaded');
        } else {
            console.error('No crypto data');
        }
        
        updateConversion();
    } catch (e) {
        console.error('Init error:', e);
        alert('Failed to load app data. Check console for details.');
    }
}

async function updateConversion() {
    const amt = document.getElementById('amount').value;
    if (!amt || amt <= 0) {
        alert('Please enter a valid amount');
        return;
    }
    
    const loading = document.getElementById('loading');
    loading.style.display = 'block';
    
    try {
        const frm = document.getElementById('fromCurr').value;
        const to = document.getElementById('toCurr').value;

        const res = await fetch(`${API}/convert?amount=${amt}&from=${frm}&to=${to}`);
        const data = await res.json();

        if (data.success) {
            document.getElementById('res-val').innerText = `${data.result.toLocaleString()} ${to}`;
            document.getElementById('res-rate').innerText = `1 ${frm} = ${data.rate} ${to}`;
            
            renderLineChart(data.trend, to);

            // Add to history
            history.unshift(`${amt} ${frm} = ${data.result.toFixed(2)} ${to}`);
            if (history.length > 10) history.pop();
            updateHistory();
        } else {
            alert('Conversion error: ' + data.error);
        }
    } catch (e) {
        alert('Error: ' + e.message);
    } finally {
        loading.style.display = 'none';
    }
}

function renderLineChart(points, label) {
    const ctx = document.getElementById('lineChart').getContext('2d');
    if(lineChart) lineChart.destroy();
    lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [1,2,3,4,5,6,7,8,9,10],
            datasets: [{
                label: `Trend ${label}`,
                data: points,
                borderColor: '#00f2fe',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(0, 242, 254, 0.1)'
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function updateHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = history.map(item => `<li>${item}</li>`).join('');
}

function loadWalletCharts() {
    const ctx = document.getElementById('pieChart').getContext('2d');
    if(pieChart) pieChart.destroy();
    pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['BTC', 'ETH', 'USD', 'PKR'],
            datasets: [{
                data: [40, 20, 30, 10],
                backgroundColor: ['#f3ba2f', '#627eea', '#00f2fe', '#00ffcc'],
                borderWidth: 0
            }]
        },
        options: { cutout: '70%', plugins: { legend: { position: 'bottom', labels: {color: '#fff'} } } }
    });
}

document.getElementById('convertBtn').onclick = updateConversion;

// Swap currencies
document.getElementById('swapBtn').onclick = function() {
    const from = document.getElementById('fromCurr');
    const to = document.getElementById('toCurr');
    const temp = from.value;
    from.value = to.value;
    to.value = temp;
    updateConversion();
};

setInterval(() => { document.getElementById('clock').innerText = new Date().toLocaleTimeString(); }, 1000);

// Calculator Logic
let calcDisplay = document.getElementById('calc-display');
let calcExpression = '';

document.querySelectorAll('.calc-btn').forEach(btn => {
    btn.onclick = function() {
        const value = this.getAttribute('data-value');
        if (value === 'C') {
            calcExpression = '';
            calcDisplay.value = '';
        } else if (value === '=') {
            try {
                calcExpression = eval(calcExpression.replace('^', '**').replace('sqrt', 'Math.sqrt').replace('sin', 'Math.sin').replace('cos', 'Math.cos').replace('tan', 'Math.tan').replace('log', 'Math.log10').replace('ln', 'Math.log').replace('pi', 'Math.PI').replace('e', 'Math.E'));
                calcDisplay.value = calcExpression;
            } catch {
                calcDisplay.value = 'Error';
                calcExpression = '';
            }
        } else {
            calcExpression += value;
            calcDisplay.value = calcExpression;
        }
    }
});
init();