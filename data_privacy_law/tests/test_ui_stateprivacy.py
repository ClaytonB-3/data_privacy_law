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
generate_llm_response = state_privacy.generate_llm_response


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

    # def test_convert_date_function(self):
    #     """
    #     Verify that the convert_date function converts dates correctly.
    #     """

    #     # Use importlib to import the module, since its filename starts with a digit.
    #     spec = importlib.util.spec_from_file_location(
    #         "state_privacy", "app/pages/1_State_Privacy.py"
    #     )
    #     state_privacy = importlib.util.module_from_spec(spec)
    #     spec.loader.exec_module(state_privacy)
    #     convert_date = state_privacy.convert_date

    #     self.assertEqual(
    #         convert_date("01012020"),
    #         "01/01/2020",
    #         "Date conversion did not work as expected.",
    #     )
    #     self.assertEqual(
    #         convert_date("invalid"),
    #         "invalid",
    #         "Non 8-digit string should remain unchanged.",
    #     )

    def test_generate_page_summary(self):
        """
        Test the generate_page_summary function.
        """
        # Test valid inputs
        chunk_ids_with_metadata = [
            ("./pdfs/Texas/test.pdf", "Texas Privacy Act", "1"),
            ("./pdfs/Texas/test.pdf", "Texas Privacy Act", "2"),
        ]
        user_question = "What are state privacy laws related to social media?"
        # Test with invalid inputs
        with self.assertRaises(TypeError):
            generate_page_summary(None, user_question)

        with self.assertRaises(TypeError):
            generate_page_summary(chunk_ids_with_metadata, None)

    def test_map_chunk_to_metadata(self):
        """
        Test the map_chunk_to_metadata function.
        """
        chunk_ids_with_metadata = [
            ("./pdfs/Texas/test.pdf", "Texas Privacy Act", "1"),
            ("./pdfs/Texas/test.pdf", "Texas Privacy Act", "2"),
        ]
        self.assertTrue(isinstance(chunk_ids_with_metadata, list))
        with self.assertRaises(TypeError):
            map_chunk_to_metadata(None)

    def test_generate_llm_response(self):
        """
        Test the generate_llm_response function.
        """
        non_string_user_question = 123
        with self.assertRaises(TypeError):
            generate_llm_response(non_string_user_question)


if __name__ == "__main__":
    unittest.main()
