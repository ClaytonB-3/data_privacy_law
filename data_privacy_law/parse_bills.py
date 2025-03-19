"""
Parse PDF in selected folders and add into FAISS database.
Usage: python parse_bills.py -s <state1> -s <state2> ...
-s <state1> -s <state2> ...: Specify the state folders to parse. Enter 'all' for all available.
"""
import os
import argparse

from db_manager.faiss_db_manager import add_bills_to_faiss_index, write_bill_info_to_csv

us_states = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
    "Comprehensive"
]

def get_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--states", required=True, action="append", type=str,
                        help="Which folder's bill PDF would you like to parse?\
                              Enter 'all' for all available.")
    return parser.parse_args()

def main():
    """
    Main execution function.
    """
    # Create data directory if it doesn't exist
    if not os.path.exists("./db_manager/data"):
        os.makedirs("./db_manager/data")

    if not os.path.exists("./db_manager/faiss_index"):
        os.makedirs("./db_manager/faiss_index")

    args = get_args()
    state_inputs = args.states

    folders = os.listdir("pdfs/")
    if "all" in state_inputs:
        state_inputs += folders
        state_inputs.remove("all")

    print(f"Processed list: [{", ".join(state_inputs)}]")
    for state_input in state_inputs:
        state_input = state_input.strip().capitalize()

        if state_input not in us_states:
            print(f"{state_input} skipped: No such state or type of bill")
            continue
        if state_input not in folders:
            print(f"{state_input} skipped: No such state or type of bill in pdfs/")
            continue

        pdfs_folder = os.path.join("pdfs", state_input)
        if not os.path.exists(pdfs_folder):
            print(f"Folder not found: {pdfs_folder}")
            continue

        # Gather all PDF file paths in the specified folder.
        pdf_paths = [
            os.path.join(pdfs_folder, filename)
            for filename in os.listdir(pdfs_folder)
            if filename.lower().endswith(".pdf")
        ]

        if not pdf_paths:
            print(f"No PDF files found in folder: {pdfs_folder}")
            continue

        # Process the list of PDF paths and write into csv.
        bill_info_list = add_bills_to_faiss_index(pdf_paths)
        write_bill_info_to_csv(bill_info_list)

if __name__ == "__main__":
    main()
