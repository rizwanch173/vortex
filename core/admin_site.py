from __future__ import annotations

import json
from decimal import Decimal

from django.db.models import Count, DateTimeField, DecimalField, ExpressionWrapper, F, Sum, Value
from django.db.models.functions import Cast
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
from django.urls import reverse
from unfold.sites import UnfoldAdminSite

from .models import Client, Invoice, Payment, VisaApplication


class DashboardAdminSite(UnfoldAdminSite):
    """
    AdminSite with dashboard metrics for the admin index.
    Field mapping assumptions:
    - Invoice status uses Invoice.status (draft/sent/paid/overdue/cancelled).
    - Revenue received uses Payment.amount minus Payment.discount
      with Payment.payment_status == "received".
    - Visa success uses VisaApplication.decision (approved/rejected) and
      VisaApplication.visa_type == "us" for US metrics.
    - Success rate trend uses VisaApplication.decision_date (if null, excluded).
    """

    site_header = "Vortex Ease"
    site_title = "Vortex Ease"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        today = timezone.now().date()
        start_current = today - timezone.timedelta(days=30)
        start_previous = today - timezone.timedelta(days=60)

        invoice_qs = Invoice.objects.all()
        total_invoices = invoice_qs.count()
        draft_invoices = invoice_qs.filter(status="draft").count()
        paid_invoices = invoice_qs.filter(status="paid").count()
        sent_invoices = invoice_qs.filter(status="sent").count()
        overdue_invoices = invoice_qs.filter(status="overdue").count()
        cancelled_invoices = invoice_qs.filter(status="cancelled").count()
        outstanding_invoices = sent_invoices + overdue_invoices
        partially_paid_invoices = 0  # Not supported by the current model.

        total_invoiced = (
            invoice_qs.exclude(status="cancelled").aggregate(
                total=Coalesce(
                    Sum("total_amount"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )["total"]
            or Decimal("0.00")
        )

        received_expr = ExpressionWrapper(
            F("amount")
            - Coalesce(
                F("discount"),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )

        total_received = (
            Payment.objects.filter(payment_status="received").aggregate(
                total=Coalesce(
                    Sum(received_expr),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )["total"]
            or Decimal("0.00")
        )

        outstanding_amount = max(total_invoiced - total_received, Decimal("0.00"))
        collection_rate = (total_received / total_invoiced * 100) if total_invoiced else 0
        avg_invoice_value = (total_invoiced / total_invoices) if total_invoices else Decimal("0.00")

        received_at_expr = Coalesce(
            Cast("payment_received_date", DateTimeField()),
            "created_at",
            output_field=DateTimeField(),
        )
        recent_received = (
            Payment.objects.filter(payment_status="received")
            .annotate(received_at=received_at_expr)
            .filter(received_at__date__gte=start_current)
            .aggregate(
                total=Coalesce(
                    Sum(received_expr),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )["total"]
            or Decimal("0.00")
        )

        visa_decisions = VisaApplication.objects.filter(
            decision__in=["approved", "rejected"]
        )
        approved_count = visa_decisions.filter(decision="approved").count()
        rejected_count = visa_decisions.filter(decision="rejected").count()
        decided_count = approved_count + rejected_count
        overall_success_rate = (approved_count / decided_count * 100) if decided_count else 0
        overall_reject_rate = (rejected_count / decided_count * 100) if decided_count else 0

        us_decisions = visa_decisions.filter(visa_type="us")
        us_approved = us_decisions.filter(decision="approved").count()
        us_rejected = us_decisions.filter(decision="rejected").count()
        us_decided = us_approved + us_rejected
        us_success_rate = (us_approved / us_decided * 100) if us_decided else 0

        current_period = visa_decisions.filter(decision_date__gte=start_current)
        previous_period = visa_decisions.filter(
            decision_date__gte=start_previous, decision_date__lt=start_current
        )
        current_approved = current_period.filter(decision="approved").count()
        current_rejected = current_period.filter(decision="rejected").count()
        current_total = current_approved + current_rejected
        previous_approved = previous_period.filter(decision="approved").count()
        previous_rejected = previous_period.filter(decision="rejected").count()
        previous_total = previous_approved + previous_rejected

        current_rate = (current_approved / current_total * 100) if current_total else 0
        previous_rate = (previous_approved / previous_total * 100) if previous_total else 0
        success_rate_change = current_rate - previous_rate

        total_clients = Client.objects.count()
        pending_cases = VisaApplication.objects.exclude(stage="decision_received").count()

        top_destinations = (
            VisaApplication.objects.values("visa_type")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        visa_type_labels = dict(Client.VISA_TYPE_CHOICES)
        top_destinations = [
            {
                "label": visa_type_labels.get(item["visa_type"], item["visa_type"]),
                "count": item["count"],
            }
            for item in top_destinations
        ]

        # Revenue trend (last 12 months)
        start_month = (today.replace(day=1) - timezone.timedelta(days=365)).replace(day=1)
        revenue_qs = (
            Payment.objects.filter(payment_status="received")
            .annotate(month=TruncMonth(received_at_expr))
            .filter(month__gte=start_month)
            .values("month")
            .annotate(total=Coalesce(Sum(received_expr), Value(Decimal("0.00"))))
            .order_by("month")
        )
        revenue_by_month = {row["month"].date(): row["total"] for row in revenue_qs if row["month"]}

        months = []
        cursor = start_month
        for _ in range(12):
            months.append(cursor)
            next_month = (cursor.replace(day=28) + timezone.timedelta(days=4)).replace(day=1)
            cursor = next_month

        revenue_labels = [m.strftime("%b %Y") for m in months]
        revenue_values = [
            float(revenue_by_month.get(m, Decimal("0.00"))) for m in months
        ]

        status_labels = ["Draft", "Sent", "Paid", "Overdue", "Cancelled"]
        status_values = [
            draft_invoices,
            sent_invoices,
            paid_invoices,
            overdue_invoices,
            cancelled_invoices,
        ]

        approvals_labels = ["Approved", "Rejected"]
        approvals_values = [approved_count, rejected_count]
        us_approvals_values = [us_approved, us_rejected]

        stage_label_map = dict(VisaApplication.APPLICATION_STAGE_CHOICES)
        stage_counts_qs = (
            VisaApplication.objects.values("stage")
            .annotate(count=Count("id"))
        )
        stage_counts = {row["stage"]: row["count"] for row in stage_counts_qs}
        stage_labels = [
            stage_label_map.get(key, key) for key, _ in VisaApplication.APPLICATION_STAGE_CHOICES
        ]
        stage_values = [
            stage_counts.get(key, 0) for key, _ in VisaApplication.APPLICATION_STAGE_CHOICES
        ]

        visa_type_label_map = dict(Client.VISA_TYPE_CHOICES)
        visa_type_counts_qs = (
            VisaApplication.objects.values("visa_type")
            .annotate(count=Count("id"))
        )
        visa_type_counts = {row["visa_type"]: row["count"] for row in visa_type_counts_qs}
        visa_type_labels = [
            visa_type_label_map.get(key, key) for key, _ in Client.VISA_TYPE_CHOICES
        ]
        visa_type_values = [
            visa_type_counts.get(key, 0) for key, _ in Client.VISA_TYPE_CHOICES
        ]

        payment_method_label_map = dict(Payment.PAYMENT_METHOD_CHOICES)
        payment_method_counts_qs = (
            Payment.objects.values("payment_method")
            .annotate(count=Count("id"))
        )
        payment_method_counts = {
            row["payment_method"]: row["count"] for row in payment_method_counts_qs
        }
        unspecified_methods = (
            payment_method_counts.pop(None, 0) + payment_method_counts.pop("", 0)
        )
        payment_method_labels = [
            payment_method_label_map.get(key, key) for key, _ in Payment.PAYMENT_METHOD_CHOICES
        ]
        payment_method_values = [
            payment_method_counts.get(key, 0) for key, _ in Payment.PAYMENT_METHOD_CHOICES
        ]
        if unspecified_methods:
            payment_method_labels.append("Unspecified")
            payment_method_values.append(unspecified_methods)

        currency_code = "GBP"

        def fmt_currency(value, currency=currency_code):
            value = value or Decimal("0.00")
            return f"{currency} {value:,.2f}"

        visa_changelist = reverse(f"{self.name}:core_visaapplication_changelist")
        invoice_changelist = reverse(f"{self.name}:core_invoice_changelist")

        dashboard_context = {
            "invoice_kpis": [
                {
                    "label": "Total Received",
                    "value": fmt_currency(total_received),
                    "url": "",
                },
                {
                    "label": "Total Invoiced",
                    "value": fmt_currency(total_invoiced),
                    "url": "",
                },
                {
                    "label": "Outstanding",
                    "value": fmt_currency(outstanding_amount),
                    "url": f"{invoice_changelist}?outstanding=yes",
                },
                {
                    "label": "Paid Invoices",
                    "value": f"{paid_invoices:,}",
                    "url": f"{invoice_changelist}?status__exact=paid",
                },
                {
                    "label": "Draft Invoices",
                    "value": f"{draft_invoices:,}",
                    "url": f"{invoice_changelist}?status__exact=draft",
                },
            ],
            "visa_kpis": [
                {"label": "Overall Success", "value": f"{overall_success_rate:.1f}%"},
                {"label": "Rejection Rate", "value": f"{overall_reject_rate:.1f}%"},
                {
                    "label": "Success Rate Change",
                    "value": f"{success_rate_change:+.1f}%",
                },
            ],
            "ops_kpis": [
                {
                    "label": "Pending Cases",
                    "value": f"{pending_cases:,}",
                    "url": f"{visa_changelist}?case_status=pending",
                },
                {"label": "Total Clients", "value": f"{total_clients:,}", "url": ""},
                {
                    "label": "Partially Paid Invoices",
                    "value": f"{partially_paid_invoices:,}",
                    "url": "",
                },
            ],
            "performance_kpis": [
                {
                    "label": "Revenue (30 Days)",
                    "value": fmt_currency(recent_received),
                    "muted": "Payments received",
                },
                {
                    "label": "Collection Rate",
                    "value": f"{collection_rate:.1f}%",
                    "muted": "Received / Invoiced",
                },
                {
                    "label": "Avg Invoice Value",
                    "value": fmt_currency(avg_invoice_value),
                    "muted": "Non-cancelled invoices",
                },
                {
                    "label": "Decisions (30 Days)",
                    "value": f"{current_total:,}",
                    "muted": "Approved + Rejected",
                },
            ],
            "top_destinations": top_destinations,
        }

        chart_payload = {
            "revenue": {"labels": revenue_labels, "data": revenue_values},
            "invoice_status": {"labels": status_labels, "data": status_values},
            "approvals": {"labels": approvals_labels, "data": approvals_values},
            "us_approvals": {"labels": approvals_labels, "data": us_approvals_values},
            "visa_stages": {"labels": stage_labels, "data": stage_values},
            "visa_types": {"labels": visa_type_labels, "data": visa_type_values},
            "payment_methods": {"labels": payment_method_labels, "data": payment_method_values},
            "currency": currency_code,
        }

        extra_context = extra_context or {}
        extra_context.update(
            {
                "dashboard": dashboard_context,
                "chart_data": json.dumps(chart_payload),
                "invoice_counts": {
                    "total": total_invoices,
                    "outstanding": outstanding_invoices,
                    "draft": draft_invoices,
                    "paid": paid_invoices,
                },
            }
        )

        return super().index(request, extra_context=extra_context)


admin_site = DashboardAdminSite(name="dashboard_admin")
