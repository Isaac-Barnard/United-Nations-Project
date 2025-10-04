document.addEventListener("DOMContentLoaded", () => {
    const sumModeToggle = document.getElementById("sumModeToggle");
    const totalDisplay = document.querySelector(".total-items-value");

    // === Equivalent to Django’s |custom_decimal_places filter ===
    function customDecimalPlaces(value) {
        if (value === null || value === undefined || isNaN(value)) return '';
        if (value === 0) return '0';
        if (value % 1 !== 0) {
            return value.toFixed(3); // non-integers: 3 decimal places
        } else {
            return value.toFixed(1); // integers: 1 decimal place
        }
    }

    // === Parse input like “2s”, “3b”, “v”, etc. ===
    function parseInput(value) {
        if (!value) return 0;
        const match = value.match(/^(\d+)?([sbvc])?$/i);
        if (!match) return parseFloat(value) || 0;
        const num = parseInt(match[1]) || 1;
        const unit = match[2]?.toLowerCase();
        const map = { s: 64, b: 9, v: 576, c: 16 };
        return num * (map[unit] || 1);
    }

    // === Recalculate totals ===
    function updateTotals() {
        let grandTotal = 0;
        document.querySelectorAll(".item-row").forEach(row => {
            const marketValue = parseFloat(row.dataset.marketValue) || 0;
            const count = parseFloat(row.querySelector(".current-count").textContent) || 0;
            const totalValue = marketValue * count;
            row.querySelector(".total-value").textContent = customDecimalPlaces(totalValue);
            grandTotal += totalValue;
        });
        totalDisplay.textContent = customDecimalPlaces(grandTotal);
    }

    // === Update when input loses focus ===
    document.querySelectorAll(".item-input").forEach(input => {
        input.addEventListener("blur", e => {
            const row = e.target.closest(".item-row");
            const countCell = row.querySelector(".current-count");
            const newCount = parseInput(e.target.value);
            const oldCount = parseFloat(countCell.textContent) || 0;
            const finalCount = sumModeToggle.checked ? oldCount + newCount : newCount;

            countCell.textContent = customDecimalPlaces(finalCount);
            e.target.value = "";
            updateTotals();
        });
    });
});
