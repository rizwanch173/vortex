(function($) {
    'use strict';

    console.log('Invoice autocalculate script loaded');

    // Make calculateSubtotal globally accessible
    window.calculateSubtotal = function() {
        console.log('calculateSubtotal called');
        var subtotalField = $('#id_subtotal');
        if (!subtotalField.length) {
            console.log('Subtotal field not found');
            return;
        }

        // Find the selected applications (filter_horizontal widget)
        var selectedApplicationsSelect = $('#id_visa_applications_to');
        var selectedIds = [];

        if (selectedApplicationsSelect.length) {
            console.log('Found filter_horizontal widget');
            // Get selected IDs from the "to" select (filter_horizontal)
            selectedApplicationsSelect.find('option').each(function() {
                var val = $(this).val();
                if (val) {
                    selectedIds.push(val);
                }
            });
            console.log('Selected IDs:', selectedIds);
        } else {
            // Fallback: regular select multiple
            var visaApplicationsMultiple = $('#id_visa_applications');
            if (visaApplicationsMultiple.length && visaApplicationsMultiple.is('select')) {
                console.log('Found regular select multiple');
                selectedIds = visaApplicationsMultiple.val() || [];
            } else {
                console.log('No visa applications field found');
                return;
            }
        }

        if (selectedIds.length === 0) {
            console.log('No applications selected, setting subtotal to 0.00');
            subtotalField.val('0.00');
            return;
        }

        // Use absolute URL for AJAX endpoint
        var ajaxUrl = '/admin/core/invoice/get-visa-prices/';
        console.log('Making AJAX request to:', ajaxUrl, 'with IDs:', selectedIds);

        // Make AJAX request to get prices
        $.ajax({
            url: ajaxUrl,
            type: 'GET',
            data: {
                'visa_applications[]': selectedIds
            },
            beforeSend: function(xhr, settings) {
                // Add CSRF token
                var csrftoken = $('[name=csrfmiddlewaretoken]').val() ||
                               $('input[name="csrfmiddlewaretoken"]').val() ||
                               $.cookie('csrftoken');
                if (csrftoken) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function(response) {
                console.log('AJAX success, response:', response);
                if (response.total !== undefined) {
                    // Remove readonly attribute temporarily to update value
                    var wasReadonly = subtotalField.prop('readonly');
                    subtotalField.prop('readonly', false);
                    subtotalField.val(response.total.toFixed(2));
                    if (wasReadonly) {
                        subtotalField.prop('readonly', true);
                    }
                    subtotalField.trigger('change');
                    console.log('Subtotal updated to:', response.total);
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error calculating subtotal:', error);
                console.error('Status:', status);
                console.error('Response:', xhr.responseText);
            }
        });
    };

    // Wait for DOM and Django admin to be ready
    $(document).ready(function() {
        console.log('Document ready, initializing invoice autocalculate');

        // Wait a bit for Django admin to fully load
        setTimeout(function() {
            var subtotalField = $('#id_subtotal');
            if (!subtotalField.length) {
                console.log('Subtotal field not found on page');
                return;
            }
            console.log('Subtotal field found');

            // Find the filter_horizontal widget
            var selectedApplicationsSelect = $('#id_visa_applications_to');
            var fromApplicationsSelect = $('#id_visa_applications_from');

            if (selectedApplicationsSelect.length) {
                console.log('Filter horizontal widget found');

                // Calculate on page load
                setTimeout(calculateSubtotal, 1000);

                // Listen for changes in the select boxes
                selectedApplicationsSelect.on('change', function() {
                    console.log('Selected applications changed');
                    setTimeout(calculateSubtotal, 100);
                });

                fromApplicationsSelect.on('change', function() {
                    console.log('Available applications changed');
                    setTimeout(calculateSubtotal, 100);
                });

                // Use MutationObserver to watch for DOM changes (when items are moved)
                if (typeof MutationObserver !== 'undefined') {
                    var observer = new MutationObserver(function(mutations) {
                        var hasChanges = false;
                        mutations.forEach(function(mutation) {
                            if (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0) {
                                hasChanges = true;
                            }
                        });
                        if (hasChanges) {
                            console.log('DOM mutation detected in select boxes');
                            setTimeout(calculateSubtotal, 100);
                        }
                    });

                    // Observe changes in both select boxes
                    if (selectedApplicationsSelect.length) {
                        observer.observe(selectedApplicationsSelect[0], {
                            childList: true,
                            subtree: true
                        });
                    }
                    if (fromApplicationsSelect.length) {
                        observer.observe(fromApplicationsSelect[0], {
                            childList: true,
                            subtree: true
                        });
                    }
                }

                // Listen for clicks on the specific add/remove buttons by ID
                $('#id_visa_applications_add, #id_visa_applications_remove').on('click', function(e) {
                    console.log('Add/remove button clicked:', this.id);
                    e.stopPropagation();
                    // Wait for Django's filter_horizontal to update the DOM
                    setTimeout(calculateSubtotal, 600);
                });

                // Also use delegated event listener as backup
                $(document).on('click', '#id_visa_applications_add, #id_visa_applications_remove', function(e) {
                    console.log('Delegated: Add/remove button clicked:', this.id);
                    setTimeout(calculateSubtotal, 600);
                });

                // Also listen for clicks on any selector-add/remove buttons (fallback)
                $(document).on('click', 'button.selector-add, button.selector-remove', function(e) {
                    console.log('Generic selector button clicked:', this.id);
                    setTimeout(calculateSubtotal, 600);
                });

                // Also listen for any clicks in the selector area
                $(document).on('click', '.selector, .selector-chosen, .selector-available', function(e) {
                    // Only trigger if clicking on buttons or options, not the select itself
                    if ($(e.target).is('a, button, option')) {
                        console.log('Click in selector area');
                        setTimeout(calculateSubtotal, 300);
                    }
                });

                // Listen for double-clicks on options (another way to move items)
                selectedApplicationsSelect.on('dblclick', 'option', function() {
                    console.log('Double-click on selected option');
                    setTimeout(calculateSubtotal, 200);
                });

                fromApplicationsSelect.on('dblclick', 'option', function() {
                    console.log('Double-click on available option');
                    setTimeout(calculateSubtotal, 200);
                });

                // More frequent periodic check as fallback (every 300ms for very fast updates)
                var lastSelectedIds = '';
                var checkInterval = setInterval(function() {
                    var currentIds = [];
                    selectedApplicationsSelect.find('option').each(function() {
                        var val = $(this).val();
                        if (val) {
                            currentIds.push(val);
                        }
                    });
                    var currentIdsStr = currentIds.sort().join(',');
                    if (currentIdsStr !== lastSelectedIds) {
                        console.log('Periodic check detected change:', lastSelectedIds, '->', currentIdsStr);
                        lastSelectedIds = currentIdsStr;
                        calculateSubtotal();
                    }
                }, 300);

                // Clean up interval when page unloads
                $(window).on('beforeunload', function() {
                    clearInterval(checkInterval);
                });
            } else {
                // Fallback: regular select multiple
                console.log('No filter_horizontal widget, trying regular select');
                var visaApplicationsMultiple = $('#id_visa_applications');
                if (visaApplicationsMultiple.length && visaApplicationsMultiple.is('select')) {
                    console.log('Found regular select multiple');
                    // Calculate on page load
                    setTimeout(calculateSubtotal, 1000);

                    // Listen for changes
                    visaApplicationsMultiple.on('change', function() {
                        console.log('Regular select changed');
                        calculateSubtotal();
                    });
                } else {
                    console.log('No visa applications field found at all');
                }
            }
        }, 500);
    });
})(django.jQuery || jQuery);
