document.addEventListener('DOMContentLoaded', function() {
    const denominationValues = JSON.parse(document.getElementById('denomination_values').textContent);

    // Function to format numbers to up to 3 decimal places and remove trailing zeros
    function formatNumber(value) {
        return parseFloat(value).toFixed(3).replace(/\.?0+$/, '');
    }

    // Function to update total diamond value
    function updateTotal() {
        let total = 0;

        // Loop through denominationValues and calculate total diamond value
        for (const [key, value] of Object.entries(denominationValues)) {
            const quantityElement = document.getElementById(key);
            const quantity = parseFloat(quantityElement.value) || 0;
            const diamondEquivalent = parseFloat(value);

            total += quantity * diamondEquivalent;
        }

        // Update the displayed total with formatted value
        document.getElementById('total_diamond_value').textContent = formatNumber(total);
    }

    // Attach updateTotal function to all input fields
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', updateTotal);
    });

    // Initialize total value on page load
    updateTotal();
});
