"""
Testing the Federal Privacy Laws page UI for subheaders and column content.

This module provides unit tests to verify that the Federal Privacy Laws page UI:
  - Renders the expected subheader texts.
  - Contains non-empty content in the content column.
  - Contains an image in the image column.
"""

import unittest
from streamlit.testing.v1 import AppTest


def find_widgets(widget, target_type):
    """
    Goal of this function is to automate the searching of attributes (title, table, images etc.) in streamlit.
    Required as the structure of streamlit pages is unclear (ex: how to access a subheader?)

    Implemetation is done using a recursive search.
    Idea is to find a widget (given in argument 1) which matches a particular thing we are looking for (like title) - 
    which is mentioned in argument 2 of the function

    If a widget has some children which are lists or dictionaries, then we loop through their contents till we find
    the target type. 

    Args:
        widget: The widget or container object to search within.
        target_type (str): The type of widget to search for (e.g., 'subheader', 'markdown', 'imgs').

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


class StateFederalPageSubheaderTest(unittest.TestCase):
    """
    Unit tests for verifying subheader and column content elements on the Federal Privacy Laws page.
    """

    def setUp(self):
        """
        Set up the test environment by loading the Federal Privacy Laws page.
        """
        self.at = AppTest.from_file('./pages/2_Federal_Privacy.py').run(timeout=10)

    def test_subheaders_presence(self):
        """
        Verify that the expected subheader texts are present in the widget tree.

        This test searches for all subheader widgets in the page and asserts that each
        expected subheader text is found.
        """
        subheaders = []

        for widget in self.at:
            subheaders.extend(find_widgets(widget, 'subheader'))

        expected_subheaders = [
            "The main message on Federal Privacy Laws",
            "The crucial ongoing debate",
            "Emerging Technology and Data Practices"
        ]

        for expected_text in expected_subheaders:
            self.assertTrue(
                any(sh.value == expected_text for sh in subheaders),
                f"Expected subheader '{expected_text}' not found."
            )

    def test_content_column_has_content(self):
        """
        Verify that the content column contains expected text content.

        This test searches for markdown widgets in the widget tree and asserts that one
        of them contains a known snippet of text expected in the content column.
        """
        markdown_widgets = []

        for widget in self.at:
            markdown_widgets.extend(find_widgets(widget, 'markdown'))

        expected_snippet = "Federal bills cover almost every corner of privacy"

        self.assertTrue(
            any(expected_snippet in mw.value for mw in markdown_widgets if mw.value),
            f"Expected content snippet '{expected_snippet}' not found in the content column."
        )

    def test_image_column_has_content(self):
        """
        Verify that the image column contains an image.

        This test searches for image widgets (of type 'imgs') in the widget tree and
        asserts that at least one image widget is found.
        """
        image_widgets = []

        for widget in self.at:
            image_widgets.extend(find_widgets(widget, 'imgs'))

        self.assertTrue(
            len(image_widgets) > 0,
            "Expected an image in the image column, but no image widget was found."
        )
    
    
    def test_title(self):
        """
        Verify to see that the title of the page matches the expected title.
        """
        self.assertEqual(self.at.title[0].value, 'Explore Federal Privacy Laws')


if __name__ == "__main__":
    unittest.main()
