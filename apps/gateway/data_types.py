from parse import compile, Parser


class URIPatternData:
    __slots__ = (
        'pattern', 'methods', 'requires_auth', 'target_path', 
        'upstream_base_url', 'upstream_app_token', 'upstream_token_prefix'
    )

    def __init__(
        self,
        pattern: str,
        methods: tuple[str],
        requires_auth: bool,
        target_path: str = "",
        upstream_base_url: str = "",
        upstream_app_token: str = "",
        upstream_token_prefix: str = ""
    ):
        self.pattern: Parser = compile(pattern)
        self.methods: set[str] = set(methods)
        self.requires_auth = requires_auth
        self.target_path = target_path
        self.upstream_base_url = upstream_base_url
        self.upstream_app_token = upstream_app_token
        self.upstream_token_prefix = upstream_token_prefix
