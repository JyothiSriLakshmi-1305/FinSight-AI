// XEPO Chatbot Modal Logic for home.html
const XEPOL_QUESTIONS = [
    {q: 'What is budget?', a: 'A budget is a plan to manage your income and expenses over a period of time. It helps you control spending and save money.'},
    {q: 'What is expense?', a: 'An expense is the money you spend on goods, services, or bills. Tracking expenses helps you stay within your budget.'},
    {q: 'How does BudgetWise help me?', a: 'BudgetWise helps you track your expenses, set budgets, and analyze your spending to improve your financial health.'},
    {q: 'How to add an expense?', a: 'Go to the Expenses tab and use the Add New Expense form to record your spending.'},
    {q: 'How to view reports?', a: 'Go to the Reports tab to see analytics and insights about your spending.'},
    {q: 'How to contact developers?', a: 'Go to the Contact Us section at the bottom of the page.'}
];

function openXepolChatbot() {
    const modal = document.getElementById('xepol-chatbot-modal');
    const body = document.getElementById('xepol-chatbot-body');
    const input = document.getElementById('xepol-chatbot-input');
    const navBtn = document.getElementById('chatbotNavBtn');
    const arrow = document.getElementById('xepol-chatbot-arrow');
    const box = document.getElementById('xepol-chatbot-box');
    modal.classList.add('open');
    if (navBtn) navBtn.classList.add('active');
    // Position arrow below Chatbot tab
    if (navBtn && arrow && box) {
        const navRect = navBtn.getBoundingClientRect();
        const scrollY = window.scrollY || document.documentElement.scrollTop;
        arrow.style.top = (navRect.bottom + scrollY + 2) + 'px';
        arrow.style.left = (navRect.left + navRect.width/2 - 22) + 'px';
        // Position box below arrow
        box.style.top = (navRect.bottom + scrollY + 30) + 'px';
        box.style.left = (navRect.left + navRect.width/2 - box.offsetWidth/2) + 'px';
    }
    body.innerHTML = '';
    setTimeout(() => { input.focus(); }, 200);
    xepolBotGreet();
}

function closeXepolChatbot() {
    document.getElementById('xepol-chatbot-modal').classList.remove('open');
    const navBtn = document.getElementById('chatbotNavBtn');
    if (navBtn) navBtn.classList.remove('active');
}

function xepolBotGreet() {
    xepolAddBotMsg('Hi!');
    xepolAddBotMsg('I am your AI assistant, XepoL.');
    setTimeout(() => xepolAddBotMsg('How can I help you?', XEPOL_QUESTIONS), 400);
}

function xepolAddBotMsg(msg, questions=[]) {
    const chatBody = document.getElementById('xepol-chatbot-body');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'xepol-msg xepol-bot';
    msgDiv.innerHTML = msg;
    chatBody.appendChild(msgDiv);
    if (questions.length) {
        const row = document.createElement('div');
        row.className = 'xepol-questions-row';
        questions.forEach(q => {
            const btn = document.createElement('button');
            btn.className = 'xepol-question-btn';
            btn.textContent = q.q;
            btn.onclick = () => xepolHandleQuestion(q.q);
            row.appendChild(btn);
        });
        chatBody.appendChild(row);
    }
    chatBody.scrollTop = chatBody.scrollHeight;
}

