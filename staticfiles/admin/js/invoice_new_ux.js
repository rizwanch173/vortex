(function($) {
    'use strict';

    console.log('=== Invoice UX Script Loading ===');

    var selectedApplications = [];
    var availableApplications = [];

    // Get jQuery - try multiple sources
    var $ = null;
    if (typeof django !== 'undefined' && django.jQuery) {
        $ = django.jQuery;
        console.log('Using django.jQuery');
    } else if (typeof jQuery !== 'undefined') {
        $ = jQuery;
        console.log('Using jQuery');
    } else if (typeof window.$ !== 'undefined') {
        $ = window.$;
        console.log('Using window.$');
    } else {
        console.error('jQuery not found!');
        return;
    }

    // Get CSRF token
    function getCSRFToken() {
        return $('[name=csrfmiddlewaretoken]').val() ||
               $('input[name="csrfmiddlewaretoken"]').val() ||
               '';
    }

    // Load available applications for a client
    function loadAvailableApplications(clientId, invoiceId) {
        console.log('=== loadAvailableApplications ===');
        console.log('Client ID:', clientId);
        console.log('Invoice ID:', invoiceId);

        if (!clientId || clientId === '' || clientId === null) {
            console.log('No client ID, clearing dropdown');
            $('#available-applications').html('<option value="">-- Select a client first --</option>');
            $('#available-applications').prop('disabled', true);
            $('#add-application-btn').prop('disabled', true);
            return;
        }

        var url = '/admin/core/invoice/get-available-applications/?client_id=' + encodeURIComponent(clientId);
        if (invoiceId && invoiceId !== 0) {
            url += '&invoice_id=' + encodeURIComponent(invoiceId);
        }

        console.log('AJAX URL:', url);

        // Show loading state
        $('#available-applications').html('<option value="">Loading...</option>').prop('disabled', true);
        $('#applications-error').hide();

        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            beforeSend: function(xhr) {
                var token = getCSRFToken();
                if (token) {
                    xhr.setRequestHeader("X-CSRFToken", token);
                }
            },
            success: function(response) {
                console.log('=== AJAX Success ===');
                console.log('Response:', response);
                
                if (response.error) {
                    console.error('Server error:', response.error);
                    $('#applications-error').text('Error: ' + response.error).show();
                    $('#available-applications').html('<option value="">Error loading applications</option>');
                    return;
                }
                
                availableApplications = response.available_applications || [];
                console.log('Loaded applications:', availableApplications.length);

                // Ensure each app has required properties
                $.each(availableApplications, function(index, app) {
                    app.id = parseInt(app.id);
                    app.price = parseFloat(app.price) || 0;
                    if (!app.display && app.text) {
                        app.display = app.text;
                    }
                    if (!app.display) {
                        app.display = 'Application #' + app.id;
                    }
                });

                updateAvailableDropdown();
            },
            error: function(xhr, status, error) {
                console.error('=== AJAX Error ===');
                console.error('Status:', status);
                console.error('Error:', error);
                console.error('Response:', xhr.responseText);
                console.error('Status Code:', xhr.status);
                
                var errorMsg = 'Error loading applications';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                } else if (xhr.status === 404) {
                    errorMsg = 'Client not found';
                } else if (xhr.status === 403) {
                    errorMsg = 'Permission denied';
                }
                
                $('#applications-error').text(errorMsg).show();
                $('#available-applications').html('<option value="">Error loading applications</option>');
            }
        });
    }

    // Update the available applications dropdown
    function updateAvailableDropdown() {
        console.log('=== updateAvailableDropdown ===');
        console.log('Available apps count:', availableApplications.length);
        
        var select = $('#available-applications');
        select.empty();

        if (availableApplications.length === 0) {
            select.append('<option value="">No applications available for this client</option>');
            select.prop('disabled', true);
            $('#add-application-btn').prop('disabled', true);
        } else {
            select.prop('disabled', false);
            select.append('<option value="">-- Select an application --</option>');
            $.each(availableApplications, function(index, app) {
                var displayText = app.display || app.text || 'Application #' + app.id;
                var price = parseFloat(app.price) || 0;
                var priceText = price > 0 ? '£' + price.toFixed(2) : 'No price set';
                select.append('<option value="' + app.id + '">' + displayText + ' (' + priceText + ')</option>');
            });
            updateAddButtonState();
        }
    }

    // Update add button state
    function updateAddButtonState() {
        var selectedId = $('#available-applications').val();
        $('#add-application-btn').prop('disabled', !selectedId);
    }

    // Render selected applications table
    function renderSelectedApplications() {
        console.log('=== renderSelectedApplications ===');
        console.log('Selected apps count:', selectedApplications.length);
        
        var container = $('#selected-applications-container');

        if (selectedApplications.length === 0) {
            container.html('<div class="empty-state"><p>No applications selected. Select a client and add applications above.</p></div>');
            updateSubtotal(0);
            return;
        }

        var html = '<table class="applications-table"><thead><tr><th>Application</th><th>Price</th><th>Action</th></tr></thead><tbody>';

        var total = 0;
        $.each(selectedApplications, function(index, app) {
            var price = parseFloat(app.price) || 0;
            total += price;
            var displayText = app.display || app.text || 'Application #' + app.id;
            var priceText = price > 0 ? '£' + price.toFixed(2) : '<span style="color: #dc3545;">⚠️ No price</span>';
            
            html += '<tr data-app-id="' + app.id + '">';
            html += '<td>' + displayText + '</td>';
            html += '<td>' + priceText + '</td>';
            html += '<td><button type="button" class="remove-btn" data-app-id="' + app.id + '">Remove</button></td>';
            html += '</tr>';
        });

        html += '</tbody></table>';
        container.html(html);

        updateSubtotal(total);
    }

    // Update subtotal
    function updateSubtotal(amount) {
        var total = parseFloat(amount) || 0;
        
        $('#subtotal-display').text(total.toFixed(2));
        
        var subtotalField = $('#id_subtotal');
        if (subtotalField.length) {
            var wasReadonly = subtotalField.prop('readonly');
            subtotalField.prop('readonly', false);
            subtotalField.val(total.toFixed(2));
            if (wasReadonly) {
                subtotalField.prop('readonly', true);
            }
        }
        
        updateSelectedApplicationsField();
    }

    // Update hidden field
    function updateSelectedApplicationsField() {
        var hiddenField = $('#selected-applications-data');
        if (hiddenField.length) {
            hiddenField.val(JSON.stringify(selectedApplications));
        }
    }

    // Add application
    function addApplication(visaAppId) {
        console.log('=== addApplication ===');
        console.log('Application ID:', visaAppId);
        
        var invoiceId = window.INVOICE_ID || null;

        // Check for duplicates
        var alreadySelected = selectedApplications.some(function(app) {
            return parseInt(app.id) === parseInt(visaAppId);
        });
        
        if (alreadySelected) {
            $('#applications-error').text('This application is already selected').show();
            setTimeout(function() {
                $('#applications-error').fadeOut();
            }, 3000);
            return;
        }

        if (!invoiceId || invoiceId === 0) {
            // For new invoices, add to local array
            var app = availableApplications.find(function(a) { 
                return parseInt(a.id) === parseInt(visaAppId); 
            });
            
            if (app) {
                var appCopy = $.extend({}, app);
                selectedApplications.push(appCopy);
                availableApplications = availableApplications.filter(function(a) { 
                    return parseInt(a.id) !== parseInt(visaAppId); 
                });
                
                updateAvailableDropdown();
                renderSelectedApplications();
                $('#applications-error').hide();
                
                console.log('Application added. Total selected:', selectedApplications.length);
            } else {
                $('#applications-error').text('Application not found').show();
            }
            return;
        }

        // For existing invoices, use AJAX
        $.ajax({
            url: '/admin/core/invoice/' + invoiceId + '/add-application/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ visa_application_id: visaAppId }),
            beforeSend: function(xhr) {
                var token = getCSRFToken();
                if (token) {
                    xhr.setRequestHeader("X-CSRFToken", token);
                }
            },
            success: function(response) {
                console.log('Application added via AJAX:', response);
                if (response.selected_applications) {
                    selectedApplications = response.selected_applications;
                    $.each(selectedApplications, function(i, app) {
                        app.price = parseFloat(app.price) || 0;
                    });
                }
                loadAvailableApplications(window.CLIENT_ID, invoiceId);
                renderSelectedApplications();
                $('#applications-error').hide();
            },
            error: function(xhr, status, error) {
                console.error('Error adding application:', error);
                var errorMsg = 'Error adding application';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                $('#applications-error').text(errorMsg).show();
            }
        });
    }

    // Remove application
    function removeApplication(visaAppId) {
        console.log('=== removeApplication ===');
        console.log('Application ID:', visaAppId);
        
        var invoiceId = window.INVOICE_ID || null;

        if (!invoiceId || invoiceId === 0) {
            // For new invoices, remove from local array
            var app = selectedApplications.find(function(a) { 
                return parseInt(a.id) === parseInt(visaAppId); 
            });
            
            if (app) {
                selectedApplications = selectedApplications.filter(function(a) { 
                    return parseInt(a.id) !== parseInt(visaAppId); 
                });
                availableApplications.push(app);
                updateAvailableDropdown();
                renderSelectedApplications();
            }
            return;
        }

        // For existing invoices, use AJAX
        $.ajax({
            url: '/admin/core/invoice/' + invoiceId + '/remove-application/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ visa_application_id: visaAppId }),
            beforeSend: function(xhr) {
                var token = getCSRFToken();
                if (token) {
                    xhr.setRequestHeader("X-CSRFToken", token);
                }
            },
            success: function(response) {
                console.log('Application removed via AJAX:', response);
                if (response.selected_applications) {
                    selectedApplications = response.selected_applications;
                    $.each(selectedApplications, function(i, app) {
                        app.price = parseFloat(app.price) || 0;
                    });
                }
                loadAvailableApplications(window.CLIENT_ID, invoiceId);
                renderSelectedApplications();
            },
            error: function(xhr, status, error) {
                console.error('Error removing application:', error);
                alert('Error removing application: ' + error);
            }
        });
    }

    // Initialize
    function initialize() {
        console.log('=== Initializing Invoice UX ===');
        console.log('INVOICE_ID:', window.INVOICE_ID);
        console.log('CLIENT_ID:', window.CLIENT_ID);
        console.log('SELECTED_APPLICATIONS:', window.SELECTED_APPLICATIONS);

        // Find client field
        var clientField = $('#id_client');
        if (clientField.length === 0) {
            clientField = $('select[name="client"]');
        }
        if (clientField.length === 0) {
            clientField = $('select[id*="client"]');
        }

        console.log('Client field found:', clientField.length > 0);
        if (clientField.length === 0) {
            console.error('Client field not found!');
            setTimeout(initialize, 500);
            return;
        }

        var invoiceId = window.INVOICE_ID || null;
        var initialClientId = window.CLIENT_ID;

        // Client change handler
        clientField.on('change', function() {
            var clientId = $(this).val();
            console.log('=== Client Changed ===');
            console.log('New Client ID:', clientId);
            
            window.CLIENT_ID = clientId;

            if (!clientId || clientId === '' || clientId === null) {
                $('#available-applications').html('<option value="">-- Select a client first --</option>');
                $('#available-applications').prop('disabled', true);
                $('#add-application-btn').prop('disabled', true);
                selectedApplications = [];
                renderSelectedApplications();
                return;
            }

            if (invoiceId && invoiceId !== 0) {
                if (clientId != initialClientId) {
                    if (confirm('Changing the client will clear all selected applications. Continue?')) {
                        selectedApplications = [];
                        renderSelectedApplications();
                        initialClientId = clientId;
                    } else {
                        $(this).val(initialClientId);
                        return;
                    }
                }
            } else {
                selectedApplications = [];
                renderSelectedApplications();
            }

            loadAvailableApplications(clientId, invoiceId);
        });

        // Load initial data
        var currentClientValue = clientField.val();
        if (currentClientValue) {
            console.log('Client already selected:', currentClientValue);
            window.CLIENT_ID = currentClientValue;
            loadAvailableApplications(currentClientValue, invoiceId);
        } else if (initialClientId) {
            console.log('Loading from window.CLIENT_ID:', initialClientId);
            loadAvailableApplications(initialClientId, invoiceId);
        }

        // Load existing selected applications for edit mode
        if (invoiceId && invoiceId !== 0 && window.SELECTED_APPLICATIONS) {
            try {
                var parsed = typeof window.SELECTED_APPLICATIONS === 'string'
                    ? JSON.parse(window.SELECTED_APPLICATIONS)
                    : window.SELECTED_APPLICATIONS;
                selectedApplications = parsed || [];
                $.each(selectedApplications, function(i, app) {
                    app.price = parseFloat(app.price) || 0;
                });
                console.log('Loaded existing selected applications:', selectedApplications.length);
                renderSelectedApplications();
            } catch (e) {
                console.error('Error parsing selected applications:', e);
            }
        } else {
            renderSelectedApplications();
        }

        // Add button handler
        $('#add-application-btn').on('click', function() {
            var selectedId = $('#available-applications').val();
            if (selectedId) {
                addApplication(selectedId);
                $('#available-applications').val('');
                updateAddButtonState();
            } else {
                $('#applications-error').text('Please select an application first').show();
                setTimeout(function() {
                    $('#applications-error').fadeOut();
                }, 2000);
            }
        });

        // Dropdown change handler
        $('#available-applications').on('change', function() {
            updateAddButtonState();
        });

        // Remove button handler (delegated)
        $(document).on('click', '.remove-btn', function() {
            var appId = $(this).data('app-id');
            removeApplication(appId);
        });

        // Form submit handler
        $('form').on('submit', function() {
            updateSelectedApplicationsField();
            console.log('Form submitting with', selectedApplications.length, 'applications');
        });

        updateAddButtonState();
        console.log('=== Initialization Complete ===');
    }

    // Start initialization
    $(document).ready(function() {
        initialize();
    });

})(django.jQuery || jQuery || window.$);
