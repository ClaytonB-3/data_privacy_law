"""
Testing the GDPR page UI for subheaders and column content.

This module provides unit tests to verify that the GDPR page UI:
  - Renders the expected subheader texts.
  - Contains non-empty content in the content column.
  - Contains an image in the image column.
"""

import unittest
from streamlit.testing.v1 import AppTest

from tests.test_utils import find_widgets



class StateFederalPageSubheaderTest(unittest.TestCase):
    """
    Unit tests for verifying subheader and column content elements on the
    Federal Privacy Laws page.
    """

    def setUp(self):
        """
        Set up the test environment by loading the Federal Privacy Laws page.
        """
        self.at = AppTest.from_file('app/pages/4_EU_GDPR.py').run(timeout=10)

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
            "Overview of GDPR",
            "Key Principles of GDPR"
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

        expected_snippet = "The General Data Protection Regulation (GDPR)" \
"is a comprehensive data protection law " \
"enacted by the European Union (EU)"

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
        self.assertEqual(self.at.title[0].value, 'Explore the GDPR')


if __name__ == "__main__":
    unittest.main()
