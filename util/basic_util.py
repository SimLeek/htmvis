def clamp(n, min_n, max_n):
    #
    """
    Clamps a number to a min or max value.

    Sources:
        http://stackoverflow.com/a/5996949
    """
    return max(min(max_n, n), min_n)


