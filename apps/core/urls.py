from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("tourist-visa/<slug:slug>/", views.visa_detail_page, name="visa_detail_page"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("service-details/tourist-visa/", views.tourist_visa_service_details, name="tourist_visa_service_details"),
    path("about/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("team/", views.team, name="team"),
    path("terms-and-conditions/", views.terms_and_conditions, name="terms_and_conditions"),
    path("blog/tourist-visa-tips/", views.blog_tourist_visa_tips, name="blog_tourist_visa_tips"),
    path("blog/student-visa-guide/", views.blog_student_visa_guide, name="blog_student_visa_guide"),
    path("blog/work-visa-requirements/", views.blog_work_visa_requirements, name="blog_work_visa_requirements"),
    path("blogs/", views.blogs, name="blogs"),
    path("search/", views.search, name="search"),
    path("invoice/<int:invoice_id>/pay/", views.invoice_pay, name="invoice_pay"),
    path("invoice/<int:invoice_id>/preview/", views.invoice_preview_public, name="invoice_preview_public"),
    path("invoice/<int:invoice_id>/download/", views.invoice_download_public, name="invoice_download_public"),

    # ── Study Visa Section ──────────────────────────────────────────────────────
    path("study-visa/", views.study_visa_hub, name="study_visa_hub"),
    path("study-visa/uk/", views.study_visa_uk, name="study_visa_uk"),
    path("study-visa/uk/requirements/", views.study_visa_uk_requirements, name="study_visa_uk_requirements"),
    path("study-visa/uk/process/", views.study_visa_uk_process, name="study_visa_uk_process"),
    path("study-visa/uk/fees/", views.study_visa_uk_fees, name="study_visa_uk_fees"),
    path("study-visa/uk/faqs/", views.study_visa_uk_faqs, name="study_visa_uk_faqs"),
    path("study-visa/uk/universities/", views.study_visa_uk_universities, name="study_visa_uk_universities"),
]
