# The Privacy Law Compass

![example workflow](https://github.com/ClaytonB-3/data_privacy_law/actions/workflows/build_test.yml/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/ClaytonB-3/data_privacy_law/badge.svg?branch=main)](https://coveralls.io/github/ClaytonB-3/data_privacy_law?branch=main)

__The Questions of Interest__ <br/>
Data privacy is one of the most widely discussed issues today, as users leave digital footprints everywhere. It is crucial for governments to safeguard users' information and prevent its misuse. 

Our project aims to explore how data privacy laws vary between state and federal levels, and then present it to interested users in a simplified and cogent manner. In this endeavour we will also examine how large language models (LLMs) can be deployed to summarize legal data, and also extract useful information from large documents that contain the bare act's of various governments regarding privacy law. 

__Project Goal__ <br/>
Our goal is to develop an interactive web tool that visualizes and compares data privacy regulations across different states. This tool will offer users an intuitive way to explore how privacy laws vary by state and evolve over time, providing valuable insights into regulatory trends and developments.

__Project Type__
- Present Data 

__Data Sources__
- LegiScan National Legislative Datasets
- Open States Bills Data
- International Association of Privacy Professionals (IAPP) : US State Privacy Legislation Tracker

## Setup Guide

### Prerequisites
- Python 3.12
- Conda (Miniconda or Anaconda)
- Git

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd data_privacy_law
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate data_privacy_law
```

Alternatively, you can create the environment manually:
```bash
conda create --name data_privacy_law python=3.12
conda activate data_privacy_law
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```bash
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="your_langchain_api_key"
LANGCHAIN_PROJECT="your_langchain_project_name"
GOOGLE_API_KEY="your_google_api_key"
```

Replace `your_langchain_api_key` and `your_google_api_key` with your actual API keys:
- Get a Google API key from [Google Cloud Console](https://console.cloud.google.com/)
- Get a LangChain API key from [LangSmith](https://smith.langchain.com/)

### Running the Application

1. Start the Streamlit application:
```bash
cd data_privacy_law
streamlit run app/Home.py
```

The application should open in your default web browser at `http://localhost:8501`

### Running Tests

To run the test suite:
```bash
python -m unittest discover
```

### Running pylint formatting checking

To run the pylint checking:
```bash
cd data_privacy_law
pylint .
```

### Troubleshooting
If having issues with the index delete the faiss_index folder and rebuild it by doing the following:
```bash
cd data_privacy_law
python parse_bills.py -s all
```