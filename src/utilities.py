def nameof(obj):
    """
    Returns the name of the object as a string.
    """
    if hasattr(obj, '__name__'):
        return obj.__name__
    elif hasattr(obj, '__class__'):
        return obj.__class__.__name__
    else:
        return str(obj)