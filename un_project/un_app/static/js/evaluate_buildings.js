document.addEventListener('DOMContentLoaded', function() {
    const denominationValues = JSON.parse(document.getElementById('denomination_values').textContent);

    // Function to format numbers to up to 3 decimal places and remove trailing zeros
    function formatNumber(value) {
        // Convert the value to a float, then format to 3 decimal places and remove trailing zeros
        return parseFloat(value).toFixed(3).replace(/\.?0+$/, '');
    }

    // Function to update total diamond value
    function updateTotal() {
        let total = 0;
        for (const [key, value] of Object.entries(denominationValues)) {
            const quantityElement = document.getElementById(key);
            const quantity = parseFloat(quantityElement.value) || 0;
            const diamondEquivalent = parseFloat(value);

            total += quantity * diamondEquivalent;
        }

        // Update the displayed total with formatted value
        document.getElementById('total_diamond_value').textContent = formatNumber(total);
    }

    // Attach updateTotal to all input fields
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', updateTotal);
    });
});