function xepolAddUserMsg(msg) {
    const chatBody = document.getElementById('xepol-chatbot-body');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'xepol-msg xepol-user';
    msgDiv.textContent = msg;
    chatBody.appendChild(msgDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function sendXepolMessage() {
    const input = document.getElementById('xepol-chatbot-input');
    let msg = input.value.trim();
    if (!msg) return;
    xepolAddUserMsg(msg);
    input.value = '';
    setTimeout(() => xepolBotReply(msg), 400);
}

function xepolBotReply(msg) {
    const lower = msg.toLowerCase().replace(/\s|\?/gi,'');
    if (["hello","hi","hii"].includes(lower)) {
        xepolAddBotMsg('Hello, how can I help you?', XEPOL_QUESTIONS);
        return;
    }
    // Check for question match (case-insensitive, ignore spaces and ?)
    let found = null;
    for (const q of XEPOL_QUESTIONS) {
        if (q.q.replace(/\s|\?/gi,'').toLowerCase() === lower) {
            found = q;
            break;
        }
    }
    if (found) {
        xepolAddBotMsg(found.a);
        setTimeout(() => xepolAddBotMsg('Do you want more ideas?', [
            {q:'Yes',a:''},{q:'No',a:''}
        ]), 500);
        return;
    }
    if (["yes"].includes(lower)) {
        xepolAddBotMsg('How can I help you?', XEPOL_QUESTIONS);
        return;
    }
    if (["no"].includes(lower)) {
        xepolAddBotMsg('Thank you for your time.');
        return;
    }
    // Not understood
    xepolAddBotMsg('Sorry! I am unable to answer it. You can ask the below related question:', XEPOL_QUESTIONS);
}

function xepolHandleQuestion(q) {
    xepolAddUserMsg(q);
    setTimeout(() => xepolBotReply(q), 400);
}

document.addEventListener('DOMContentLoaded', function() {
    // ...existing code...
    // Chatbot Nav Button
    const chatbotBtn = document.getElementById('chatbotNavBtn');
    if (chatbotBtn) {
        chatbotBtn.addEventListener('click', openXepolChatbot);
    }
    // Chatbot Close Button
    const chatbotClose = document.getElementById('xepol-chatbot-close');
    if (chatbotClose) {
        chatbotClose.addEventListener('click', closeXepolChatbot);
    }
    // Chatbot Send Button
    const chatbotSend = document.getElementById('xepol-chatbot-send');
    if (chatbotSend) {
        chatbotSend.addEventListener('click', sendXepolMessage);
    }
    // Chatbot Input Enter Key
    const chatbotInput = document.getElementById('xepol-chatbot-input');
    if (chatbotInput) {
        chatbotInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') sendXepolMessage();
        });
    }
});
// XEPO Help Tooltip Logic
function cycleXepoHelpTooltip() {
    const tooltip = document.getElementById('xepo-help-tooltip');
    if (!tooltip) return;
    let visible = false;
    function show() {
        tooltip.classList.add('show');
        visible = true;
        setTimeout(hide, 2500); // Show for 2.5s
    }
    function hide() {
        tooltip.classList.remove('show');
        visible = false;
        setTimeout(show, 6000); // Hide for 6s, then show again
    }
    show();
}

document.addEventListener('DOMContentLoaded', function() {
    // ...existing code...
    if (document.getElementById('xepo-help-tooltip')) {
        cycleXepoHelpTooltip();
    }
});
// XEPO Chatbot Logic
const XEPO_QUESTIONS = [
    {q: 'What is budget?', a: 'A budget is a plan to manage your income and expenses over a period of time. It helps you control spending and save money.'},
    {q: 'What is expense?', a: 'An expense is the money you spend on goods, services, or bills. Tracking expenses helps you stay within your budget.'},
    {q: 'How can I log in ?', a: 'To log in, click the Login button on the top right or visit the /login page and enter your credentials.'},
    {q: 'How can I signUp ?', a: 'To sign up, click the Sign Up button visit signup page and fill in your details.'},
    {q: 'How does BudgetWise help me?', a: 'BudgetWise helps you track your expenses, set budgets, and analyze your spending to improve your financial health.'},
    {q: 'How to add an expense?', a: 'Go to the Expenses page and use the Add New Expense form to record your spending.'},
    {q: 'How to view reports?', a: 'Go to the Reports page to see analytics and insights about your spending.'},
    {q: 'How to Contact to Developers?', a: 'Go to the end of this by scrolling and find the Contact Us section for contact.'}
];

function toggleXepoChat() {
    const chatWindow = document.getElementById('xepo-chat-window');
    chatWindow.classList.toggle('open');
    if (chatWindow.classList.contains('open')) {
        // Always set chat window to full size immediately when opened
        chatWindow.style.width = '340px';
        chatWindow.style.maxHeight = '480px';
        chatWindow.style.height = '480px';
        setTimeout(() => {
            document.getElementById('xepo-chat-input').focus();
        }, 200);
        if (!chatWindow.dataset.initiated) {
            xepoBotGreet();
            chatWindow.dataset.initiated = '1';
        }
    } else {
        // Reset height on close for consistency
        chatWindow.style.height = '';
    }
}

