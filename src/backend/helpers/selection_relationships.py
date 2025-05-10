
def selection_relationships(
    selection: str,
    relationships: list[str],
) -> list[str]:
    """
    Given a selection and a list of relationships, return a list of relationships that are
    related to the selection.

    Args:
        selection (str): The selection to check.
        relationships (list[str]): The list of relationships to check.

    Returns:
        list[str]: A list of relationships that are related to the selection.
    """
    return [relationship for relationship in relationships if selection in relationship]