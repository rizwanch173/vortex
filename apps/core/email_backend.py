import ssl

from django.core.mail.backends.smtp import EmailBackend


class InsecureTLSBackend(EmailBackend):
    """SMTP backend that disables TLS certificate verification (dev only)."""

    def _get_ssl_context(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    def open(self):
        if self.connection:
            return False

        try:
            self.connection = self.connection_class(
                self.host,
                self.port,
                local_hostname=getattr(self, "local_hostname", None),
                timeout=self.timeout,
            )

            if self.use_tls:
                self.connection.starttls(context=self._get_ssl_context())

            if self.username and self.password:
                self.connection.login(self.username, self.password)

            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False
