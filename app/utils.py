def convert_to_string(instance) -> str:
    """Convert model instance data to a space-separated string"""
    return " ".join(str(value) for value in instance.__data__.values()) 