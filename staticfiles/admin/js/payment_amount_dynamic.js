// JavaScript to dynamically update payment amount dropdown based on visa type
(function($) {
    'use strict';

    // Cache pricing data from the page (if available) or use defaults
    var pricingData = null;

    function loadPricingData() {
        // Try to get pricing from a data attribute or use defaults
        var $pricingData = $('#pricing-data');
        if ($pricingData.length) {
            try {
                pricingData = JSON.parse($pricingData.text());
            } catch (e) {
                console.warn('Could not parse pricing data');
            }
        }

        // Fallback to default pricing
        if (!pricingData) {
            pricingData = {
                'schengen': { amount: '125.00', currency: 'GBP' },
                'us': { amount: '150.00', currency: 'GBP' },
                'uk': { amount: '150.00', currency: 'GBP' },
                'au': { amount: '150.00', currency: 'GBP' },
                'nz': { amount: '150.00', currency: 'GBP' }
            };
        }
    }

    function updatePaymentAmountFields() {
        // Get the selected visa type from the main form
        var visaTypeSelect = $('#id_visa_type');
        if (!visaTypeSelect.length) {
            return;
        }

        var selectedVisaType = visaTypeSelect.val();
        if (!selectedVisaType) {
            return;
        }

        // Get pricing for selected visa type
        var pricing = pricingData[selectedVisaType] || { amount: '150.00', currency: 'GBP' };
        var price = pricing.amount;
        var currency = pricing.currency;

        // Find all payment amount input fields in inline forms (now readonly input, not dropdown)
        $('.inline-group .stacked input[name*="amount"]').each(function() {
            var $amountInput = $(this);

            // Update the readonly input value
            $amountInput.val(price);

            // Find and update currency field
            // Currency is in the same row (two-column layout) - look for it in the payment inline
            var $inlineRelated = $amountInput.closest('.inline-related');
            var $currencySelect = $inlineRelated.find('select[name*="currency"]').first();

            if ($currencySelect && $currencySelect.length) {
                $currencySelect.val(currency);
                $currencySelect.trigger('change');
            }

            // Trigger change event to ensure form validation
            $amountInput.trigger('change');
        });
    }

    // Run when document is ready
    $(document).ready(function() {
        // Load pricing data
        loadPricingData();

        // Update payment amount fields when visa type changes
        $(document).on('change', '#id_visa_type', function() {
            setTimeout(updatePaymentAmountFields, 100);
        });

        // Also update on initial load if visa type is already selected
        setTimeout(updatePaymentAmountFields, 500);

        // Update when new payment inline is added
        if (typeof django !== 'undefined' && django.jQuery) {
            django.jQuery(document).on('formset:added', function() {
                setTimeout(updatePaymentAmountFields, 200);
            });
        }
    });
})(django.jQuery || jQuery);
