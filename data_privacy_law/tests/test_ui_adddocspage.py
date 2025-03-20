# pylint: disable=duplicate-code
# Duplicate code being used for testing the rendering of streamlit pages
"""
Testing the Add Documents page UI for title, subheaders, selectbox, dropdowns,
file uploader, and button for submission.
"""

import unittest
from streamlit.testing.v1 import AppTest

from tests.test_utils import find_widgets


class AddDocumentsPageTest(unittest.TestCase):
    """
    Unit tests for verifying subheader and column content elements on the
    State Comprehensive Laws page.
    """

    def setUp(self):
        """
        Set up the test environment by loading the State Comprehensive Laws page.
        Adjust the file path if necessary.
        """
        self.at = AppTest.from_file('app/pages/5_Add_Documents.py').run(timeout=10)

    def test_title(self):
        """
        Verify that the title of the page matches the expected title.
        """
        self.assertEqual(
            self.at.title[0].value,
            'Add a Document to our Database of Laws',
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
            "Select the type of law",
            "Enter relevant US state / NA"
        ]
        for expected_text in expected_subheaders:
            self.assertTrue(
                any(sh.value == expected_text for sh in subheaders),
                f"Expected subheader '{expected_text}' not found."
            )

    def test_radio_input_present(self):
        """
        Verify that the radio group (type of law) is present.
        """
        radio_widgets = []
        for widget in self.at:
            radio_widgets.extend(find_widgets(widget, 'radio'))
        self.assertTrue(
            len(radio_widgets) > 0,
            "Expected a radio widget for 'type of law' selection, but none found."
        )

    def test_selectbox_present(self):
        """
        Verify that a selectbox for the US states is present.
        """
        selectbox_widgets = []
        for widget in self.at:
            selectbox_widgets.extend(find_widgets(widget, 'selectbox'))
        self.assertTrue(
            len(selectbox_widgets) > 0,
            "Expected a selectbox widget for US states, but none found."
        )

    def test_file_uploader_present(self):
        """
        Verify that a file uploader is present and has expected label.
        """
        file_uploader_widgets = []
        for widget in self.at:
            file_uploader_widgets.extend(find_widgets(widget, 'file_uploader'))
        self.assertTrue(
            len(file_uploader_widgets) > 0,
            "Expected a file_uploader widget, but none found."
        )

    def test_submit_button_present(self):
        """
        Verify the presence of a button with label "Validate and Submit Inputs"
        """
        button_widgets = []
        for widget in self.at:
            button_widgets.extend(find_widgets(widget, 'button'))
        print("__________________")
        print("Buttons are", button_widgets)
        print("__________________")
        self.assertTrue(
            any(b.label == "Validate and Submit Inputs" for b in button_widgets),
            "No button with label 'Validate and Submit Inputs' was found."
        )

if __name__ == "__main__":
    unittest.main()
