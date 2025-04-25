from django.db import models
from .data_types import URIPatternData


class URIPattern(models.Model):
    pattern = models.CharField(verbose_name="URI pattern", max_length=256, blank=False, null=False)  # noqa: E501
    methods = models.CharField(verbose_name="Allowed methods separated with comma ','", max_length=100)  # noqa: E501
    requires_auth = models.BooleanField(default=False)
    target_path = models.CharField(verbose_name="Target path", max_length=256, blank=True, default="")  # noqa: E501

    def to_uri_pattern_data(self) -> URIPatternData:
        methods = self.methods.replace(" ", "").split(',')
        return URIPatternData(
            self.pattern, methods, self.requires_auth, self.target_path
        )
