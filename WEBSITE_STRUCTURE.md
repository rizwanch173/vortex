# Vortex Ease — Main Website Structure & Pages

## Overview

**Vortex Ease** (`https://vortexease.com`) is a visa consultation platform serving clients from the UK. The public website is fully server-rendered using Django templates. All visa country page content is driven by YAML configuration files — no database reads for public content pages.

- **Brand Colours:** Primary Blue `#003a66` · Accent Red `#e02454`
- **Contact:** +44 7539 080846 · contact@vortexease.com
- **Tech Stack:** Django 5.2 · Bootstrap · jQuery · Owl Carousel · WeasyPrint (PDF)

---

## Site Map

```
/                                       Home
├── /services/                          Services Overview
├── /service-details/tourist-visa/      Tourist Visa Service Detail
│
├── /tourist-visa/<slug>/               Country Visa Detail (dynamic × 12)
│   ├── /tourist-visa/austria-tourist-visa/
│   ├── /tourist-visa/france-tourist-visa/
│   ├── /tourist-visa/germany-tourist-visa/
│   ├── /tourist-visa/greece-tourist-visa/
│   ├── /tourist-visa/italy-tourist-visa/
│   ├── /tourist-visa/netherlands-tourist-visa/
│   ├── /tourist-visa/spain-tourist-visa/
│   ├── /tourist-visa/switzerland-tourist-visa/
│   ├── /tourist-visa/australia-tourist-visa/
│   ├── /tourist-visa/canada-tourist-visa/
│   ├── /tourist-visa/usa-tourist-visa/
│   └── /tourist-visa/new-zealand-tourist-visa/
│
├── /about/                             About Us
├── /team/                              Our Team
├── /faq/                               FAQ
├── /contact/                           Contact Form
├── /terms-and-conditions/              Terms & Conditions
│
├── /blogs/                             Blog Listing
│   ├── /blog/tourist-visa-tips/        Blog Post 1
│   ├── /blog/student-visa-guide/       Blog Post 2
│   └── /blog/work-visa-requirements/   Blog Post 3
│
├── /search/                            Search Results  (?s=query)
│
└── /invoice/<id>/pay/                  Invoice Payment (public)
    ├── /invoice/<id>/preview/          Invoice Preview (public)
    └── /invoice/<id>/download/         Invoice PDF Download (public)
```

---

## Page-by-Page Reference

### `/` — Home
- **Template:** `templates/home.html`
- **View:** `core/views.py → home()`
- **Data Sources:**
  - `config/visa_service_countries.yaml` → countries grid
  - `config/testmonial.yaml` + random success story images → testimonials carousel
- **Sections:**
  1. Hero carousel (3 slides with background images + CTA buttons)
  2. About section (mission & vision block)
  3. Countries We Serve grid (12 country flag cards, dynamic from YAML)
  4. Services carousel (Tourist, Student, Business, Family, Job Seeker, Migration)
  5. Benefits section (3 benefit icons)
  6. Testimonials / Success Stories carousel (`component/testmonial.html`)

---

### `/services/` — Services Overview
- **Template:** `templates/services.html`
- **View:** `core/views.py → services()`
- **Data Sources:** `config/visa_service_countries.yaml` (sidebar navigation)
- **Sections:**
  1. Page title + breadcrumbs
  2. Service cards grid (Tourist, Student, Business visa types with images + descriptions)
  3. Countries sidebar

---

### `/service-details/tourist-visa/` — Tourist Visa Service Detail
- **Template:** `templates/service_details.html`
- **View:** `core/views.py → tourist_visa_service_details()`
- **Data Sources:** None (static content)

---

### `/tourist-visa/<slug>/` — Country Visa Detail (Dynamic)
- **Template:** `templates/tourist_visa_detail.html`
- **View:** `core/views.py → visa_detail_page(slug)`
- **Data Sources:** `config/<country>_tourist_visa.yaml` (loaded per slug)
- **Slug → YAML mapping:** slug dashes replaced with underscores (e.g. `france-tourist-visa` → `france_tourist_visa.yaml`)
- **Sections:**
  1. Page title + breadcrumbs
  2. Hero image (from `config.images[0]`)
  3. Dynamic sections loop from YAML:
     - General info sections
     - **Benefits** section (bullet list from `description_benefits[]`)
     - **Estimated Cost** section (cost breakdown list)
     - Benefits + Estimated Cost can render merged in a single two-column card
  4. Sidebar:
     - All countries list (active country highlighted)
     - "Request Checklist" CTA (email input — currently not wired to a backend endpoint)
  5. Apply Now CTA button

