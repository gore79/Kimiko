def greet(user_name: str) -> str:
    user_name = (user_name or "").strip() or "there"
    return f"Hello, {user_name}! How can I assist you today?"
