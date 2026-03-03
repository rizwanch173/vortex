# Vortex Ease — Content Writing Guide for AI Agents

> This document gives an AI agent everything it needs to write, rewrite, or improve content for the **About**, **FAQ**, and **Team** pages of the Vortex Ease website. Read this fully before writing any content.

---

## 1. Brand Identity

| Field | Value |
|-------|-------|
| **Company Name** | Vortex Ease (also written as VortexEase) |
| **Type** | Visa consultation & immigration services company |
| **Location** | United Kingdom |
| **Phone** | +44 7539 080846 |
| **Email** | contact@vortexease.com |
| **Website** | https://vortexease.com |
| **Social** | Facebook: /vortexease · Instagram: /vortexease |

### Services Offered
1. **Tourist Visas** — Schengen countries, USA, Canada, Australia, New Zealand
2. **Student Visas** — International education assistance
3. **Business Visas** — Corporate travel and meetings
4. **Family Visas** — Reuniting families
5. **Job Seeker Visas** — Employment abroad
6. **Migration/Immigration** — Permanent residency

### Countries Covered
**Schengen:** Austria, France, Germany, Greece, Italy, Netherlands, Spain, Switzerland
**Non-Schengen:** USA, Canada, Australia, New Zealand

---

## 2. Tone of Voice

| Do | Don't |
|----|-------|
| Warm, professional, reassuring | Cold, bureaucratic, jargon-heavy |
| Use "we" and "you" (conversational) | Use passive voice excessively |
| Highlight client outcomes | Focus only on internal processes |
| Be specific (name countries, numbers) | Be vague ("many countries", "various visas") |
| Acknowledge the stress of visa applications | Dismiss or trivialise client anxieties |

**Voice examples:**
- ✅ "We take the stress out of visa applications so you can focus on your journey."
- ✅ "Our consultants have helped hundreds of families reunite across borders."
- ❌ "Visa processing is facilitated through our comprehensive methodology."

---

## 3. HTML Template Pattern

Every page follows this exact structure. Do not deviate from it.

### Page Skeleton
```html
{% extends "base.html" %}
{% load static %}

{% block title %}[Page Title]{% endblock title %}

{% block content %}

<!-- PAGE TITLE BANNER -->
<section class="page-title-section bg-img cover-background"
  data-overlay-dark="0"
  data-background="{% static 'img/bg/page-title.png' %}">
  <div class="container">
    <div class="title-info">
      <h1 class="display-18 display-md-14 display-xl-12">[Page Heading]</h1>
    </div>
    <div class="breadcrumbs-info">
      <ul class="ps-0">
        <li><a href="{% url 'home' %}">Home</a></li>
        <li><a href="#">[Page Name]</a></li>
      </ul>
    </div>
  </div>
</section>

<!-- MAIN CONTENT -->
<section>
  <div class="container">
    <!-- content goes here -->
  </div>
</section>

{% endblock content %}
```

### Content Card Block
```html
<div class="p-1-6 p-sm-1-9 primary-shadow">
  <div class="mb-1-9 wow fadeInUp" data-wow-delay="200ms">
    <h2 class="h2 mb-3">[Section Title]</h2>
    <p class="mb-3">[Paragraph text]</p>
  </div>
</div>
```

### Checklist Item (icon + text)
```html
<li class="d-flex align-items-start display-29 mb-3">
  <i class="ti-check text-secondary pe-3 font-weight-800 pt-2"></i>
  <span>[Item text]</span>
</li>
```
Wrap multiple items in `<ul class="list-unstyled mb-0">`.

### CTA Button
```html
<a href="{% url 'contact' %}" class="butn md">
  <span>[Button Label]</span>
</a>
```

### Two-Column Layout (content + sidebar)
```html
<div class="row mt-n2-9">
  <div class="col-lg-8 mt-2-9">
    <!-- Main content -->
  </div>
  <div class="col-lg-4 mt-2-9">
    <div class="sidebar ps-xl-4">
      <!-- Sidebar widget -->
    </div>
  </div>
</div>
```

### Team Member Card
```html
<div class="col-sm-6 col-lg-3 mt-2-9">
  <div class="team-style1 wow fadeInUp" data-wow-delay="200ms">
    <div class="team-img">
      <img src="{% static 'img/agent/[filename].jpg' %}" alt="[Name]" class="w-100" />
    </div>
    <div class="team-info text-center p-4">
      <h4 class="mb-1 h5">[Full Name]</h4>
      <span class="text-secondary small">[Job Title]</span>
      <p class="mt-2 small">[Short bio — 1–2 sentences]</p>
    </div>
  </div>
</div>
```
Available agent image files: `agent-1.jpg` through `agent-8.jpg` in `static/img/agent/`

