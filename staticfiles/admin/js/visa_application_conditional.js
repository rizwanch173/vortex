(function($) {
    'use strict';

    function findDecisionFieldset() {
        // Method 1: Find by class (most reliable)
        var decisionFieldset = $('fieldset.decision-info-section');

        // Method 2: Find fieldset containing decision field
        if (decisionFieldset.length === 0) {
            var decisionField = $('#id_decision');
            if (decisionField.length > 0) {
                decisionFieldset = decisionField.closest('fieldset');
            }
        }

        // Method 3: Find by h2/legend text containing "Decision"
        if (decisionFieldset.length === 0) {
            $('fieldset').each(function() {
                var $fieldset = $(this);
                var text = $fieldset.find('h2, .fieldset-title, legend').text().toLowerCase();
                if (text.includes('decision') && $fieldset.find('#id_decision').length > 0) {
                    decisionFieldset = $fieldset;
                    return false; // break
                }
            });
        }

        return decisionFieldset;
    }

    function toggleDecisionSection() {
        var stageValue = $('#id_stage').val();
        var decisionFieldset = findDecisionFieldset();

        // If found, toggle visibility
        if (decisionFieldset.length > 0) {
            if (stageValue === 'decision_received') {
                // Show Decision Information section
                decisionFieldset.css('display', 'block');
                decisionFieldset.show();
                // Make decision fields required
                $('#id_decision').prop('required', true);
                $('#id_decision_date').prop('required', true);
            } else {
                // Hide Decision Information section
                decisionFieldset.css('display', 'none');
                decisionFieldset.hide();
                // Remove required attribute
                $('#id_decision').prop('required', false);
                $('#id_decision_date').prop('required', false);
            }
        }
    }

    // Run when document is ready
    $(document).ready(function() {
        // Try multiple times to ensure form is loaded
        var attempts = 0;
        var maxAttempts = 10;

        function tryToggle() {
            attempts++;
            var decisionFieldset = findDecisionFieldset();

            if (decisionFieldset.length > 0 || attempts >= maxAttempts) {
                toggleDecisionSection();
            } else {
                setTimeout(tryToggle, 200);
            }
        }

        // Start trying after a short delay
        setTimeout(tryToggle, 300);

        // Check when stage dropdown changes
        $(document).on('change', '#id_stage', function() {
            toggleDecisionSection();
        });
    });

    // Also handle dynamic form loading
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function() {
            setTimeout(toggleDecisionSection, 200);
        });
    }
})(django.jQuery || jQuery);
