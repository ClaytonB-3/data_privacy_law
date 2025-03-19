# pylint: disable=duplicate-code
# Duplicate code being used for testing the rendering of streamlit pages
"""
Testing the State Comprehensive Laws page UI for subheaders, column content, and images.

This module provides unit tests to verify that the State Comprehensive Laws page UI:
  - Renders the expected title and subheader texts.
  - Contains non-empty content in the content column.
  - Contains at least one image in the image column.
"""

import unittest
from streamlit.testing.v1 import AppTest

from tests.test_utils import find_widgets


class StateComprehensivePageTest(unittest.TestCase):
    """
    Unit tests for verifying subheader and column content elements on the
    State Comprehensive Laws page.
    """

    def setUp(self):
        """
        Set up the test environment by loading the State Comprehensive Laws page.
        Adjust the file path if necessary.
        """
        self.at = AppTest.from_file('app/pages/3_Comprehensive_State_Privacy.py').run(timeout=10)

    def test_title(self):
        """
        Verify that the title of the page matches the expected title.
        """
        self.assertEqual(
            self.at.title[0].value,
            'Explore Comprehensive State Privacy Laws',
            "The page title does not match the expected title."
        )

    def test_subheaders_presence(self):
        """
        Verify that the expected subheader texts are present in the widget tree.
        """
        subheaders = []
        for widget in self.at:
            subheaders.extend(find_widgets(widget, 'subheader'))
        expected_subheaders = [
            "Current state of Comprehensive Privacy Laws",
            "Level of Privacy Activity in the states"
        ]
        for expected_text in expected_subheaders:
            self.assertTrue(
                any(sh.value == expected_text for sh in subheaders),
                f"Expected subheader '{expected_text}' not found."
            )

    def test_content_column_has_content(self):
        """
        Verify that the content column contains expected text content.
        """
        markdown_widgets = []
        for widget in self.at:
            markdown_widgets.extend(find_widgets(widget, 'markdown'))
        expected_snippet = "19 comprehensive laws currently in effect"
        self.assertTrue(
            any(expected_snippet in mw.value for mw in markdown_widgets if mw.value),
            f"Expected content snippet '{expected_snippet}' not found in the content column."
        )

    def test_image_column_has_content(self):
        """
        Verify that the image column contains at least one image.
        """
        image_widgets = []
        for widget in self.at:
            image_widgets.extend(find_widgets(widget, 'imgs'))
        self.assertTrue(
            len(image_widgets) > 0,
            "Expected an image in the image column, but no image widget was found."
        )

if __name__ == "__main__":
    unittest.main()
