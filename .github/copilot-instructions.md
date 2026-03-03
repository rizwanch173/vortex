# Vortex Ease — AI Coding Agent Instructions

## Project Overview
Visa consultation CRM platform. A Django 5.2 app with a YAML-driven public website and a full-featured internal admin dashboard built on **django-unfold 0.72**.

---

## Architecture

### Two-Tier Structure
- **Public site** (`core/views.py` + `core/urls.py`): renders YAML config files from `/config/*.yaml` into HTML via Django templates. No database reads for public pages.
- **Admin dashboard** (`/admin/`): custom `DashboardAdminSite` in `core/admin_site.py` — extends `UnfoldAdminSite`. All admin models are registered to this custom site, **not** `django.contrib.admin.site`.

### Key Models (`core/models.py`)
```
Client → VisaApplication (FK) → InvoiceApplication (through) → Invoice
Client → Payment (FK)
Invoice → Payment (OneToOne)
Pricing  (standalone lookup table for visa type → amount)
```
- `Client.save()` auto-generates `client_id` (format: `{LastName[0]}{GenderCode}{YYMMDD}{BirthYY}`)
- `VisaApplication.save()` auto-generates `application_id` (format: `{VisaPrefix}{client_id}`)
- `Invoice.save()` auto-generates `invoice_number` (`INV-YYYY-NNNN`) and recalculates tax/totals
- `InvoiceApplication` post-save/delete signals auto-update `invoice.invoice_id`

### Admin Registration Pattern
Always register to `admin_site`, never `admin.site`:
```python
from .admin_site import admin_site

@admin.register(ModelName, site=admin_site)
class ModelNameAdmin(ModelAdmin):  # from unfold.admin
    ...
```

---

## Critical Developer Workflows

### Local Setup
```bash
uv sync --frozen          # install dependencies (CI uses this)
python manage.py migrate
python manage.py runserver
```
SQLite is used locally; no `.env` required for basic dev.

### Production Database
Requires `.env` with: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

### Deployment
Push to `main` → GitHub Actions runs CI → SSH into server → executes `/home/djangoapp/apps/vortex/deploy.sh`

---

## Admin-Side Conventions

### View/Edit Mode Pattern
All model admins (Client, VisaApplication) use a **view-only by default** pattern with an `?edit=1` query param to unlock editing:
```python
def get_readonly_fields(self, request, obj=None):
    if obj is None: return ["created_at", "updated_at"]   # add page: editable
    if request.GET.get("edit") == "1": return ["created_at", "updated_at"]  # edit mode
    return [...all fields...]  # view mode: everything readonly
```

### Invoice Flow
Invoices are created/edited via a **custom builder page** (`/admin/core/invoice/builder/`), not the standard Django change form. `add_view` and `change_view` both redirect to this builder. AJAX endpoints on `InvoiceAdmin` handle adding/removing visa applications dynamically.

### Admin Media Files
Per-model JavaScript is declared in a nested `class Media` and placed in `static/admin/js/`:
```python
class Media:
    js = ('admin/js/my_script.js',)
```
Scripts use `DOMContentLoaded` + delayed re-runs (500ms/1000ms) to survive Unfold's DOM mutations.

### Dashboard Metrics
`core/admin_site.py` (`DashboardAdminSite.each_context`) computes all KPIs and chart data in Python and passes them to `templates/admin/index.html`. Charts are rendered with inline Chart.js. Add new metrics there.

---

## YAML Config Pattern (Public Pages)
Country visa pages are driven by `/config/<country>_tourist_visa.yaml`. Each file has:
`main_banner` → `sections[]` → `checklist_cta` → `expenses_sections`

To add a new country: create a YAML file + add entry to `config/visa_service_countries.yaml` + add a URL slug in `core/urls.py`.

---

## Key Files Reference
| File | Purpose |
|------|---------|
| `core/models.py` | All DB models + auto-ID generation logic |
| `core/admin.py` | All ModelAdmin classes + AJAX endpoints |
| `core/admin_site.py` | Custom admin site + dashboard KPI computation |
| `vortex_ease/settings.py` | Env-based DB config, Unfold theme settings |
| `templates/admin/index.html` | Dashboard with embedded Chart.js (~2400 lines) |
| `templates/admin/core/invoice/builder.html` | Custom invoice builder UI |
| `config/visa_service_countries.yaml` | Master list of supported countries |
