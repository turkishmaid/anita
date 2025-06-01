"""General utilities."""


def only_fields_like_old(documents: list[dict], filter_terms: tuple[str]) -> list[dict]:
    """Filter the list of dictionaries to those containing at least one key that contains
    any of the filter terms, and reduce the fileds of the result to just the keys in filt.

    >>> j = [{"a": 1, "b": 2, "c": 3}, {"b": 3, "c": 4, "d": 5}, {"c": 5, "d": 6, "e": 7}]
    >>> #             --------------    --------------            ------
    >>> filt = ("b", "c")
    >>> only_fields_like(j, filt)
    [{'b': 2, 'c': 3}, {'b': 3, 'c': 4}, {'c': 5}]
    >>> j = [{"a": 1, "b": 2, "c": 3}, {"b": 3, "c": 4, "d": 5}, {"d": 6, "e": 7}]
    >>> #             --------------    --------------
    >>> only_fields_like(j, filt)
    [{'b': 2, 'c': 3}, {'b': 3, 'c': 4}]
    """
    dd = documents
    ff = filter_terms
    return [{k: v for k, v in d.items() if any(f in k for f in ff)} for d in dd if any(f in k for f in ff for k in d)]


def only_fields_like(documents: list[dict], filter_terms: tuple[str]) -> list[dict]:
    """Filter the list of dictionaries to those containing at least one key that contains
    any of the filter terms, and reduce the fields of the result to just the keys that match.

    >>> j = [{"a": 1, "b": 2, "c": 3}, {"b": 3, "c": 4, "d": 5}, {"c": 5, "d": 6, "e": 7}]
    >>> #             --------------    --------------            ------
    >>> filt = ("b", "c")
    >>> only_fields_like(j, filt)
    [{'b': 2, 'c': 3}, {'b': 3, 'c': 4}, {'c': 5}]
    >>> j = [{"a": 1, "b": 2, "c": 3}, {"b": 3, "c": 4, "d": 5}, {"d": 6, "e": 7}]
    >>> #             --------------    --------------
    >>> only_fields_like(j, filt)
    [{'b': 2, 'c': 3}, {'b': 3, 'c': 4}]
    """
    result = []

    for document in documents:
        # Find matching fields in this document
        matching_fields = {key: value for key, value in document.items() if any(term in key for term in filter_terms)}

        # Only include document if it has at least one matching field
        if matching_fields:
            result.append(matching_fields)

    return result


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
