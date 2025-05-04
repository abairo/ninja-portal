def extract_token(authorization: str) -> str:
    return authorization.split(" ")[-1]
