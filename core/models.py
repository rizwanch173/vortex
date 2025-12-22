from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone
from decimal import Decimal


class Client(models.Model):
    """
    Client model for managing visa application clients.
    """

    CLIENT_STATUS_CHOICES = [
        ("new", "New"),
        ("previous", "Previous"),
    ]

    VISA_TYPE_CHOICES = [
        ("schengen", "Schengen"),
        ("us", "US"),
        ("uk", "UK"),
        ("au", "AU"),
        ("nz", "NZ"),
    ]

    PREFERRED_CONTACT_CHOICES = [
        ("email", "Email"),
        ("phone", "Phone"),
        ("whatsapp", "WhatsApp"),
        ("sms", "SMS"),
    ]

    LEAD_SOURCE_CHOICES = [
        ("website", "Website"),
        ("referral", "Referral"),
        ("social_media", "Social Media"),
        ("advertisement", "Advertisement"),
        ("walk_in", "Walk-in"),
        ("other", "Other"),
    ]

    # Personal Information
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    email = models.EmailField(
        max_length=255,
        validators=[EmailValidator()],
        verbose_name="Email Address",
        unique=True,
    )
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date of Birth"
    )

    # Passport Information
    passport_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Passport Number"
    )
    passport_file = models.FileField(
        upload_to="passports/%Y/%m/%d/",
        null=True,
        blank=True,
        verbose_name="Passport File",
        help_text="Upload passport copy (PDF, JPG, DOCX)"
    )

    # Location Information
    nationality = models.CharField(max_length=100, verbose_name="Nationality")
    country_of_residence = models.CharField(
        max_length=100,
        verbose_name="Country of Residence"
    )

    # Contact Preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=PREFERRED_CONTACT_CHOICES,
        default="email",
        verbose_name="Preferred Contact Method"
    )

    # Lead Information
    lead_source = models.CharField(
        max_length=50,
        choices=LEAD_SOURCE_CHOICES,
        default="website",
        verbose_name="Lead Source"
    )

    # Status
    client_status = models.CharField(
        max_length=20,
        choices=CLIENT_STATUS_CHOICES,
        default="new",
        verbose_name="Client Status"
    )

    # Visa Type/Country
    visa_type = models.CharField(
        max_length=20,
        choices=VISA_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Visa Type",
        help_text="Select the visa type or country"
    )

    # Additional Information
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Additional notes about the client"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["passport_number"]),
            models.Index(fields=["client_status"]),
            models.Index(fields=["visa_type"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        """Return the full name of the client."""
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        """Return the URL to view this client in admin."""
        from django.urls import reverse
        return reverse("admin:core_client_change", args=[self.pk])


class VisaApplication(models.Model):
    """
    Visa Application model to track the lifecycle of visa applications.
    """

    APPLICATION_STAGE_CHOICES = [
        ("initial", "Initial"),
        ("document_collected", "Document Collected"),
        ("payment_requested", "Payment Requested"),
        ("payment_received", "Payment Received"),
        ("appointment_scheduled", "Appointment Scheduled"),
        ("appointment_attended", "Appointment Attended"),
        ("waiting_for_decision", "Waiting for Decision"),
        ("decision_received", "Decision Received"),
    ]

    DECISION_CHOICES = [
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    # Foreign Key to Client
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="visa_applications",
        verbose_name="Client"
    )

    # Visa Information
    visa_type = models.CharField(
        max_length=20,
        choices=Client.VISA_TYPE_CHOICES,
        verbose_name="Visa Type"
    )

    # Application Stage
    stage = models.CharField(
        max_length=30,
        choices=APPLICATION_STAGE_CHOICES,
        default="initial",
        verbose_name="Application Stage"
    )

    # Appointment Information (required when stage is appointment_scheduled)
    appointment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Appointment Date & Time",
        help_text="Required when appointment is scheduled"
    )
    appointment_location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Appointment Location",
        help_text="Embassy/Consulate location"
    )

    # Decision Information
    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        blank=True,
        null=True,
        verbose_name="Decision"
    )
    decision_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Decision Date"
    )
    decision_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Decision Notes"
    )

    # Assigned Agent
    assigned_agent = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Assigned Agent"
    )

    # Additional Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Application Notes"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Visa Application"
        verbose_name_plural = "Visa Applications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["client"]),
            models.Index(fields=["stage"]),
            models.Index(fields=["visa_type"]),
            models.Index(fields=["decision"]),
            models.Index(fields=["appointment_date"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.client.full_name} - {self.get_visa_type_display()} ({self.get_stage_display()})"

    @property
    def get_price(self):
        """Get the price for this visa application."""
        from .models import Pricing
        return Pricing.get_price_for_visa_type(self.visa_type)

    def save(self, *args, **kwargs):
        """Override save to update client status when decision is received."""
        # If decision is received and approved/rejected, move client to "previous"
        if self.stage == "decision_received" and self.decision in ["approved", "rejected"]:
            self.client.client_status = "previous"
            self.client.save()
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Payment model to track payments from clients.
    """

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("requested", "Payment Requested"),
        ("received", "Received"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("bank_transfer", "Bank Transfer"),
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("cash", "Cash"),
        ("online_payment", "Online Payment"),
        ("other", "Other"),
    ]

    DISCOUNT_TYPE_CHOICES = [
        ("referral", "Referral"),
        ("general", "General"),
        ("sale", "Sale"),
    ]

    # Foreign Keys
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Client"
    )
    visa_application = models.ForeignKey(
        VisaApplication,
        on_delete=models.SET_NULL,
        related_name="payments",
        null=True,
        blank=True,
        verbose_name="Visa Application",
        help_text="Optional: Link payment to specific visa application"
    )

    # Payment Information
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Amount"
    )
    currency = models.CharField(
        max_length=3,
        default="GBP",
        verbose_name="Currency",
        help_text="Currency code (e.g., GBP, USD, EUR)"
    )

    # Discount Information
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Discount",
        help_text="Discount amount (in same currency as payment)"
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Discount Type",
        help_text="Type of discount applied"
    )

    # Payment Details
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        verbose_name="Payment Status"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True,
        verbose_name="Payment Method"
    )

    # Payment Dates
    payment_requested_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Payment Requested Date"
    )
    payment_received_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Payment Received Date"
    )

    # Transaction Information
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Transaction ID",
        help_text="Bank transaction ID or reference number"
    )

    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Payment Notes"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["client"]),
            models.Index(fields=["visa_application"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["payment_received_date"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.client.full_name} - {self.amount} {self.currency} ({self.get_payment_status_display()})"

    @property
    def final_amount(self):
        """Calculate final amount after discount."""
        discount = self.discount or Decimal('0.00')
        amount = self.amount or Decimal('0.00')
        return max(Decimal('0.00'), amount - discount)


class Pricing(models.Model):
    """
    Pricing model to manage visa type prices.
    """

    VISA_TYPE_CHOICES = [
        ("schengen", "Schengen"),
        ("us", "US"),
        ("uk", "UK"),
        ("au", "AU"),
        ("nz", "NZ"),
    ]

    CURRENCY_CHOICES = [
        ("GBP", "GBP"),
        ("USD", "USD"),
        ("EUR", "EUR"),
    ]

    visa_type = models.CharField(
        max_length=20,
        choices=VISA_TYPE_CHOICES,
        unique=True,
        verbose_name="Visa Type",
        help_text="Select the visa type for this pricing"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Amount",
        help_text="Price for this visa type"
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="GBP",
        verbose_name="Currency",
        help_text="Currency for this price"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this pricing is currently active"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Pricing"
        verbose_name_plural = "Pricing"
        ordering = ["visa_type"]
        indexes = [
            models.Index(fields=["visa_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.get_visa_type_display()} - {self.amount} {self.currency}"

    @classmethod
    def get_price_for_visa_type(cls, visa_type):
        """Get the active price for a visa type."""
        try:
            pricing = cls.objects.get(visa_type=visa_type, is_active=True)
            return pricing.amount
        except cls.DoesNotExist:
            # Default pricing: Schengen = 125, others = 150
            if visa_type == "schengen":
                return 125.00
            return 150.00


class InvoiceApplication(models.Model):
    """
    Through model for Invoice-VisaApplication relationship.
    Stores the unit price at the time of invoice creation.
    """
    invoice = models.ForeignKey(
        'Invoice',
        on_delete=models.CASCADE,
        related_name="invoice_applications"
    )
    visa_application = models.ForeignKey(
        VisaApplication,
        on_delete=models.CASCADE,
        related_name="invoice_applications"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Unit Price",
        help_text="Price at the time of invoice creation"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Invoice Application"
        verbose_name_plural = "Invoice Applications"
        unique_together = [['invoice', 'visa_application']]
        indexes = [
            models.Index(fields=["invoice"]),
            models.Index(fields=["visa_application"]),
        ]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.visa_application.get_visa_type_display()}"


class Invoice(models.Model):
    """
    Invoice model to manage invoices for clients and visa applications.
    Supports multiple visa applications per invoice.
    """

    INVOICE_STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
    ]

    # Foreign Key to Client
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name="Client"
    )

    # Many-to-Many relationship with Visa Applications (using through model)
    visa_applications = models.ManyToManyField(
        VisaApplication,
        through='InvoiceApplication',
        related_name="invoices",
        verbose_name="Visa Applications",
        help_text="Select one or more visa applications for this invoice"
    )

    # Invoice Information
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Invoice Number",
        help_text="Unique invoice number (e.g., INV-2025-001)"
    )
    invoice_date = models.DateField(
        verbose_name="Invoice Date",
        help_text="Date when invoice was issued"
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Due Date",
        help_text="Payment due date"
    )

    # Financial Information
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Subtotal",
        help_text="Total amount before discount and tax"
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Discount",
        help_text="Discount amount"
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Tax Rate (%)",
        help_text="Tax rate percentage (e.g., 20.00 for 20%)"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Tax Amount",
        help_text="Calculated tax amount"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total Amount",
        help_text="Final amount after discount and tax"
    )
    currency = models.CharField(
        max_length=3,
        default="GBP",
        verbose_name="Currency",
        help_text="Currency code (e.g., GBP, USD, EUR)"
    )

    # Invoice Status
    status = models.CharField(
        max_length=20,
        choices=INVOICE_STATUS_CHOICES,
        default="draft",
        verbose_name="Status"
    )

    # Payment Link
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        related_name="invoice",
        null=True,
        blank=True,
        verbose_name="Payment",
        help_text="Link to payment record (if payment received)"
    )

    # Additional Information
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Additional notes or terms"
    )
    sent_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Sent Date",
        help_text="Date and time when invoice was sent to client"
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Paid Date",
        help_text="Date when invoice was paid"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-invoice_date", "-created_at"]
        indexes = [
            models.Index(fields=["client"]),
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["invoice_date"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.client.full_name} - {self.total_amount} {self.currency}"

    def save(self, *args, **kwargs):
        """Override save to auto-calculate tax and total amounts."""
        # Ensure subtotal and discount have default values
        subtotal = self.subtotal or Decimal('0.00')
        discount = self.discount or Decimal('0.00')
        tax_rate = self.tax_rate or Decimal('0.00')

        # Calculate tax amount
        subtotal_after_discount = subtotal - discount
        self.tax_amount = (subtotal_after_discount * tax_rate) / Decimal('100.00')

        # Calculate total amount
        self.total_amount = subtotal_after_discount + self.tax_amount

        # Auto-generate invoice number if not provided
        if not self.invoice_number:
            from django.utils import timezone
            year = timezone.now().year
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=f"INV-{year}-"
            ).order_by('-invoice_number').first()

            if last_invoice:
                try:
                    last_num = int(last_invoice.invoice_number.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1

            self.invoice_number = f"INV-{year}-{new_num:04d}"

        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculate and update invoice totals based on invoice applications."""
        total = Decimal('0.00')
        # Use unit_price from through model
        for invoice_app in self.invoice_applications.all():
            total += invoice_app.unit_price

        self.subtotal = total
        # Recalculate tax and total (save() will do this, but we need to ensure it happens)
        subtotal = self.subtotal or Decimal('0.00')
        discount = self.discount or Decimal('0.00')
        tax_rate = self.tax_rate or Decimal('0.00')
        subtotal_after_discount = subtotal - discount
        self.tax_amount = (subtotal_after_discount * tax_rate) / Decimal('100.00')
        self.total_amount = subtotal_after_discount + self.tax_amount
        self.save()
