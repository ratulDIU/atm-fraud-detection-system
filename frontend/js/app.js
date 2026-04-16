let transactionCount = 1;
const colors = ['green', 'yellow', 'blue', 'purple', 'pink', 'orange'];

const form = document.getElementById("fraudForm");
const analyzeBtn = document.getElementById("analyzeBtn");
const addTransactionBtn = document.getElementById("addTransactionBtn");
const transactionsContainer = document.getElementById("transactionsContainer");
const errorMessage = document.getElementById("errorMessage");
const errorText = document.getElementById("errorText");
const transactionCountSpan = document.getElementById("transactionCount");

// Create transaction element
function createTransactionElement(index) {
    const color = colors[(index - 1) % colors.length];
    const bgColor = `${color}-50`;
    const borderColor = `${color}-200`;
    const btnColor = `${color}-600`;
    const btnHover = `${color}-700`;

    const transactionDiv = document.createElement('div');
    transactionDiv.id = `transaction-${index}`;
    transactionDiv.className = `bg-${bgColor} rounded-2xl p-6 border-2 border-${borderColor} transition-all duration-300`;
    transactionDiv.innerHTML = `
        <div class="flex items-center justify-between mb-5">
            <h4 class="font-bold text-lg text-gray-800 flex items-center">
                <i data-lucide="credit-card" class="w-5 h-5 mr-2 text-${color}-600"></i>
                Withdrawal #${index}
            </h4>
            ${index > 1 ? `<button type="button" class="remove-transaction px-3 py-1 text-red-600 hover:bg-red-50 rounded-lg transition" data-index="${index}">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>` : ''}
        </div>

        <div class="space-y-4">
            <div>
                <label class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Amount (৳)</label>
                <input type="number" class="amount-input w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-${color}-500 focus:border-transparent transition mt-1 font-semibold"
                       placeholder="Enter amount" data-index="${index}">
            </div>

            <div>
                <label class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Location</label>
                <div class="flex gap-2 mt-1">
                    <input type="text" readonly class="location-input flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                           placeholder="Click Detect to get GPS coordinates" data-index="${index}">
                    <button type="button" class="detect-btn px-4 py-3 bg-${btnColor} hover:bg-${btnHover} text-white font-semibold rounded-lg transition flex items-center space-x-1"
                            data-index="${index}">
                        <i data-lucide="map-pin" class="w-4 h-4"></i>
                        <span>Detect</span>
                    </button>
                </div>
                <div class="location-status text-xs mt-2"></div>
            </div>
        </div>
    `;

    return transactionDiv;
}

// Add transaction
addTransactionBtn.addEventListener('click', (e) => {
    e.preventDefault();
    if (transactionCount < 10) {
        transactionCount++;
        transactionsContainer.appendChild(createTransactionElement(transactionCount));
        transactionCountSpan.textContent = transactionCount;
        attachEventListeners();
        lucide.createIcons();
    }
});

// Attach event listeners
function attachEventListeners() {
    // Detect location buttons - ONLY on click
    document.querySelectorAll('.detect-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const index = btn.dataset.index;
            detectLocation(index);
        });
    });

    // Remove transaction buttons
    document.querySelectorAll('.remove-transaction').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const index = btn.dataset.index;
            const element = document.getElementById(`transaction-${index}`);
            element.style.opacity = '0';
            element.style.transform = 'scale(0.95)';
            setTimeout(() => {
                element.remove();
            }, 300);
        });
    });
}

// Detect location - ONLY when user clicks
function detectLocation(index) {
    const locationInput = document.querySelector(`.location-input[data-index="${index}"]`);
    const statusDiv = document.querySelector(`#transaction-${index} .location-status`);
    
    locationInput.value = "🔍 Detecting...";
    locationInput.style.borderColor = "#999";
    statusDiv.textContent = "Fetching your location...";
    statusDiv.className = "location-status text-xs mt-2 text-gray-600";

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                const accuracy = Math.round(position.coords.accuracy);
                const locationString = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
                
                locationInput.value = locationString;
                locationInput.style.borderColor = "#10b981";
                locationInput.style.backgroundColor = "#ecfdf5";
                
                statusDiv.innerHTML = `✓ Location detected (±${accuracy}m accuracy)`;
                statusDiv.className = "location-status text-xs mt-2 text-green-600 font-medium";
            },
            (error) => {
                let errorMsg = "Unable to get location";
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg = "Location permission denied. Enable it in browser settings.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg = "Location service unavailable";
                        break;
                    case error.TIMEOUT:
                        errorMsg = "Location request timeout";
                        break;
                }
                
                locationInput.value = "❌ " + errorMsg;
                locationInput.style.borderColor = "#ef4444";
                locationInput.style.backgroundColor = "#fef2f2";
                
                statusDiv.innerHTML = `⚠ ${errorMsg}`;
                statusDiv.className = "location-status text-xs mt-2 text-red-600 font-medium";
                
                console.error("Geolocation error:", error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    } else {
        locationInput.value = "❌ Geolocation not supported";
        locationInput.style.borderColor = "#ef4444";
        statusDiv.textContent = "Your browser doesn't support location detection";
        statusDiv.className = "location-status text-xs mt-2 text-red-600";
    }
}

// Show error message
function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
    setTimeout(() => {
        errorMessage.classList.add('hidden');
    }, 5000);
}

// Form submit
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorMessage.classList.add('hidden');

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i data-lucide="loader" class="w-6 h-6 mr-3 animate-spin"></i> Analyzing...';
    lucide.createIcons();

    // Collect transactions
    const transactions = [];
    const amountInputs = document.querySelectorAll('.amount-input');
    
    amountInputs.forEach((amountInput) => {
        const index = amountInput.dataset.index;
        const amount = parseInt(amountInput.value) || 0;
        const location = document.querySelector(`.location-input[data-index="${index}"]`).value.trim();

        if (amount > 0 && location && !location.includes('❌')) {
            transactions.push({
                amount: amount.toString(),
                location: location
            });
        }
    });

    if (transactions.length === 0) {
        showError('Please enter at least one valid withdrawal with amount and location.');
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i data-lucide="search" class="w-6 h-6 mr-3"></i> Analyze & Detect Fraud';
        lucide.createIcons();
        return;
    }

    const timeIntervalValue = document.getElementById("interval").value;
    const timeInterval = timeIntervalValue ? parseInt(timeIntervalValue) : null;

    const data = {
        account: document.getElementById("account").value,
        transactions,
        time_interval: timeInterval
    };

    try {
        const response = await fetch("http://localhost:8000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i data-lucide="search" class="w-6 h-6 mr-3"></i> Analyze & Detect Fraud';
        lucide.createIcons();

        localStorage.setItem("fraudResult", JSON.stringify(result));
        window.location.href = "result.html";
    } catch (error) {
        console.error("Error:", error);
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i data-lucide="search" class="w-6 h-6 mr-3"></i> Analyze & Detect Fraud';
        lucide.createIcons();

        showError("Connection error. Make sure the backend server is running on http://localhost:8000");
    }
});

// Initialize first transaction
transactionsContainer.appendChild(createTransactionElement(1));
attachEventListeners();
lucide.createIcons();
