// Tab Navigation
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.getAttribute('data-tab');
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked button
    event.target.classList.add('active');
}

// ====== SINGLE PATIENT TAB ======

function searchPatient() {
    const patientId = document.getElementById('patient-id').value;

    if (!patientId) {
        showError('Please enter a patient ID');
        return;
    }

    hideError();
    hidePatientResult();

    fetch(`/api/ui/patient/${patientId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.message);
                return;
            }

            displayPatientResult(data);
        })
        .catch(error => {
            showError('Failed to fetch patient data: ' + error.message);
            console.error('Error:', error);
        });
}

function displayPatientResult(patient) {
    document.getElementById('result-patient-id').textContent = patient.patient_id;
    document.getElementById('result-age').textContent = patient.age;
    document.getElementById('result-gender').textContent = patient.gender;
    document.getElementById('result-codes-completed').textContent = patient.codes_completed;
    document.getElementById('result-bundle').textContent = patient.bundle || 'No bundle';
    document.getElementById('result-payout').textContent = patient.payout + " tokens";

    // Parse codes and verify bundle
    const completedCodes = parseCodesString(patient.codes_completed);
    const bundleCodes = parseCodesString(patient.bundle || '');

    // Display bundle verification grid
    displayBundleVerification(completedCodes, bundleCodes);

    document.getElementById('patient-result').classList.remove('hidden');
}

function parseCodesString(codesString) {
    if (!codesString || !codesString.trim()) {
        return new Set();
    }
    return new Set(codesString.split(',').map(code => code.trim()).filter(code => code));
}

function displayBundleVerification(completedCodes, bundleCodes) {
    const grid = document.getElementById('bundle-verification-grid');
    const statusDiv = document.getElementById('bundle-match-status');

    grid.innerHTML = '';
    statusDiv.innerHTML = '';

    // If no bundle, show message
    if (bundleCodes.size === 0) {
        statusDiv.innerHTML = '<div class="no-bundle-message">No bundle specified for this patient</div>';
        return;
    }

    // Create grid items for each bundle code
    bundleCodes.forEach(code => {
        const isCompleted = completedCodes.has(code);
        const gridItem = document.createElement('div');
        gridItem.className = `bundle-grid-item ${isCompleted ? 'completed' : 'missing'}`;

        const icon = isCompleted ? '✓' : '✗';
        const status = isCompleted ? 'Completed' : 'Missing';

        gridItem.innerHTML = `
            <div class="code-label">${code}</div>
            <div class="status-icon ${isCompleted ? 'check' : 'x'}">${icon}</div>
            <div class="status-text">${status}</div>
        `;

        grid.appendChild(gridItem);
    });

    // Check if all codes match
    const allMatch = completedCodes.size === bundleCodes.size && 
                     Array.from(bundleCodes).every(code => completedCodes.has(code));

    if (allMatch) {
        statusDiv.innerHTML = '<div class="match-success">✓ Bundle Complete - All codes match!</div>';
    } else {
        const missingCodes = Array.from(bundleCodes).filter(code => !completedCodes.has(code));
        statusDiv.innerHTML = `<div class="match-failure">✗ Bundle Incomplete - Missing ${missingCodes.length} code(s)</div>`;
    }
}

function hidePatientResult() {
    document.getElementById('patient-result').classList.add('hidden');
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    document.getElementById('error-message').classList.add('hidden');
}

// Allow Enter key to search
document.getElementById('patient-id').addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        searchPatient();
    }
});

// ====== ALL PATIENTS TAB ======

function loadAllPatients() {
    hidePatientError();
    document.getElementById('patients-list').classList.add('hidden');

    fetch('/api/ui/all-patients')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showPatientError(data.message);
                return;
            }

            displayAllPatients(data.patients);
        })
        .catch(error => {
            showPatientError('Failed to fetch patients: ' + error.message);
            console.error('Error:', error);
        });
}

function displayAllPatients(patients) {
    const tbody = document.getElementById('patients-tbody');
    tbody.innerHTML = '';

    patients.forEach(patient => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${patient.patient_id}</td>
            <td>${patient.age}</td>
            <td>${patient.gender}</td>
            <td><strong>${patient.payout} tokens </strong></td>
        `;
        tbody.appendChild(row);
    });

    document.getElementById('patients-list').classList.remove('hidden');
}

function showPatientError(message) {
    const errorDiv = document.getElementById('patients-error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hidePatientError() {
    document.getElementById('patients-error').classList.add('hidden');
}

// ====== STATISTICS TAB ======

function loadStatistics() {
    hideStatsError();
    document.getElementById('stats-container').classList.add('hidden');

    fetch('/api/ui/statistics')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showStatsError(data.message);
                return;
            }

            displayStatistics(data);
        })
        .catch(error => {
            showStatsError('Failed to fetch statistics: ' + error.message);
            console.error('Error:', error);
        });
}

function displayStatistics(stats) {
    document.getElementById('stat-total-records').textContent = stats.total_records;
    document.getElementById('stat-total-payout').textContent = stats.total_payout + " tokens";
    document.getElementById('stat-average-payout').textContent = stats.average_payout + " tokens";
    document.getElementById('stat-min-payout').textContent = stats.min_payout + " tokens";
    document.getElementById('stat-max-payout').textContent = stats.max_payout + " tokens";

    document.getElementById('stats-container').classList.remove('hidden');
}