function xepoBotGreet() {
    xepoAddBotMsg('Hello, My name is Xepo; Your AI assistant.');
}

function xepoAddBotMsg(msg, questions=[]) {
    const chatBody = document.getElementById('xepo-chat-body');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'xepo-msg xepo-bot';
    msgDiv.innerHTML = msg;
    chatBody.appendChild(msgDiv);
    if (questions.length) {
        const row = document.createElement('div');
        row.className = 'xepo-questions-row';
        questions.forEach(q => {
            const btn = document.createElement('button');
            btn.className = 'xepo-question-btn';
            btn.textContent = q.q;
            btn.onclick = () => xepoHandleQuestion(q.q);
            row.appendChild(btn);
        });
        chatBody.appendChild(row);
    }
    chatBody.scrollTop = chatBody.scrollHeight;
}

function xepoAddUserMsg(msg) {
    const chatBody = document.getElementById('xepo-chat-body');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'xepo-msg xepo-user';
    msgDiv.textContent = msg;
    chatBody.appendChild(msgDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function sendXepoMessage() {
    const input = document.getElementById('xepo-chat-input');
    let msg = input.value.trim();
    if (!msg) return;
    xepoAddUserMsg(msg);
    input.value = '';
    setTimeout(() => xepoBotReply(msg), 400);
}

function xepoBotReply(msg) {
    const lower = msg.toLowerCase();
    if (["hello","hi","hii"].includes(lower)) {
        xepoAddBotMsg('Hello, How can I help you?', XEPO_QUESTIONS);
        return;
    }
    // Check for question match (case-insensitive, ignore spaces and ?)
    let found = null;
    for (const q of XEPO_QUESTIONS) {
        if (q.q.replace(/\s|\?/gi,'').toLowerCase() === lower.replace(/\s|\?/gi,'').toLowerCase()) {
            found = q;
            break;
        }
    }
    if (found) {
        xepoAddBotMsg(found.a);
        setTimeout(() => xepoAddBotMsg('Do you have more questions?', [
            {q:'Yes',a:''},{q:'No',a:''}
        ]), 500);
        return;
    }
    if (["yes"].includes(lower)) {
        xepoAddBotMsg('Please ask.', XEPO_QUESTIONS);
        return;
    }
    if (["no"].includes(lower)) {
        xepoAddBotMsg('Thank you, Have a nice day.');
        return;
    }
    // Not understood
    xepoAddBotMsg('Sorry, I can not understand your question.', XEPO_QUESTIONS);
}

function xepoHandleQuestion(q) {
    xepoAddUserMsg(q);
    setTimeout(() => xepoBotReply(q), 400);
}
// --- Profile Dropdown Logic ---
function toggleProfileDropdown() {
    const dropdown = document.getElementById('profileDropdown');
    dropdown.classList.toggle('show');
}

// Hide dropdown when clicking outside
document.addEventListener('click', function(event) {
    const profileIcon = document.getElementById('profileIcon');
    const dropdown = document.getElementById('profileDropdown');
    if (!profileIcon.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

// Edit Username (placeholder)
function editUsername() {
    const newName = prompt('Enter new username:');
    if (newName) {
        // You can add AJAX/Flask call here to update username in backend
        alert('Username updated to: ' + newName);
        // Optionally update avatar
        document.querySelector('.profile-icon img').src = `https://ui-avatars.com/api/?name=${encodeURIComponent(newName)}&background=667eea&color=fff&rounded=true`;
    }
}
// --- Logout: Show login page and hide nav/dashboard ---
function logout() {
    // If loginPage exists, show it and hide nav/dashboard
    const loginPage = document.getElementById('loginPage');
    if (loginPage) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
        loginPage.classList.add('active');
        document.getElementById('navBar').classList.remove('show');
    } else {
        // If no login page, reload or redirect to login route
        window.location.href = '/login';
    }
}
// --- User Budget Input Logic ---
document.addEventListener('DOMContentLoaded', function() {
    // ...existing code...
    // User Budget Form logic
    const userBudgetForm = document.getElementById('userBudgetForm');
    if (userBudgetForm) {
        userBudgetForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Get values
            const month = document.getElementById('inputMonth').value || '--';
            const budget = document.getElementById('inputBudget').value || '--';
            const rent = parseInt(document.getElementById('inputRent').value) || 0;
            const grocery = parseInt(document.getElementById('inputGrocery').value) || 0;
            const travel = parseInt(document.getElementById('inputTravel').value) || 0;
            // Output
            document.getElementById('outputMonth').textContent = month;
            document.getElementById('outputBudget').textContent = budget !== '--' ? `₹${parseInt(budget).toLocaleString()}` : '--';
            document.getElementById('outputInitialExpense').textContent = `₹${(rent + grocery + travel).toLocaleString()}`;
        });
    }
});
// BudgetWise Pro - Dashboard Only (No Login)
// All login logic removed. Dashboard is default. Navigation is open.

// Expense data
let expenseData = {
    'Food': 15000,
    'Transport': 8000,
    'Education': 12000,
    'Loans': 20000,
    'Rent': 25000,
    'Entertainment': 5000,
    'Healthcare': 7000,
    'Shopping': 6000
};

const monthlyBudget = 120000;
let barChart, pieChart;

function createParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 50;
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 6 + 's';
        particle.style.animationDuration = (6 + Math.random() * 4) + 's';
        particlesContainer.appendChild(particle);
    }
}