### FAQ Accordion Item
```html
<div class="accordion-item mb-3">
  <h3 class="accordion-header" id="faq[N]">
    <button class="accordion-button collapsed" type="button"
      data-bs-toggle="collapse"
      data-bs-target="#collapse[N]"
      aria-expanded="false"
      aria-controls="collapse[N]">
      [Question text]
    </button>
  </h3>
  <div id="collapse[N]" class="accordion-collapse collapse"
    aria-labelledby="faq[N]"
    data-bs-parent="#faqAccordion">
    <div class="accordion-body">
      [Answer text]
    </div>
  </div>
</div>
```
First item only: `class="accordion-button"` (not collapsed), `aria-expanded="true"`, `class="accordion-collapse collapse show"`.

---

## 4. About Page (`templates/about.html`)

### Current State
The page exists with a working layout. Content is generic placeholder text. It needs to be rewritten with specific, credible, brand-appropriate copy.

### Required Sections (in order)

| # | Section Heading | Content Goal |
|---|----------------|--------------|
| 1 | Welcome to Vortex Ease | Who we are, founding story, mission. 2–3 paragraphs. |
| 2 | Our Services | Bullet list of 6 services with brief description each. |
| 3 | Why Choose Us? | 5 differentiators with bold label + explanation. |
| 4 | Our Mission & Values | 1 paragraph on values. Optional. |
| — | CTA button | "Contact Us Today" → `/contact/` |
| — | Sidebar | Contact info widget (phone + email + CTA button) |

### Instructions for the AI Agent — About Page

Write content for section 1 (company story) that:
- States Vortex Ease is based in the **UK**, serving clients navigating UK and international visa processes
- Acknowledges that visa applications are stressful and time-consuming
- Positions Vortex Ease as expert guides who simplify the process
- Mentions a **high approval rate** (the site meta description references 99%)
- Keeps each paragraph to 3–4 sentences max

Write content for section 3 (Why Choose Us) using these 5 differentiators:
1. **Expert Consultants** — deep knowledge of embassy requirements per country
2. **End-to-End Support** — from document collection to appointment booking
3. **High Approval Rate** — reference the 99% claim
4. **Fast Turnaround** — efficient process minimising delays
5. **Transparent Fees** — no hidden costs, clear pricing upfront

### HTML Structure to Produce
```
<section> page title banner </section>
<section>
  <div class="container">
    <div class="row mt-n2-9">
      <div class="col-lg-8 mt-2-9">
        — card: Welcome to Vortex Ease (2–3 paragraphs)
        — card mt-2-9: Our Services (ul checklist)
        — card mt-2-9: Why Choose Us (ul checklist, bold labels)
        — CTA button
      </div>
      <div class="col-lg-4 mt-2-9">
        — sidebar widget: Contact Information
      </div>
    </div>
  </div>
</section>
```

---

## 5. FAQ Page (`templates/faq.html`)

### Current State
8 FAQ items exist and are well-structured. The accordion works correctly. Content is reasonable but can be improved or extended.

### Existing Questions (do not duplicate)
1. What documents do I need for a tourist visa application?
2. How long does the visa application process take?
3. Do you guarantee visa approval?
4. What countries do you provide visa services for?
5. How much do your services cost?
6. Can I convert a tourist visa to a work visa?
7. What if my visa application is rejected?
8. Do I need travel insurance for my visa application?

### Suggested Additional Questions
Add these to make the FAQ more complete:

| # | Question | Answer guidance |
|---|----------|----------------|
| 9 | How do I get started? | Contact us via phone/email or use the free quote form. We'll review your situation and advise on next steps. |
| 10 | Can I apply for multiple Schengen countries at once? | Explain Schengen rules — apply to the country of longest stay or first entry. We advise on which embassy to apply to. |
| 11 | How far in advance should I apply? | Tourist visas: 3 months in advance (no earlier). Recommend applying 6–8 weeks before travel. |
| 12 | What happens at a visa appointment? | Biometrics, document submission, brief interview in some cases. We prepare clients fully beforehand. |

### Instructions for the AI Agent — FAQ Page

When writing or improving FAQ answers:
- Keep answers **3–6 sentences max**
- Be direct — answer the question in the first sentence
- Where relevant, mention specific countries from the list (Austria, France, Germany, Greece, Italy, Netherlands, Spain, Switzerland, USA, Canada, Australia, New Zealand)
- Do not use phrases like "it depends" without immediately explaining on what it depends
- End answers that involve uncertainty with a clear action: "Contact us for personalised advice."

### HTML Structure to Produce
```
<section> page title banner </section>
<section>
  <div class="container">
    <div class="row mt-n2-9">
      <div class="col-lg-10 mx-auto mt-2-9">
        — card: "Common Questions" h2 + accordion #faqAccordion
          (item 1: accordion-button open, items 2–N: accordion-button collapsed)
        — text-center CTA: "Still have questions?" + Contact Us button
      </div>
    </div>
  </div>
</section>
```

