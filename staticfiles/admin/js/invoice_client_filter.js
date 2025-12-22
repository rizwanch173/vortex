(function($) {
    'use strict';

    console.log('Invoice client filter script loaded');

    function filterVisaApplications() {
        var clientField = $('#id_client');
        var visaApplicationsFrom = $('#id_visa_applications_from');
        var visaApplicationsTo = $('#id_visa_applications_to');

        if (!clientField.length) {
            return;
        }

        var clientId = clientField.val();
        console.log('Client selected:', clientId);

        if (!clientId) {
            // No client selected - clear visa applications
            visaApplicationsFrom.empty();
            visaApplicationsTo.empty();
            console.log('No client selected, cleared visa applications');
            return;
        }

        // Make AJAX request to get visa applications for this client
        $.ajax({
            url: '/admin/core/invoice/get-visa-applications-by-client/',
            type: 'GET',
            data: {
                'client_id': clientId
            },
            beforeSend: function(xhr, settings) {
                var csrftoken = $('[name=csrfmiddlewaretoken]').val() ||
                               $('input[name="csrfmiddlewaretoken"]').val();
                if (csrftoken) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function(response) {
                console.log('Received visa applications:', response);

                // Get currently selected IDs
                var selectedIds = [];
                visaApplicationsTo.find('option').each(function() {
                    selectedIds.push($(this).val());
                });

                // Clear and repopulate the "from" select
                visaApplicationsFrom.empty();
                if (response.visa_applications && response.visa_applications.length > 0) {
                    $.each(response.visa_applications, function(index, app) {
                        var option = $('<option></option>')
                            .attr('value', app.id)
                            .text(app.display);
                        visaApplicationsFrom.append(option);
                    });
                }

                // Keep selected items in "to" select if they're still valid
                visaApplicationsTo.empty();
                if (selectedIds.length > 0 && response.visa_applications) {
                    $.each(response.visa_applications, function(index, app) {
                        if (selectedIds.indexOf(String(app.id)) !== -1) {
                            var option = $('<option></option>')
                                .attr('value', app.id)
                                .text(app.display);
                            visaApplicationsTo.append(option);
                        }
                    });
                }

                // Trigger subtotal calculation after filtering
                setTimeout(function() {
                    if (typeof calculateSubtotal === 'function') {
                        calculateSubtotal();
                    }
                }, 200);
            },
            error: function(xhr, status, error) {
                console.error('Error fetching visa applications:', error);
            }
        });
    }

    $(document).ready(function() {
        var clientField = $('#id_client');
        if (!clientField.length) {
            return;
        }

        // Filter on page load if client is already selected
        setTimeout(filterVisaApplications, 500);

        // Filter when client changes
        clientField.on('change', function() {
            console.log('Client field changed');
            filterVisaApplications();
        });
    });
})(django.jQuery || jQuery);
