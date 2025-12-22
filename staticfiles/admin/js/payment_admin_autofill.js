// JavaScript to auto-populate payment amount based on selected visa application
// Note: The backend form already auto-populates on page load, this handles dynamic changes
(function($) {
    'use strict';

    // Cache pricing data - fallback defaults (should match Pricing model)
    var pricingData = {
        'schengen': { amount: '125.00', currency: 'GBP' },
        'us': { amount: '150.00', currency: 'GBP' },
        'uk': { amount: '150.00', currency: 'GBP' },
        'au': { amount: '150.00', currency: 'GBP' },
        'nz': { amount: '150.00', currency: 'GBP' }
    };

    function updatePaymentAmount() {
        var visaAppSelect = $('#id_visa_application');
        var amountInput = $('#id_amount');
        var currencySelect = $('#id_currency');

        if (!visaAppSelect.length || !amountInput.length) {
            return;
        }

        var selectedVisaAppId = visaAppSelect.val();
        if (!selectedVisaAppId) {
            return;
        }

        // Make AJAX call to get visa application's visa type
        $.ajax({
            url: '/admin/core/visaapplication/' + selectedVisaAppId + '/change/',
            method: 'GET',
            success: function(data) {
                var $form = $(data);
                var visaTypeValue = $form.find('#id_visa_type').val();

                if (visaTypeValue && pricingData[visaTypeValue]) {
                    var pricing = pricingData[visaTypeValue];
                    var price = pricing.amount;
                    var currency = pricing.currency;

                    // Only auto-fill if amount is empty or was previously auto-filled
                    if (!amountInput.val() || amountInput.data('auto-filled')) {
                        amountInput.val(price);
                        amountInput.data('auto-filled', true);
                    }

                    // Update currency
                    if (currencySelect.length) {
                        currencySelect.val(currency);
                        currencySelect.trigger('change');
                    }
                }
            },
            error: function() {
                console.warn('Could not fetch visa application details to auto-populate amount');
            }
        });
    }

    // Calculate and display final amount after discount
    function updateFinalAmount() {
        var amountInput = $('#id_amount');
        var discountInput = $('#id_discount');
        var currencySelect = $('#id_currency');
        var finalAmountDisplay = $('#final-amount-display');

        if (!amountInput.length) {
            return;
        }

        var amount = parseFloat(amountInput.val()) || 0;
        var discount = parseFloat(discountInput.val()) || 0;
        var currency = currencySelect.val() || 'GBP';
        var finalAmount = Math.max(0, amount - discount);

        // Create or update the final amount display
        if (finalAmountDisplay.length === 0) {
            // Create the display element if it doesn't exist
            var $discountRow = discountInput.closest('.form-row');
            if ($discountRow.length) {
                var $finalAmountRow = $('<div class="form-row"><div class="field-box"><label>Final Amount (After Discount):</label><div id="final-amount-display" style="padding: 0.5rem 0.75rem; background-color: #f0fdf4; border: 1px solid #86efac; border-radius: 0.375rem; font-weight: 600; color: #166534; margin-top: 0.5rem;"></div></div></div>');
                $discountRow.after($finalAmountRow);
            }
        }

        finalAmountDisplay = $('#final-amount-display');
        if (finalAmountDisplay.length) {
            if (discount > 0) {
                finalAmountDisplay.html(
                    '<div style="font-weight: 600; color: #166534;">' + finalAmount.toFixed(2) + ' ' + currency + '</div>' +
                    '<div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem;">' +
                    '(Original: ' + amount.toFixed(2) + ' ' + currency + ' - Discount: ' + discount.toFixed(2) + ' ' + currency + ')' +
                    '</div>'
                );
            } else {
                finalAmountDisplay.html(
                    '<div style="font-weight: 600; color: #374151;">' + finalAmount.toFixed(2) + ' ' + currency + '</div>'
                );
            }
        }
    }

    // Run when document is ready
    $(document).ready(function() {
        // Update payment amount when visa application changes
        $(document).on('change', '#id_visa_application', function() {
            updatePaymentAmount();
            updateFinalAmount();
        });

        // Update final amount when amount or discount changes
        $(document).on('input change', '#id_amount, #id_discount, #id_currency', function() {
            updateFinalAmount();
        });

        // Calculate final amount on initial load
        setTimeout(updateFinalAmount, 500);

        // Mark amount as manually edited if user changes it (so we don't overwrite manual entries)
        $(document).on('input change', '#id_amount', function() {
            var $input = $(this);
            // If user manually changes the amount, remove auto-fill flag
            if ($input.val() && $input.data('auto-filled')) {
                // Check if the value changed from what we set
                var currentValue = $input.val();
                var $visaAppSelect = $('#id_visa_application');
                if ($visaAppSelect.val()) {
                    // User manually edited, so don't auto-update anymore
                    $input.removeData('auto-filled');
                }
            }
        });
    });
})(django.jQuery || jQuery);
