"""
Utility functions for testing streamlit apps.
- find_widgets: A recursive function to search for widgets of a given type in the widget tree.
"""

def find_widgets(widget, target_type):
    """
    Goal of this function is to automate the searching of attributes
    (title, table, images etc.) in streamlit.
    Required as the structure of streamlit pages is unclear (ex: how to
    access a subheader?)

    Implemetation is done using a recursive search.
    Idea is to find a widget (given in argument 1) which matches a particular
    thing we are looking for (like title) - which is mentioned in argument 2
    of the function

    If a widget has some children which are lists or dictionaries, then 
    we loop through their contents till we find the target type. 

    Args:
        widget: The widget or container object to search within.
        target_type (str): The type of widget to search for (e.g., 'subheader',
        'markdown', 'imgs').

    Returns:
        list: A list of widget objects that match the target type.
    """
    found = []
    if hasattr(widget, 'type') and widget.type == target_type:
        found.append(widget)
    if hasattr(widget, 'children'):
        children = widget.children
        if isinstance(children, dict):
            for child in children.values():
                if isinstance(child, list):
                    for subchild in child:
                        found.extend(find_widgets(subchild, target_type))
                else:
                    found.extend(find_widgets(child, target_type))
        elif isinstance(children, list):
            for child in children:
                found.extend(find_widgets(child, target_type))
    return found
