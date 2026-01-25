from django.db import models
from .data_types import URIPatternData


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

    class Meta:
        unique_together = ("pattern", "methods")

    def to_uri_pattern_data(self) -> URIPatternData:
        """
        Converts the model instance to a lightweight URIPatternData dataclass.

        Returns:
            URIPatternData: Data transfer object for the URI pattern.
        """
        methods = self.methods.replace(" ", "").split(',')
        return URIPatternData(
            self.pattern, methods, self.requires_auth, self.target_path
        )