function showStatsError(message) {
    const errorDiv = document.getElementById('stats-error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideStatsError() {
    document.getElementById('stats-error').classList.add('hidden');
}

// ====== MARKETPLACE TAB ======

let currentPatientId = null;
let currentPatientPayout = null;

function loadMarketplaceActivities() {
    const patientId = document.getElementById('marketplace-patient-id').value;

    if (!patientId) {
        showMarketplaceError('Please enter a patient ID');
        return;
    }

    hideMarketplaceError();

    // First, get the patient's current payout
    fetch(`/api/ui/patient/${patientId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showMarketplaceError('Patient not found');
                return;
            }

            currentPatientId = patientId;
            currentPatientPayout = data.payout;

            // Then, fetch available activities through UI server proxy
            console.log('Fetching activities from: /api/ui/marketplace/activities');
            return fetch('/api/ui/marketplace/activities');
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Activities response:', data);
            if (data.error) {
                showMarketplaceError('Failed to load activities: ' + data.message);
                return;
            }

            displayActivities(data.activities);
        })
        .catch(error => {
            console.error('Full error:', error);
            showMarketplaceError('Error loading activities: ' + error.message + '. Make sure the marketplace server is running on port 6000.');
        });
}

function displayActivities(activities) {
    const grid = document.getElementById('activities-grid');
    grid.innerHTML = '';

    activities.forEach(activity => {
        const card = document.createElement('div');
        card.className = 'activity-card';
        card.onclick = () => redeemActivity(activity.id, activity.name, activity.icon);
        
        card.innerHTML = `
            <div class="activity-icon">${activity.icon}</div>
            <div class="activity-name">${activity.name}</div>
            <div class="activity-description">${activity.description}</div>
            <div class="activity-discount">-${activity.discount_amount} tokens from Payout</div>
        `;
        grid.appendChild(card);
    });

    document.getElementById('marketplace-activities').classList.add('show');
    document.getElementById('marketplace-activities').classList.remove('marketplace-hidden');
}

function redeemActivity(activityId, activityName, activityIcon) {
    if (!currentPatientId) {
        showMarketplaceError('Please select a patient first');
        return;
    }

    hideMarketplaceError();

    // POST request through UI server proxy
    fetch(`/api/ui/marketplace/redeem`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            patient_id: parseInt(currentPatientId),
            activity_id: activityId,
            current_payout: currentPatientPayout
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Redeem response:', data);
        if (data["error"]) {
            document.getElementById('marketplace-activities').classList.remove('show');
            document.getElementById('marketplace-activities').classList.add('marketplace-hidden');
            showMarketplaceError('Failed to redeem activity: ' + data["message"]);
            return;
        }

        return fetch(`/api/ui/marketplace/patient/` + currentPatientId+`/coupons/`+ activityId)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Coupon response:', data);
        if (data.error) {
            document.getElementById('marketplace-activities').classList.remove('show');
            document.getElementById('marketplace-activities').classList.add('marketplace-hidden');
            showMarketplaceError('Failed to fetch coupon: ' + data.message);
            return;
        }

        displayCoupon(activityIcon, activityName, data);
    })
    .catch(error => {
        console.error('Redeem error:', error);
        showMarketplaceError('Error redeeming activity: ' + error.message);
    });
}

function displayCoupon(icon, activityName, couponData) {
    console.log('Coupon Data:', couponData);
    
    document.getElementById('coupon-icon').textContent = icon;
    document.getElementById('coupon-activity-name').textContent = activityName;
    document.getElementById('coupon-patient-id').textContent = currentPatientId;
    
    // Set coupon code - use the correct field name
    document.getElementById('coupon-code-value').textContent = couponData['coupon_code'];
    console.log('Set coupon code to:', couponData["coupon_code"]);
    
    document.getElementById('coupon-discount').textContent = `-${couponData["discount_amount"]} tokens`;
    document.getElementById('coupon-original-payout').textContent = `${couponData["original_payout"]} tokens`;
    document.getElementById('coupon-new-payout').textContent = `${couponData["new_payout"]} tokens`;
    
    // Format expires date
    const expiresDate = new Date(couponData["expires_at"]);
    document.getElementById('coupon-expires').textContent = expiresDate.toLocaleDateString();

    // Update current payout for next activity
    currentPatientPayout = couponData["new_payout"];

    // Update the patient's payout in the REST API server
    updatePatientPayoutInServer(parseInt(currentPatientId), currentPatientPayout);

    // Hide activities and show result
    document.getElementById('marketplace-activities').classList.remove('show');
    document.getElementById('marketplace-activities').classList.add('marketplace-hidden');
    document.getElementById('marketplace-result').classList.add('show');
}

function updatePatientPayoutInServer(patientId, newPayout) {
    fetch(`/api/ui/update-patient-payout/${patientId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            payout: newPayout
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Payout updated in server:', data);
    })
    .catch(error => {
        console.error('Error updating payout in server:', error);
    });
}

function copyCouponCode() {
    const couponCode = document.getElementById('coupon-code-value').textContent;
    console.log('Copying coupon code:', couponCode);
    
    navigator.clipboard.writeText(couponCode).then(() => {
        // Show feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

function resetMarketplace() {
    document.getElementById('marketplace-result').classList.remove('show');
    document.getElementById('marketplace-activities').classList.add('show');
    document.getElementById('marketplace-activities').classList.remove('marketplace-hidden');
}

function showMarketplaceError(message) {
    const errorDiv = document.getElementById('marketplace-error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideMarketplaceError() {
    document.getElementById('marketplace-error').classList.add('hidden');
}