function showPage(pageId) {
    // Hide all pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));
    // Show selected page
    document.getElementById(pageId + 'Page').classList.add('active');
    // Initialize specific page content
    if (pageId === 'reports') {
        setTimeout(() => {
            initCharts();
            updateReportsStats();
        }, 100);
    } else if (pageId === 'expenses') {
        populateExpenseTable();
    } else if (pageId === 'dashboard') {
        updateDashboardStats();
    }
}

function addExpense(event) {
    event.preventDefault();
    const category = document.getElementById('expenseCategory').value;
    const amount = parseInt(document.getElementById('expenseAmount').value);
    if (category && amount > 0) {
        if (expenseData[category]) {
            expenseData[category] += amount;
        } else {
            expenseData[category] = amount;
        }
        const successMsg = document.getElementById('addExpenseSuccess');
        successMsg.textContent = `✅ Expense for ${category} (₹${amount.toLocaleString()}) added successfully!`;
        successMsg.className = 'add-expense-success';
        successMsg.style.display = 'block';
        setTimeout(() => { successMsg.style.display = 'none'; }, 3000);
        document.getElementById('expenseCategory').value = '';
        document.getElementById('expenseAmount').value = '';
        populateExpenseTable();
        updateDashboardStats();
    }
}

function deleteExpenseCategory(category) {
    if (confirm(`Are you sure you want to delete all expenses for ${category}?`)) {
        delete expenseData[category];
        populateExpenseTable();
        updateDashboardStats();
    }
}

function updateDashboardStats() {
    const total = Object.values(expenseData).reduce((a, b) => a + b, 0);
    const categoryCount = Object.keys(expenseData).length;
    const dailyAverage = Math.round(total / 30);
    const remaining = monthlyBudget - total;
    const progressPercentage = Math.min((total / monthlyBudget) * 100, 100);
    document.getElementById('totalExpenses').textContent = `₹${total.toLocaleString()}`;
    document.getElementById('categoryCount').textContent = categoryCount;
    document.getElementById('dailyAverage').textContent = `₹${dailyAverage.toLocaleString()}`;
    document.getElementById('budgetSpent').textContent = total.toLocaleString();
    document.getElementById('budgetTotal').textContent = monthlyBudget.toLocaleString();
    document.getElementById('budgetRemaining').textContent = remaining.toLocaleString();
    document.getElementById('budgetProgress').style.width = `${progressPercentage}%`;
    // Progress bar color
    const progressBar = document.getElementById('budgetProgress');
    if (progressPercentage > 90) {
        progressBar.style.background = 'linear-gradient(135deg, #f44336 0%, #ff5722 100%)';
    } else if (progressPercentage > 75) {
        progressBar.style.background = 'linear-gradient(135deg, #ff9800 0%, #ffc107 100%)';
    } else {
        progressBar.style.background = 'linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)';
    }
}

