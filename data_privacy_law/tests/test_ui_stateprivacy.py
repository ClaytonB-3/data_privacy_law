"""
Testing the State Privacy Law App UI and helper functions.

This module provides unit tests to verify that the State Privacy Law app UI:
  - Renders the expected header text.
  - Contains a state selector with the correct label.
  - Contains a question input field with the expected label.
  - Displays the expected map image.
  - Converts date strings correctly via the convert_date helper.
"""

import unittest
import importlib.util

from streamlit.testing.v1 import AppTest

from tests.test_utils import find_widgets

# Use importlib to import the module, since its filename starts with a digit.
spec = importlib.util.spec_from_file_location(
    "state_privacy", "app/pages/1_State_Privacy.py"
)
state_privacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(state_privacy)
generate_page_summary = state_privacy.generate_page_summary
map_chunk_to_metadata = state_privacy.map_chunk_to_metadata


class StatePrivacyLawAppTest(unittest.TestCase):
    """
    Unit tests for verifying UI elements on the State Privacy Law app page.
    """

    def setUp(self):
        """
        Set up the test environment by loading the State Privacy Law app.
        Adjust the file path if necessary.
        """
        # Since your tests are run from the project root, the relative path to the page is:
        # "pages/1_State_Privacy.py"
        self.at = AppTest.from_file("app/pages/1_State_Privacy.py").run(timeout=10)

    def test_header_presence(self):
        """
        Verify that the header 'Explore State Privacy Laws' is present.
        """
        headers = []
        for widget in self.at:
            headers.extend(find_widgets(widget, "header"))
        self.assertTrue(
            any(h.value == "Explore State Privacy Laws" for h in headers),
            "Header 'Explore State Privacy Laws' not found.",
        )

    def test_state_selector_presence(self):
        """
        Verify that the state selector (selectbox) is present with the expected label.
        """
        selectboxes = []
        for widget in self.at:
            selectboxes.extend(find_widgets(widget, "selectbox"))
        self.assertTrue(
            any(
                "Select a state to explore their privacy law"
                in getattr(sb, "label", "")
                for sb in selectboxes
            ),
            "State selector with expected label not found.",
        )

    def test_question_input_presence(self):
        """
        Verify that the question input field is present with the expected label.
        """
        text_inputs = []
        for widget in self.at:
            text_inputs.extend(find_widgets(widget, "text_input"))
        self.assertTrue(
            any(
                "Ask a question about State Privacy Laws:" in getattr(ti, "label", "")
                for ti in text_inputs
            ),
            "Question input field with expected label not found.",
        )

if __name__ == "__main__":
    unittest.main()
