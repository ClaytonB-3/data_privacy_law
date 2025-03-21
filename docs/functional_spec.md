# Functional Specification

## Background
In the United States, there is no comprehensive privacy law, and the existing laws are often indecipherable to the average person. This presents two key challenges:

1. Consolidating all privacy-specific and privacy-related laws into a single platform by filtering them from the vast array of existing laws.  
2. Enabling users to interact with these laws in a human-readable format through natural language queries.

Our goal is to create a platform that addresses both challenges by providing easy access to privacy laws and related regulations in one place. Additionally, we aim to allow users to query this database in plain language, making legal information more accessible and understandable for the average person.

---

## User Profile

### Average Citizen
- **Expertise**: Limited knowledge of both the legal domain and computing.  
- **Requirement**: The platform must have a simple, intuitive UI that enables easy navigation and allows for plain language queries.  
- **Outcome**: They can understand the content of the laws in accessible terms.

### Legal Domain Expert
- **Expertise**: Deep understanding of the law but limited computing knowledge.  
- **Requirement**: Simple, intuitive UI with the added ability to trace output back to the original legal documents.  
- **Outcome**: Query results must include references to the specific documents or sections used to generate responses (e.g., “referenced from Bill HB 1672 of 2025”).

### Technical App Support
- **Expertise**: Limited understanding of the law, but significant computing knowledge. Able to run python files from the command line.
- **Requirement**: The platform must provide the ability to rebuild the database if it is corrupted and to add new pdfs.
- **Outcome**: Adding documents must be easy and doing a full reset of the database must require simple commands.

---

## Data Sources

### Original Data Sources
1. **LegiScan**  
2. **Openstates**  
3. **IAPP Databases**

**Data Management**
The data from these data sources exists in pdfs. In order to be able to work with the data we will do the following:
1. Convert the pdfs to text
2. Generate metadata for the document through an LLM
3. Chunk the texts into smaller pieces and convert to vectors
4. Store the vectors along with the text of the chunk and metadata of the PDF in a vector database. 

The above process allows us to query the data by slicing on document metadata or by finding chunks similar to a natural language query using vector similarity. 

### Generated Data Sources
- A **vector database** containing word embeddings and metadata about the bills.  
- This database will be used for faster generation of responses via LLMs.

---

## Use Cases

### 1. General Public in Washington (WA) – Understanding Financial Data Usage
**Scenario**: A resident of Washington wants to know how financial institutions can use their financial data.

**User Action**:
1. Select “WA”
2. Select “Financial Data” sector
3. Input: “Who can access my financial data stored in my bank?”

**Platform Response**:  
The web interface will provide the relevant bills and a context-aware, human-readable explanation, referencing specific quote(s) in the bill.

---

### 2. Legal Expert – Access to De-identified Health Data
**Scenario**: A privacy law expert wants to determine whether research institutions in Washington can access de-identified health data for analysis without patient consent.

**User Action**:
1. Select “WA”
2. Select “Health Data” sector
3. Input: “Can research and public health institutions access and analyze anonymous health data without patient consent?”

**Platform Response**:  
The web interface will display relevant legal provisions, along with additional details on any limitations or exceptions.
