from typing import Tuple


class URIPatternData:
    __slots__ = ('pattern', 'methods', 'requires_auth', 'target_path')

    def __init__(self, pattern: str, methods: Tuple[str],
                 requires_auth: bool, target_path: str):
        self.pattern = pattern
        self.methods = methods
        self.requires_auth = requires_auth
        self.target_path = target_path
