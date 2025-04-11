// Document ready handler for liquid form submission
document.addEventListener('DOMContentLoaded', function() {
    const liquidForm = document.getElementById('liquidForm');
    
    if (liquidForm) {
        liquidForm.addEventListener('submit', handleLiquidFormSubmit);
    }

    // Initialize selectors and their handlers
    initializeSelectors();
    
    // Initialize item inputs
    initializeItemInputs();
    
    // Initialize denomination inputs
    initializeDenominationInputs();
    
    // Initialize sum mode toggle
    initializeSumModeToggle();
});

// Initialize sum mode toggle
function initializeSumModeToggle() {
    const sumModeToggle = document.getElementById('sumModeToggle');
    if (sumModeToggle) {
        // Set initial state (could be stored in localStorage for persistence)
        window.sumModeEnabled = sumModeToggle.checked;
        
        // Add change event listener
        sumModeToggle.addEventListener('change', function() {
            window.sumModeEnabled = this.checked;
            console.log('Sum mode ' + (window.sumModeEnabled ? 'enabled' : 'disabled'));
        });
    }
}

// Handle item input changes
async function handleItemInputChange() {
    const row = this.closest('.item-row');
    const itemName = row.dataset.itemName;
    const inputValue = parseFloat(this.value) || 0;

    // Use the window.sumModeEnabled variable to check if sum mode is active
    const isSumMode = window.sumModeEnabled;

    // Get the existing count from the row
    let count = inputValue;
    if (isSumMode) {
        const currentCountEl = row.querySelector('.current-count');
        const currentCount = parseFloat(currentCountEl.textContent) || 0;
        count = currentCount + inputValue;
    }

    const nationSelect = document.querySelector('select[name="nation"]');
    const companySelect = document.querySelector('select[name="company"]');
    const formData = new FormData();
    
    formData.append('item_name', itemName);
    formData.append('count', count);
    if (nationSelect.value) formData.append('nation_id', nationSelect.value);
    if (companySelect.value) formData.append('company_id', companySelect.value);
    
    try {
        const response = await fetch('/handle-item-update/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            updateItemRow(row, data);
        } else if (data.status === 'ignored') {
            this.value = '0';
        } else {
            alert('Error updating item: ' + data.message);
            this.value = '0';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error updating item');
        this.value = '0';
    }
}

// Apply the same sum mode logic to denomination input changes
async function handleDenominationInputChange() {
    const containerSelect = document.querySelector('.container-select');
    const container = containerSelect.value;
    
    if (!container) {
        alert('Please select a container first');
        this.value = '0';
        return;
    }

    const denominationId = this.dataset.denominationId;
    const denominationIndex = this.dataset.denominationIndex;
    const inputValue = parseFloat(this.value) || 0;
    
    // Use sum mode for denominations too
    const isSumMode = window.sumModeEnabled;
    
    // Get current count if in sum mode
    let count = inputValue;
    if (isSumMode) {
        const containerRow = document.querySelector(`.container-row[data-container-name="${container}"]`);
        if (containerRow) {
            const denominationCells = containerRow.querySelectorAll('.denomination-count');
            const currentCount = parseFloat(denominationCells[denominationIndex].textContent) || 0;
            count = currentCount + inputValue;
        }
    }
    
    const nationSelect = document.querySelector('select[name="nation"]');
    const companySelect = document.querySelector('select[name="company"]');
    const formData = new FormData();
    
    formData.append('container', container);
    formData.append('denomination_id', denominationId);
    formData.append('count', count);
    if (nationSelect.value) formData.append('nation_id', nationSelect.value);
    if (companySelect.value) formData.append('company_id', companySelect.value);
    
    try {
        const response = await fetch('/handle-liquid-asset-update/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            updateDenominationRow(container, denominationIndex, data);
        } else if (data.status === 'ignored') {
            this.value = '0';
        } else {
            alert('Error updating liquid asset: ' + data.message);
            this.value = '0';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error updating liquid asset');
        this.value = '0';
    }
}

// Liquid form submission handler
function handleLiquidFormSubmit(e) {
    e.preventDefault();
    
    const nationSelect = document.querySelector('select[name="nation"]');
    const companySelect = document.querySelector('select[name="company"]');
    const nationId = nationSelect.value;
    const companyId = companySelect.value;
    
    const formData = new FormData(liquidForm);
    if (nationId) formData.append('nation_id', nationId);
    if (companyId) formData.append('company_id', companyId);
    
    submitLiquidAssetUpdate(formData);
}

// Submit liquid asset update via AJAX
async function submitLiquidAssetUpdate(formData) {
    try {
        const response = await fetch('/handle-liquid-asset-update/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            window.location.reload();
        } else {
            alert('Error updating liquid assets: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error updating liquid assets');
    }
}

// Update total diamonds calculation
function updateTotalDiamonds() {
    let total = 0;
    const inputs = document.querySelectorAll('.input-cell[type="number"]');
    inputs.forEach(input => {
        const value = parseFloat(input.value) || 0;
        const diamondEquivalent = parseFloat(input.dataset.diamondEquivalent);
        total += value * diamondEquivalent;
    });
    document.getElementById('total_diamonds').textContent = total.toFixed(6);
}

// Initialize selectors and their event handlers
function initializeSelectors() {
    const nationSelect = document.querySelector('select[name="nation"]');
    const companySelect = document.querySelector('select[name="company"]');
    const containerSelect = document.querySelector('select[name="container"]');
    const itemSelect = document.querySelector('select[name="item"]');
    const denominationSelect = document.querySelector('select[name="denomination"]');

    // Initialize disabled states
    if (nationSelect.value) {
        companySelect.disabled = true;
    } else if (companySelect.value) {
        nationSelect.disabled = true;
    }

    // Add select change handlers to window object for inline handlers
    window.handleNationChange = function(select) {
        if (select.value) {
            companySelect.value = '';
            companySelect.disabled = true;
            updateContainers('nation', select.value);
            select.form.submit();
        } else {
            companySelect.disabled = false;
        }
    };

    window.handleCompanyChange = function(select) {
        if (select.value) {
            nationSelect.value = '';
            nationSelect.disabled = true;
            updateContainers('company', select.value);
            select.form.submit();
        } else {
            nationSelect.disabled = false;
        }
    };

    // Add item select handler
    if (itemSelect) {
        itemSelect.addEventListener('change', function() {
            if (this.value) {
                containerSelect.value = '';
                denominationSelect.value = '';
                containerSelect.disabled = true;
                denominationSelect.disabled = true;
            } else {
                containerSelect.disabled = false;
                denominationSelect.disabled = false;
            }
        });
    }

    // Add container select handler
    if (containerSelect) {
        containerSelect.addEventListener('change', function() {
            if (this.value) {
                itemSelect.value = '';
                itemSelect.disabled = true;
            } else {
                itemSelect.disabled = false;
            }
        });
    }

    updateTotalDiamonds();
}

// Update containers based on entity selection
async function updateContainers(entityType, entityId) {
    if (!entityId) return;

    try {
        const queryParam = entityType === 'nation' ? `nation_id=${entityId}` : `company_id=${entityId}`;
        const response = await fetch(`/get-containers/?${queryParam}`);
        const data = await response.json();
        
        const containerSelect = document.querySelector('select[name="container"]');
        containerSelect.innerHTML = '<option value="">Select a Container</option>';
        data.containers.forEach(container => {
            containerSelect.innerHTML += `
                <option value="${container.id}">${container.name}</option>
            `;
        });
    } catch (error) {
        console.error('Error updating containers:', error);
    }
}

// Initialize item inputs and their handlers
function initializeItemInputs() {
    const itemInputs = document.querySelectorAll('.item-input');
    
    itemInputs.forEach(input => {
        input.addEventListener('change', handleItemInputChange);
    });
}

// Update item row with new data
function updateItemRow(row, data) {
    row.querySelector('.total-value').textContent = data.new_total_value;
    row.querySelector('.current-count').textContent = data.new_count;
    document.querySelector('.total-items-value').textContent = data.total_items_value;
    row.querySelector('.item-input').value = '0';
}

// Initialize denomination inputs and their handlers
function initializeDenominationInputs() {
    const denominationInputs = document.querySelectorAll('.denomination-input');
    denominationInputs.forEach(input => {
        input.addEventListener('change', handleDenominationInputChange);
    });
}

// Update denomination row with new data
function updateDenominationRow(container, denominationIndex, data) {
    document.getElementById('total_diamonds').textContent = data.new_total_diamonds;
    
    const containerRow = document.querySelector(`.container-row[data-container-name="${container}"]`);
    if (containerRow) {
        containerRow.querySelector('.container-total').textContent = data.new_total_diamonds;
        const denominationCells = containerRow.querySelectorAll('.denomination-count');
        denominationCells[denominationIndex].textContent = data.new_count;
    }
    
    const totalLiquidSpan = document.querySelector('.total-items-value');
    if (totalLiquidSpan) {
        totalLiquidSpan.textContent = data.total_liquid_value;
    }
    
    const input = document.querySelector(`[data-denomination-index="${denominationIndex}"]`);
    if (input) {
        input.value = '0';
    }
}