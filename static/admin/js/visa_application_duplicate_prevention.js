// Prevent duplicate visa applications by filtering visa type dropdown based on selected client
(function($) {
    'use strict';

    function initializeFiltering() {
        // Only run on add page, not edit page
        var isAddPage = window.location.pathname.indexOf('/add/') !== -1;
        if (!isAddPage) {
            return;
        }

        // Try multiple selectors for the fields
        var $clientField = $('#id_client');
        var $visaTypeField = $('#id_visa_type');

        // If not found, try alternative selectors
        if (!$clientField.length) {
            $clientField = $('select[name="client"]');
        }
        if (!$visaTypeField.length) {
            $visaTypeField = $('select[name="visa_type"]');
        }

        if (!$clientField.length || !$visaTypeField.length) {
            console.log('Visa application duplicate prevention: Fields not found', {
                client: $clientField.length,
                visaType: $visaTypeField.length,
                path: window.location.pathname
            });
            return;
        }

        console.log('Visa application duplicate prevention: Initialized');

        // Store all original visa type choices
        var allVisaTypeChoices = [];
        $visaTypeField.find('option').each(function() {
            var $option = $(this);
            if ($option.val()) {  // Only store non-empty options
                allVisaTypeChoices.push({
                    value: $option.val(),
                    text: $option.text()
                });
            }
        });

        function filterVisaTypes(clientId) {
            if (!clientId) {
                // Reset to all choices if no client selected
                $visaTypeField.empty();
                $visaTypeField.append($('<option>', {
                    value: '',
                    text: '---------'
                }));
                allVisaTypeChoices.forEach(function(choice) {
                    $visaTypeField.append($('<option>', {
                        value: choice.value,
                        text: choice.text
                    }));
                });
                $visaTypeField.val('');
                // Remove help text and error messages
                $visaTypeField.closest('.form-row').find('.duplicate-warning').remove();
                $visaTypeField.closest('.form-row').find('.errorlist').remove();
                $visaTypeField.removeClass('error');
                return;
            }

            // Fetch existing visa applications for this client
            // Use the correct admin URL path
            var currentPath = window.location.pathname;
            var basePath = currentPath.replace('/add/', '').replace('/add', '');
            if (basePath === currentPath) {
                // If we're not on add page, construct from scratch
                basePath = '/admin/core/visaapplication';
            }
            var ajaxUrl = basePath + '/get-existing-visa-types/';

            console.log('Fetching existing visa types for client:', clientId, 'URL:', ajaxUrl);

            $.ajax({
                url: ajaxUrl,
                type: 'GET',
                data: {
                    'client_id': clientId
                },
                dataType: 'json',
                beforeSend: function(xhr, settings) {
                    // Add CSRF token - try multiple ways to find it
                    var csrfToken = null;
                    var $csrfInput = $('[name=csrfmiddlewaretoken]');
                    if ($csrfInput.length) {
                        csrfToken = $csrfInput.val();
                    } else {
                        var csrfCookie = document.cookie.match(/csrftoken=([^;]+)/);
                        if (csrfCookie) {
                            csrfToken = csrfCookie[1];
                        }
                    }
                    if (csrfToken) {
                        xhr.setRequestHeader("X-CSRFToken", csrfToken);
                    }
                },
                success: function(data) {
                    console.log('Received existing visa types:', data);
                    if (data.existing_types) {
                        var existingTypes = data.existing_types;

                        // Store current value before filtering
                        var currentValue = $visaTypeField.val();

                        // Clear current options
                        $visaTypeField.empty();
                        $visaTypeField.append($('<option>', {
                            value: '',
                            text: '---------'
                        }));

                        // Add only available visa types (exclude existing ones)
                        allVisaTypeChoices.forEach(function(choice) {
                            if (existingTypes.indexOf(choice.value) === -1) {
                                $visaTypeField.append($('<option>', {
                                    value: choice.value,
                                    text: choice.text
                                }));
                            }
                        });

                        // Clear selected value if it's now invalid (was in existing types)
                        if (currentValue && existingTypes.indexOf(currentValue) !== -1) {
                            $visaTypeField.val('');
                            // Remove any error messages
                            $visaTypeField.closest('.form-row, .field-box').find('.errorlist').remove();
                            $visaTypeField.removeClass('error');
                        }

                        // Show message if no options available
                        var helpText = $visaTypeField.closest('.form-row, .field-box').find('.duplicate-warning');
                        if ($visaTypeField.find('option').length <= 1) {
                            if (helpText.length === 0) {
                                $visaTypeField.after('<p class="help duplicate-warning" style="color: #dc3545; margin-top: 5px;">This client already has applications for all available visa types.</p>');
                            }
                        } else {
                            helpText.remove();
                        }
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error fetching existing visa types:', status, error);
                    console.error('Response:', xhr.responseText);
                }
            });
        }

        // Filter when client is selected
        $clientField.on('change', function() {
            var clientId = $(this).val();
            console.log('Client changed:', clientId);
            filterVisaTypes(clientId);
        });

        // Filter on page load if client is pre-selected
        if ($clientField.val()) {
            filterVisaTypes($clientField.val());
        }
    }

    // Initialize when document is ready
    $(document).ready(function() {
        // Wait a bit for form to be fully loaded
        setTimeout(function() {
            initializeFiltering();
        }, 500);
    });

    // Also initialize after form validation errors (when page reloads with errors)
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).ready(function() {
            setTimeout(function() {
                initializeFiltering();
            }, 500);
        });
    }
})(django.jQuery || jQuery);
