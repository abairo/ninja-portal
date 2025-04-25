from parse import compile, Parser


class URIPatternData:
    __slots__ = ('pattern', 'methods', 'requires_auth', 'target_path')

    def __init__(self, pattern: str, methods: tuple[str],
                 requires_auth: bool, target_path: str):
        self.pattern: Parser = compile(pattern)
        self.methods: set[str] = set(methods)
        self.requires_auth = requires_auth
        self.target_path = target_path