---

## 6. Team Page (`templates/team.html`)

### Current State
The page is **almost empty** — it has a banner and a single intro paragraph. It needs full team member cards added. This is the most incomplete page.

### Available Image Files
`static/img/agent/` contains 8 images. Use filenames: `agent-1.jpg` to `agent-8.jpg`.
(If exact filenames are unknown, use `agent-1.jpg` as a placeholder pattern and note they should be confirmed.)

### Team Member Structure to Write
Write content for **8 team members**. Each needs:
- **Full name** (professional UK-sounding names appropriate for a visa consulting firm)
- **Job title** (from the list below)
- **Short bio** (2 sentences: expertise + what they help clients with)

### Suggested Roles
| Role | Count |
|------|-------|
| Senior Visa Consultant | 1 |
| Schengen Visa Specialist | 1 |
| US & Canada Visa Advisor | 1 |
| Australia & New Zealand Specialist | 1 |
| Student Visa Advisor | 1 |
| Immigration Case Manager | 1 |
| Client Relations Manager | 1 |
| Document Review Specialist | 1 |

### Instructions for the AI Agent — Team Page

When writing team member bios:
- Each bio must be exactly 2 sentences
- Sentence 1: their background/expertise
- Sentence 2: what they specifically help Vortex Ease clients with
- Do NOT use generic phrases like "passionate about helping people" — be specific
- Reference specific visa types or regions that match their role

**Example bio to match:**
> "Sarah has 8 years of experience processing Schengen visa applications across French, German, and Spanish embassies. She specialises in preparing complete document packages that consistently achieve first-time approval."

### HTML Structure to Produce
```
<section> page title banner </section>

<section>
  <div class="container">
    — intro card (1 paragraph about the team)

    <div class="row mt-n2-9">
      — 8 × team member cards (col-sm-6 col-lg-3, 4 per row)
    </div>

    — CTA: "Want to work with our team?" + Get in Touch button
  </div>
</section>
```

---

## 7. Shared Sidebar Widget Pattern

Used on the About page (and optionally others). Always include:

```html
<div class="widget wow fadeInUp" data-wow-delay="200ms">
  <div class="widget-content">
    <h4 class="h5 mb-3">Contact Information</h4>
    <div class="mb-3">
      <p class="mb-2"><strong>Phone:</strong></p>
      <p class="mb-0">+44 7539 080846</p>
    </div>
    <div class="mb-3">
      <p class="mb-2"><strong>Email:</strong></p>
      <p class="mb-0">contact@vortexease.com</p>
    </div>
    <div class="mt-3">
      <a href="{% url 'contact' %}" class="butn md">
        <span>Get in Touch</span>
      </a>
    </div>
  </div>
</div>
```

---

## 8. SEO Titles & Meta Descriptions (Optional Block)

Each page can override the `{% block title %}` tag. Suggested titles:

| Page | `<title>` | Meta Description |
|------|-----------|-----------------|
| About | About Vortex Ease — Visa Consultants UK | Learn about Vortex Ease, the UK's expert visa and immigration consultants with a 99% approval rate across 12 countries. |
| FAQ | Visa FAQ — Common Questions Answered \| Vortex Ease | Find answers to the most common visa application questions — documents, timelines, costs, and more. |
| Team | Meet Our Team — Vortex Ease Visa Consultants | Meet the expert visa consultants at Vortex Ease. Specialists in Schengen, US, Canada, Australian, and more. |

---

## 9. Quick Reference — Django URLs Used in Templates

| Usage | Template tag |
|-------|-------------|
| Homepage | `{% url 'home' %}` |
| Contact page | `{% url 'contact' %}` |
| Services page | `{% url 'services' %}` |
| Team page | `{% url 'team' %}` |
| About page | `{% url 'about' %}` |
| FAQ page | `{% url 'faq' %}` |
| Static file | `{% static 'img/agent/agent-1.jpg' %}` |

---

## 10. Checklist for the AI Agent Before Submitting Content

- [ ] All 3 pages extend `base.html` and use `{% load static %}`
- [ ] Page title banner section is present on every page with correct breadcrumbs
- [ ] All content is inside `{% block content %}...{% endblock content %}`
- [ ] CSS classes match the patterns documented above exactly
- [ ] `wow fadeInUp` and `data-wow-delay="200ms"` on animated elements
- [ ] Team page has 8 member cards in a 4-column responsive grid
- [ ] FAQ accordion items are numbered sequentially (collapse1, collapse2…)
- [ ] First FAQ item has `show` class and `aria-expanded="true"`, rest are `collapsed`
- [ ] All links use `{% url 'name' %}` — never hardcoded paths
- [ ] All images use `{% static '...' %}` — never hardcoded paths
- [ ] Contact info is consistent: +44 7539 080846 · contact@vortexease.com