function updateReportsStats() {
    const total = Object.values(expenseData).reduce((a, b) => a + b, 0);
    const sortedExpenses = Object.entries(expenseData).sort(([,a], [,b]) => b - a);
    const highest = sortedExpenses[0];
    const lowest = sortedExpenses[sortedExpenses.length - 1];
    document.getElementById('reportsTotalExpenses').textContent = `₹${total.toLocaleString()}`;
    document.getElementById('reportsHighestCategory').textContent = `₹${highest[1].toLocaleString()}`;
    document.getElementById('reportsLowestCategory').textContent = `₹${lowest[1].toLocaleString()}`;
    updateInsights();
}

function updateInsights() {
    const total = Object.values(expenseData).reduce((a, b) => a + b, 0);
    const rentPercentage = ((expenseData['Rent'] || 0) / total * 100).toFixed(1);
    const essentialCategories = ['Rent', 'Food', 'Transport'];
    const essentialTotal = essentialCategories.reduce((sum, cat) => sum + (expenseData[cat] || 0), 0);
    const essentialPercentage = ((essentialTotal / total) * 100).toFixed(1);
    const savingAmount = monthlyBudget - total;
    const savingPercentage = ((savingAmount / monthlyBudget) * 100).toFixed(1);
    const insights = [
        `<strong>Rent</strong> takes up ${rentPercentage}% of your total expenses - ${rentPercentage < 30 ? 'within recommended range' : 'consider optimizing'}`,
        `Essential expenses (Rent + Food + Transport) account for ₹${essentialTotal.toLocaleString()} (${essentialPercentage}% of total)`,
        `Your entertainment spending is ${((expenseData['Entertainment'] || 0) / (expenseData['Food'] || 1) * 100).toFixed(0)}% of your food budget`,
        `You're saving ₹${savingAmount.toLocaleString()} monthly which is ${savingPercentage}% of budget - ${savingPercentage > 15 ? 'excellent saving rate!' : 'consider increasing savings'}`
    ];
    document.getElementById('insightsList').innerHTML = insights.map(insight => `<li>${insight}</li>`).join('');
}

