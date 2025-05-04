def extract_token(authorization: str) -> str:
    return authorization.strip().split(" ")[-1]