#### YAML Structure per Country (`config/<country>_tourist_visa.yaml`)
```yaml
main_banner:
  title: "Tourist in France"
  image: <url>

heading: "France Tourist Visa"
description: "..."
images: [<url>, <url>, <url>]

sections:
  - title: "Tourist Cities in France"
    description: "..."
  - title: "Benefits"
    description: "..."
    description_benefits:
      - "Travel across Schengen Area for up to 90 days"
      - "..."
  - title: "Estimated Cost"
    description: "..."
    description_benefits:
      - "Embassy fee: £25–£30"
      - "Travel insurance: ~£15"

checklist_cta:
  cta_title: "Download Checklist"
  cta_link: <pdf-url>

expenses_sections:
  title: "France Expenses"
  expenses: [...]
```

---

### `/about/` — About Us
- **Template:** `templates/about.html`
- **View:** `core/views.py → about()`
- **Data Sources:** None (static content)

---

### `/team/` — Our Team
- **Template:** `templates/team.html`
- **View:** `core/views.py → team()`
- **Data Sources:** None (static content)
- **Images:** `static/img/agent/` (8 team member photos)

---

### `/faq/` — FAQ
- **Template:** `templates/faq.html`
- **View:** `core/views.py → faq()`
- **Data Sources:** None (static content)

---

### `/contact/` — Contact Form
- **Template:** `templates/contact_us.html`
- **View:** `core/views.py → contact()` (GET + POST)
- **Data Sources:** `config/visa_service_countries.yaml` (country dropdown)
- **Form Fields:** name, email, subject, message
- **Validation:** Manual (`if not field`, email `@` + `.` check)
- **On Success:** Sends email to `DEFAULT_FROM_EMAIL` via SMTP (IONOS), redirects back to `/contact/`
- **On Error:** Re-renders form with Django `messages` framework error
- **Note:** No Django Form class — validation is inline in the view

---

### `/terms-and-conditions/` — Terms & Conditions
- **Template:** `templates/terms_and_conditions.html`
- **View:** `core/views.py → terms_and_conditions()`
- **Data Sources:** None (static content)

---

### `/blogs/` — Blog Listing
- **Template:** `templates/blogs.html`
- **View:** `core/views.py → blogs()`
- **Data Sources:** Hardcoded list in view (title, description, URL, image path)
- **Blog entries:**
  | Title | URL |
  |-------|-----|
  | Tourist Visa Tips: Essential Advice for Your Journey | `/blog/tourist-visa-tips` |
  | Student Visa Guide: Your Path to International Education | `/blog/student-visa-guide` |
  | Work Visa Requirements: Navigating Global Employment | `/blog/work-visa-requirements` |

---

### `/blog/tourist-visa-tips/` — Blog Post 1
- **Template:** `templates/blog_tourist_visa_tips.html`
- **View:** `core/views.py → blog_tourist_visa_tips()`
- **Data Sources:** None (static content)

---

### `/blog/student-visa-guide/` — Blog Post 2
- **Template:** `templates/blog_student_visa_guide.html`
- **View:** `core/views.py → blog_student_visa_guide()`
- **Data Sources:** None (static content)

---

### `/blog/work-visa-requirements/` — Blog Post 3
- **Template:** `templates/blog_work_visa_requirements.html`
- **View:** `core/views.py → blog_work_visa_requirements()`
- **Data Sources:** None (static content)

---

### `/search/` — Search Results
- **Template:** `templates/search.html`
- **View:** `core/views.py → search()`
- **Query Param:** `?s=<query>` (GET)
- **Searches across:**
  1. Country names and slugs (from `visa_service_countries.yaml`)
  2. Hardcoded services list (Tourist, Student, Business, Family, Job Seeker, Migration)
  3. Hardcoded pages list (About, FAQ, Contact, Blog posts)
- **Returns:** Array of `{ title, description, url }` results

---

### `/invoice/<id>/pay/` — Invoice Payment Page (Public)
- **Template:** `templates/invoice/pay.html`
- **View:** `core/views.py → invoice_pay()`
- **Data Sources:** `Invoice` model (DB read)
- **Note:** Demo checkout only — POST sets `payment_success = True`, no real payment gateway

---

### `/invoice/<id>/preview/` — Invoice Preview (Public)
- **Template:** `templates/admin/core/invoice/preview_pdf.html`
- **View:** `core/views.py → invoice_preview_public()`
- **Data Sources:** `Invoice`, `InvoiceApplication`, `InvoiceOtherPayment` models

