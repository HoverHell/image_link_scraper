"""
Common shared utilities.
"""

def merge_with_kwargs_dict(kwargs, key, pre=None, post=None, inplace=True):
    """
    Helper to setdefault/override the insides of a mapping in kwargs.

    Mutates the `kwargs` (if `inplace=True`, default), does not mutate the mapping in it.

    :param pre: dict with 'setdefault' values relative to the possibly-specified.
    :param post: dict with overrides of the possible specified (and `pre`).
    """
    result = {}

    if pre is not None:
        result.update(pre)

    specified = kwargs.get(key)
    if specified is not None:
        result.update(specified)

    if post is not None:
        result.update(post)

    if inplace:
        kwargs[key] = result
    return result
