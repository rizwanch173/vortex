/**
 * Date of Birth Picker Enhancement
 * Enables full year selection (from 1900 to current year)
 */
(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const dateOfBirthInput = document.querySelector('[name="date_of_birth"]');

        if (!dateOfBirthInput) return;

        // Set input type to date for native date picker
        dateOfBirthInput.type = 'date';
        dateOfBirthInput.placeholder = 'YYYY-MM-DD';

        // Set reasonable year constraints
        const currentYear = new Date().getFullYear();
        const minYear = 1900;

        dateOfBirthInput.min = `${minYear}-01-01`;
        dateOfBirthInput.max = `${currentYear}-12-31`;

        // Allow manual typing of date in YYYY-MM-DD format
        dateOfBirthInput.addEventListener('input', function(e) {
            // Validate the format if user types manually
            const value = e.target.value;
            if (value && !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
                // Invalid format, but allow user to continue typing
                return;
            }
        });
    });
})();
