import time
from decimal import Decimal, InvalidOperation

import requests
from django.core.management.base import BaseCommand, CommandError

from apps.universties_portal.models import Course


class Command(BaseCommand):
    help = "Import course records from the Times Course Finder API into the local database."

    api_url = "https://tcf-backend.timescoursefinder.com/api/v2/search/courses_v2/"

    update_fields = [
        "name",
        "institute_name",
        "campus",
        "address",
        "discipline_name",
        "specialization_name",
        "degreelevel_name",
        "coursetitle_name",
        "course_language",
        "duration",
        "duration_one",
        "duration_id",
        "course_fee",
        "course_fee_id",
        "course_fee_usd",
        "currency",
        "logo",
        "institute_slug",
        "course_slug",
        "clean_course_slug",
        "program_identifier",
        "rating",
        "requirements",
        "raw_payload",
    ]

    def add_arguments(self, parser):
        parser.add_argument("--start-page", type=int, default=1)
        parser.add_argument("--end-page", type=int, default=None)
        parser.add_argument("--max-pages", type=int, default=None)
        parser.add_argument("--batch-size", type=int, default=2000)
        parser.add_argument("--timeout", type=int, default=30)
        parser.add_argument("--retries", type=int, default=3)
        parser.add_argument("--sleep", type=float, default=0.0)

    def handle(self, *args, **options):
        start_page = options["start_page"]
        end_page = options["end_page"]
        max_pages = options["max_pages"]
        batch_size = options["batch_size"]
        timeout = options["timeout"]
        retries = options["retries"]
        sleep_time = options["sleep"]

        if start_page < 1:
            raise CommandError("--start-page must be >= 1")
        if end_page is not None and end_page < start_page:
            raise CommandError("--end-page must be >= --start-page")
        if max_pages is not None and max_pages < 1:
            raise CommandError("--max-pages must be >= 1")
        if batch_size < 1:
            raise CommandError("--batch-size must be >= 1")
        if retries < 1:
            raise CommandError("--retries must be >= 1")

        self.stdout.write(self.style.NOTICE("Starting course import..."))
        self.stdout.write(
            f"API: {self.api_url} | start_page={start_page} | "
            f"end_page={end_page or 'auto'} | max_pages={max_pages or 'none'} | "
            f"batch_size={batch_size}"
        )

        session = requests.Session()
        current_page = start_page
        processed_pages = 0
        total_pages = None
        total_rows_seen = 0
        upserted_count = 0
        skipped_rows = 0
        duplicate_rows_dropped = 0
        buffer = []

        try:
            while True:
                if end_page is not None and current_page > end_page:
                    break
                if max_pages is not None and processed_pages >= max_pages:
                    break
                if total_pages is not None and current_page > total_pages:
                    break

                payload = self._fetch_page(
                    session=session,
                    page=current_page,
                    timeout=timeout,
                    retries=retries,
                )

                if total_pages is None:
                    total_pages = self._as_int(payload.get("total_pages"))
                    total = payload.get("total")
                    rows_per_page = payload.get("rows_per_page")
                    self.stdout.write(
                        f"Remote reports total={total}, total_pages={total_pages}, "
                        f"rows_per_page={rows_per_page}"
                    )

                rows = payload.get("result") or []
                if not rows:
                    self.stdout.write(
                        self.style.WARNING(f"Page {current_page}: no rows returned, stopping import.")
                    )
                    break

                for row in rows:
                    course_obj = self._build_course_obj(row)
                    if course_obj is None:
                        skipped_rows += 1
                        continue
                    buffer.append(course_obj)

                total_rows_seen += len(rows)
                processed_pages += 1

                if len(buffer) >= batch_size:
                    upserted_rows, dropped_rows = self._flush_buffer(buffer, batch_size)
                    upserted_count += upserted_rows
                    duplicate_rows_dropped += dropped_rows
                    buffer = []

                self.stdout.write(
                    f"Page {current_page} done | rows={len(rows)} | total_seen={total_rows_seen}"
                )
                current_page += 1

                if sleep_time > 0:
                    time.sleep(sleep_time)

            if buffer:
                upserted_rows, dropped_rows = self._flush_buffer(buffer, batch_size)
                upserted_count += upserted_rows
                duplicate_rows_dropped += dropped_rows

        finally:
            session.close()

        self.stdout.write(
            self.style.SUCCESS(
                f"Import finished. pages_processed={processed_pages}, rows_seen={total_rows_seen}, "
                f"rows_upserted={upserted_count}, rows_skipped={skipped_rows}, "
                f"duplicate_rows_dropped={duplicate_rows_dropped}, last_page={current_page - 1}"
            )
        )

    def _fetch_page(self, session, page, timeout, retries):
        params = {"page": page}

        last_error = None
        for attempt in range(1, retries + 1):
            try:
                response = session.get(self.api_url, params=params, timeout=timeout)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("API did not return a JSON object.")
                return payload
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt < retries:
                    wait_s = min(2 ** (attempt - 1), 10)
                    self.stderr.write(
                        self.style.WARNING(
                            f"Page {page} failed (attempt {attempt}/{retries}): {exc}. "
                            f"Retrying in {wait_s}s..."
                        )
                    )
                    time.sleep(wait_s)

        raise CommandError(f"Page {page} failed after {retries} attempts: {last_error}")

    def _flush_buffer(self, buffer, batch_size):
        deduped_by_course_id = {}
        for obj in buffer:
            deduped_by_course_id[obj.course_id] = obj
        deduped_rows = list(deduped_by_course_id.values())
        dropped_rows = len(buffer) - len(deduped_rows)

        if dropped_rows:
            self.stdout.write(
                self.style.WARNING(
                    f"Dropped {dropped_rows} duplicate rows in current batch before upsert."
                )
            )

        Course.objects.bulk_create(
            deduped_rows,
            batch_size=batch_size,
            update_conflicts=True,
            update_fields=self.update_fields,
            unique_fields=["course_id"],
        )
        return len(deduped_rows), dropped_rows

    def _build_course_obj(self, item):
        course_id = self._as_int(item.get("course_id"))
        if not course_id:
            return None

        requirements = item.get("requirements")
        if requirements is not None and not isinstance(requirements, str):
            requirements = str(requirements)

        return Course(
            course_id=course_id,
            name=self._clean_str(item.get("name"), 500),
            institute_name=self._clean_str(item.get("institute_name"), 500),
            campus=self._clean_str(item.get("campus"), 255),
            address=self._clean_str(item.get("address"), 500),
            discipline_name=self._clean_str(item.get("discipline_name"), 255),
            specialization_name=self._clean_str(item.get("specialization_name"), 255),
            degreelevel_name=self._clean_str(item.get("degreelevel_name"), 255),
            coursetitle_name=self._clean_str(item.get("coursetitle_name"), 255),
            course_language=self._clean_str(item.get("course_language"), 100),
            duration=self._clean_str(item.get("duration"), 100),
            duration_one=self._as_int(item.get("duration_one")),
            duration_id=self._as_int(item.get("duration_id")),
            course_fee=self._as_decimal(item.get("course_fee")),
            course_fee_id=self._as_int(item.get("course_fee_id")),
            course_fee_usd=self._as_decimal(item.get("course_fee_usd")),
            currency=self._clean_str(item.get("currency"), 20),
            logo=(item.get("logo") or "")[:2000],
            institute_slug=self._clean_str(item.get("institute_slug"), 255),
            course_slug=self._clean_str(item.get("course_slug"), 255),
            clean_course_slug=self._clean_str(item.get("clean_course_slug"), 255),
            program_identifier=self._clean_str(item.get("program_identifier"), 100),
            rating=self._as_float(item.get("rating")),
            requirements=requirements,
            raw_payload=item,
        )

    @staticmethod
    def _clean_str(value, max_length):
        if value is None:
            return ""
        return str(value).strip()[:max_length]

    @staticmethod
    def _as_int(value, default=None):
        if value in (None, ""):
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _as_float(value):
        if value in (None, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _as_decimal(value):
        if value in (None, ""):
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return None
