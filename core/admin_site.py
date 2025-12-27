from __future__ import annotations

import json
from decimal import Decimal

from django.db.models import Count, DateTimeField, DecimalField, ExpressionWrapper, F, Sum, Value
from django.db.models.functions import Cast
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
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

    site_header = "VortexEase Administration"
    site_title = "VortexEase Admin"
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

        active_clients = Client.objects.filter(client_status="new").count()
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
            .annotate(
                month=TruncMonth(
                    Coalesce(
                        Cast("payment_received_date", DateTimeField()),
                        "created_at",
                        output_field=DateTimeField(),
                    )
                )
            )
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

        def fmt_currency(value, currency="GBP"):
            value = value or Decimal("0.00")
            return f"{currency} {value:,.2f}"

        dashboard_context = {
            "kpis": [
                {"label": "Total Invoiced", "value": fmt_currency(total_invoiced)},
                {"label": "Total Received", "value": fmt_currency(total_received)},
                {"label": "Outstanding", "value": fmt_currency(outstanding_amount)},
                {"label": "Paid Invoices", "value": f"{paid_invoices:,}"},
                {"label": "Draft Invoices", "value": f"{draft_invoices:,}"},
            ],
            "visa_kpis": [
                {"label": "Overall Success", "value": f"{overall_success_rate:.1f}%"},
                {"label": "US Success", "value": f"{us_success_rate:.1f}%"},
                {"label": "Rejection Rate", "value": f"{overall_reject_rate:.1f}%"},
                {
                    "label": "Success Rate Change",
                    "value": f"{success_rate_change:+.1f}%",
                },
            ],
            "ops_kpis": [
                {"label": "Active Clients", "value": f"{active_clients:,}"},
                {"label": "Pending Cases", "value": f"{pending_cases:,}"},
                {
                    "label": "Partially Paid Invoices",
                    "value": f"{partially_paid_invoices:,}",
                },
            ],
            "top_destinations": top_destinations,
        }

        chart_payload = {
            "revenue": {"labels": revenue_labels, "data": revenue_values},
            "invoice_status": {"labels": status_labels, "data": status_values},
            "approvals": {"labels": approvals_labels, "data": approvals_values},
            "us_approvals": {"labels": approvals_labels, "data": us_approvals_values},
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
