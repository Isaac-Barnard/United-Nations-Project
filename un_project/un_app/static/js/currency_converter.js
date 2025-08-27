document.addEventListener('DOMContentLoaded', function () {
    const denominationValues = JSON.parse(document.getElementById('denomination_values').textContent);
    const baseCurrencySelect = document.getElementById('base_currency');
    const baseCurrencyLabel = document.getElementById('base_currency_label');
    const totalConvertedElement = document.getElementById('total_converted_value');

    function formatNumber(value) {
        return parseFloat(value).toFixed(3).replace(/\.?0+$/, '');
    }

    function updateTotal() {
        let totalDiamonds = 0;

        // Sum everything in diamonds
        for (const [key, value] of Object.entries(denominationValues)) {
            const quantityElement = document.getElementById(key);
            const quantity = parseFloat(quantityElement.value) || 0;
            const diamondEquivalent = parseFloat(value);

            totalDiamonds += quantity * diamondEquivalent;
        }

        // Get selected base currency conversion factor
        const selectedOption = baseCurrencySelect.options[baseCurrencySelect.selectedIndex];
        const baseEquiv = parseFloat(selectedOption.dataset.equivalent);
        const baseName = selectedOption.textContent;

        baseCurrencyLabel.textContent = baseName;

        // Convert diamonds → base currency
        const totalInBase = totalDiamonds / baseEquiv;

        // Display
        totalConvertedElement.textContent = formatNumber(totalInBase);
    }

    // Attach updateTotal to all denomination inputs and the dropdown
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', updateTotal);
    });
    baseCurrencySelect.addEventListener('change', updateTotal);

    // Initialize
    updateTotal();
});
