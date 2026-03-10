from django.db import models


class Course(models.Model):
    course_id = models.BigIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=500, blank=True)
    institute_name = models.CharField(max_length=500, blank=True)
    campus = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=500, blank=True)
    discipline_name = models.CharField(max_length=255, blank=True)
    specialization_name = models.CharField(max_length=255, blank=True)
    degreelevel_name = models.CharField(max_length=255, blank=True)
    coursetitle_name = models.CharField(max_length=255, blank=True)
    course_language = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    duration_one = models.IntegerField(null=True, blank=True)
    duration_id = models.BigIntegerField(null=True, blank=True)
    course_fee = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    course_fee_id = models.BigIntegerField(null=True, blank=True)
    course_fee_usd = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=20, blank=True)
    logo = models.TextField(blank=True)
    institute_slug = models.CharField(max_length=255, blank=True)
    course_slug = models.CharField(max_length=255, blank=True)
    clean_course_slug = models.CharField(max_length=255, blank=True)
    program_identifier = models.CharField(max_length=100, blank=True)
    rating = models.FloatField(null=True, blank=True)
    requirements = models.TextField(null=True, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    

    class Meta:
        ordering = ["course_id"]
        indexes = [
            models.Index(fields=["institute_slug"]),
            models.Index(fields=["discipline_name"]),
            models.Index(fields=["degreelevel_name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.institute_name})"