function initCharts() {
    const categories = Object.keys(expenseData);
    const amounts = Object.values(expenseData);
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
        '#4ECDC4', '#45B7D1'
    ];
    if (barChart) barChart.destroy();
    if (pieChart) pieChart.destroy();
    const barCtx = document.getElementById('barChart').getContext('2d');
    barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Amount (₹)',
                data: amounts,
                backgroundColor: colors.slice(0, categories.length),
                borderColor: colors.slice(0, categories.length),
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = amounts.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed.y / total) * 100).toFixed(1);
                            return `₹${context.parsed.y.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0, 0, 0, 0.1)' },
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                },
                x: { grid: { display: false } }
            },
            animation: { duration: 2000, easing: 'easeInOutQuart' }
        }
    });
    const pieCtx = document.getElementById('pieChart').getContext('2d');
    pieChart = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: categories,
            datasets: [{
                data: amounts,
                backgroundColor: colors.slice(0, categories.length),
                borderColor: '#fff',
                borderWidth: 3,
                hoverBorderWidth: 5
            }]
        },
        options: {
            responsive: true,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = amounts.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ₹${context.parsed.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: { animateRotate: true, duration: 2000 }
        }
    });
}

function populateExpenseTable() {
    const tbody = document.getElementById('expenseTableBody');
    const total = Object.values(expenseData).reduce((a, b) => a + b, 0);
    let html = '';
    const sortedExpenses = Object.entries(expenseData).sort(([,a], [,b]) => b - a);
    sortedExpenses.forEach(([category, amount]) => {
        const percentage = ((amount / total) * 100).toFixed(1);
        html += `
            <tr>
                <td><span style="font-size:1.2em;font-weight:700;">${getCategoryIcon(category)}</span> <span style="font-weight:600;">${category}</span></td>
                <td style="color:#8e0dde;font-weight:700;">₹${amount.toLocaleString()}</td>
                <td style="color:#39c2fa;font-weight:700;">${percentage}%</td>
                <td>
                    <button onclick="deleteExpenseCategory('${category}')" 
                            class="btn" style="padding: 8px 16px; font-size: 14px; background: linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%);">
                        🗑️ Delete
                    </button>
                </td>
            </tr>
        `;
    });
    html += `
        <tr class="table-total-row">
            <td><strong>TOTAL</strong></td>
            <td><strong>₹${total.toLocaleString()}</strong></td>
            <td><strong>100.0%</strong></td>
            <td>-</td>
        </tr>
    `;
    tbody.innerHTML = html;
}

function getCategoryIcon(category) {
    const icons = {
        'Food': '🍔',
        'Transport': '🚗',
        'Education': '📚',
        'Loans': '🏦',
        'Rent': '🏠',
        'Entertainment': '🎬',
        'Healthcare': '🏥',
        'Shopping': '🛒',
        'Other': '📝'
    };
    return icons[category] || '📝';
}

function downloadCSV() {
    const total = Object.values(expenseData).reduce((a, b) => a + b, 0);
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Category,Amount (₹),Percentage\n";
    Object.entries(expenseData).forEach(([category, amount]) => {
        const percentage = ((amount / total) * 100).toFixed(1);
        csvContent += `${category},${amount},${percentage}%\n`;
    });
    csvContent += `Total,${total},100.0%\n`;
    csvContent += `Budget,${monthlyBudget},-\n`;
    csvContent += `Remaining,${monthlyBudget - total},-\n`;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `budgetwise_report_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function downloadPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const total = Object.values(expenseData).reduce((a, b) => a + b, 0);
    doc.setFontSize(24);
    doc.setFont(undefined, 'bold');
    doc.text('BudgetWise Pro - Expense Report', 20, 30);
    doc.setFontSize(12);
    doc.setFont(undefined, 'normal');
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 45);
    doc.text(`Total Expenses: ₹${total.toLocaleString()}`, 20, 55);
    doc.text(`Monthly Budget: ₹${monthlyBudget.toLocaleString()}`, 20, 65);
    doc.text(`Remaining Budget: ₹${(monthlyBudget - total).toLocaleString()}`, 20, 75);
    doc.setFontSize(16);
    doc.setFont(undefined, 'bold');
    doc.text('Detailed Breakdown:', 20, 95);
    doc.setFontSize(12);
    doc.setFont(undefined, 'normal');
    let yPosition = 110;
    const sortedExpenses = Object.entries(expenseData).sort(([,a], [,b]) => b - a);
    sortedExpenses.forEach(([category, amount]) => {
        const percentage = ((amount / total) * 100).toFixed(1);
        doc.text(`${category}:`, 30, yPosition);
        doc.text(`₹${amount.toLocaleString()} (${percentage}%)`, 100, yPosition);
        yPosition += 12;
    });
    yPosition += 20;
    doc.setFont(undefined, 'bold');
    doc.text('Budget Analysis:', 20, yPosition);
    doc.setFont(undefined, 'normal');
    yPosition += 15;
    const budgetUsed = ((total / monthlyBudget) * 100).toFixed(1);
    doc.text(`Budget Utilization: ${budgetUsed}%`, 30, yPosition);
    yPosition += 12;
    if (budgetUsed > 90) {
        doc.text('Status: High spending - Review expenses', 30, yPosition);
    } else if (budgetUsed > 75) {
        doc.text('Status: Moderate spending - Monitor closely', 30, yPosition);
    } else {
        doc.text('Status: Good spending - Within limits', 30, yPosition);
    }
    doc.save(`budgetwise_report_${new Date().toISOString().split('T')[0]}.pdf`);
}

document.addEventListener('DOMContentLoaded', function() {
    createParticles();
    showPage('dashboard');
    document.getElementById('navBar').classList.add('show');
    populateExpenseTable();
    updateDashboardStats();
});

document.addEventListener('mousemove', function(e) {
    const particles = document.querySelectorAll('.particle');
    const mouseX = e.clientX / window.innerWidth;
    const mouseY = e.clientY / window.innerHeight;
    particles.forEach((particle, index) => {
        const speed = (index % 3 + 1) * 0.5;
        const x = mouseX * speed;
        const y = mouseY * speed;
        particle.style.transform = `translate(${x}px, ${y}px)`;
    });
});
