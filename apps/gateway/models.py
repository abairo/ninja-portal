from django.db import models
from .data_types import URIPatternData


class Upstream(models.Model):
    name = models.CharField(verbose_name="Name", max_length=100, unique=True)
    base_url = models.URLField(verbose_name="Base URL")
    app_token = models.CharField(
        verbose_name="Application Token", 
        max_length=512, 
        blank=True, 
        default="",
        help_text="Token injected in the request header when redirecting to this upstream."
    )
    token_prefix = models.CharField(
        verbose_name="Token Prefix", 
        max_length=50, 
        default="Bearer "
    )

    def __str__(self):
        return self.name


class URIPattern(models.Model):
    """
    Model representing a dynamic URI routing pattern.

    Attributes:
        pattern (str): The URI path pattern to match.
        methods (str): Comma-separated list of allowed HTTP methods (e.g., 'GET,POST').
        requires_auth (bool): If True, requests matching this pattern require valid authentication.
        target_path (str): Optional override for the backend destination path.
        is_active (bool): Whether this pattern is currently active.
    """
    pattern = models.CharField(verbose_name="URI pattern", max_length=256, blank=False, null=False)  # noqa: E501
    methods = models.CharField(verbose_name="Allowed methods separated with comma ','", max_length=100)  # noqa: E501
    requires_auth = models.BooleanField(default=False)
    target_path = models.CharField(verbose_name="Target path", max_length=256, blank=True, default="")  # noqa: E501
    is_active = models.BooleanField(verbose_name="Active", default=False)
    upstream = models.ForeignKey(
        Upstream, 
        on_delete=models.PROTECT, 
        related_name="uri_patterns",
        null=True,
        help_text="The destination (Upstream) to which this route will point."
    )

    class Meta:
        unique_together = ("pattern", "methods")

    def __str__(self):
        return f"{self.pattern} -> {self.upstream.name if self.upstream else 'No Upstream'}"

    def to_uri_pattern_data(self) -> URIPatternData:
        """
        Converts the model instance to a lightweight URIPatternData dataclass.

        Returns:
            URIPatternData: Data transfer object for the URI pattern.
        """
        methods = self.methods.replace(" ", "").split(',')
        return URIPatternData(
            self.pattern, 
            methods, 
            self.requires_auth, 
            self.target_path,
            upstream_base_url=self.upstream.base_url if self.upstream else "",
            upstream_app_token=self.upstream.app_token if self.upstream else "",
            upstream_token_prefix=self.upstream.token_prefix if self.upstream else ""
        )