---

### `/invoice/<id>/download/` — Invoice PDF Download (Public)
- **View:** `core/views.py → invoice_download_public()`
- **Template:** `templates/admin/core/invoice/preview_pdf.html` (rendered to PDF)
- **PDF Engine:** WeasyPrint
- **Output:** `invoice_<id>.pdf` file download

---

## Template Inheritance

```
base.html  (master layout — blocks: title, content, extra_head)
├── global/header.html        Navigation bar, search, logo, CTA
├── global/footer.html        Logo, contact info, quick links, social icons
├── component/testmonial.html Success story Owl carousel (used in home.html)
└── All page templates extend base.html
```

### `base.html` loads globally:
| Asset | Path |
|-------|------|
| CSS | `static/css/plugins.css` |
| CSS | `static/css/styles.css` |
| CSS | `static/search/search.css` |
| CSS | `static/quform/css/base.css` |
| JS | `static/js/jquery.min.js` |
| JS | `static/js/popper.min.js` |
| JS | `static/js/bootstrap.min.js` |
| JS | `static/js/core.min.js` |
| JS | `static/search/search.js` |
| JS | `static/js/main.js` |
| Icons | Font Awesome · Themify Icons |

---

## Static Assets Structure

```
static/
├── css/
│   ├── plugins.css          Third-party plugin styles (Owl Carousel, animations)
│   ├── styles.css           Main theme stylesheet
│   └── admin_inline_custom.css  Admin customisation
├── js/
│   ├── jquery.min.js
│   ├── bootstrap.min.js
│   ├── core.min.js          Bootstrap components + animations
│   ├── popper.min.js
│   └── main.js              Custom site scripts
├── search/
│   ├── search.js
│   └── search.css
├── fonts/
│   ├── Font Awesome (fa-solid, fa-regular, fa-brands)
│   └── Themify icons
└── img/
    ├── logos/               logo.png, final_logo.png, favicon
    ├── banner/              Hero banner images (banner-01.jpg, banner-03.jpg)
    ├── content/             Page content (visa-01~06.jpg, about-01~05.jpg, flags)
    ├── bg/                  Background images (page-title.png, bg-01.jpg)
    ├── blog/                Blog post images (blog-01~03.jpg)
    ├── icons/               Service & benefit icons (icon-07~28.png)
    ├── agent/               Team member photos (8 images)
    ├── avatars/             User avatars (19 images)
    ├── clients/             Client logos (6 images)
    ├── countries/           Country images (germany.webp)
    └── testimentional/      Success story images (testimonials carousel)
```

---

## Country Pages — Supported Countries

| Country | Slug | Region |
|---------|------|--------|
| Austria | `austria-tourist-visa` | Schengen |
| France | `france-tourist-visa` | Schengen |
| Germany | `germany-tourist-visa` | Schengen |
| Greece | `greece-tourist-visa` | Schengen |
| Italy | `italy-tourist-visa` | Schengen |
| Netherlands | `netherlands-tourist-visa` | Schengen |
| Spain | `spain-tourist-visa` | Schengen |
| Switzerland | `switzerland-tourist-visa` | Schengen |
| Australia | `australia-tourist-visa` | Non-Schengen |
| Canada | `canada-tourist-visa` | Non-Schengen |
| USA | `usa-tourist-visa` | Non-Schengen |
| New Zealand | `new-zealand-tourist-visa` | Non-Schengen |

**To add a new country:**
1. Create `config/<country>_tourist_visa.yaml` following the YAML structure above
2. Add an entry to `config/visa_service_countries.yaml`
3. Add a URL entry in `core/urls.py` if needed (auto-covered by the dynamic slug route)

---

## Known Incomplete / Placeholder Areas

| Page / Feature | Issue |
|----------------|-------|
| Checklist request form (visa detail sidebar) | Posts to `#` — not connected to a view |
| Invoice payment (`/invoice/<id>/pay/`) | Demo only — no real payment gateway |
| Blog data | Hardcoded in `views.py`, not from DB or YAML |
| Contact form | No Django Form class — manual validation only |

---

## Email Configuration

- **Provider:** IONOS SMTP (`smtp.ionos.co.uk:587`, TLS)
- **Used by:** Contact form (`/contact/`) and invoice send (admin side)
- **Templates:** `templates/email/invoice_email.html`
- **Bank details in email:** VORTEXEASE LTD · Sort Code 23-11-85 · Account 58904084
