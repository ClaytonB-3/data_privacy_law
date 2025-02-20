# Component Specification

---

## Visualization Manager-P1

### What it Does
- A basic Web interactive homepage.  
- Accepts user queries and forwards them to the Data Manager for processing.  
- May provide filtering options by state and sector for better navigation.  
- Receives responses from the Model Manager and displays them in the Web interactive UI.

### Input
- State (from user)  
- Sector (from user)  
- Prompt (from user)  
- PDF page of finding (from Model Manager)  
- Answer to question (from Model Manager)  
- Supporting context to question (from Model Manager)

### Output
- LLM response  
- PDF of doc  
- Quote from doc  

---

## Data Manager

### What it Does
- Queries the vector database for getting all the relevant bills.  
- When a user inputs a question (prompt), it converts the prompt into vector embeddings and retrieves relevant context to feed into the Model Manager for response generation.

### Input
- State  
- Sector  
- Prompt  

### Output
- Possible relevant context in related bills  
- Page each piece of context is on  
- Title of the bill, year when bill was drafted  

---

## Large Language Model

### What it Does
- Summarizes relevant sections of bills based on queries and returns them to the user.

### Input
- Query comprised of enriched user question and relevant context from PDFs  

### Output
- Answer to question  
- Quote(s) related to the question  
- A page number for each quote  
- File name of PDF  

---

## Model Manager

### What it Does
- An LLM-based Model Holder.  
- Adds additional clarifying details to user prompts to ensure they are clear, well-structured, and unambiguous.  
- Provides LLM response and sends it to the Visualization Manager.

### Input
- User Input Prompts  
- Relevant context in related bills  

### Output
- LLM response  

---

## Data Processor

### What it Does
- Generates vector embeddings from provided PDFs and stores them in a vector database.  
- Tags bills with state and sector information.

### Input
- All data privacy related bills in all states and their metadata  
- Embedding model  

### Output
- Vector databases based on chunks of text in bills  

---

## Visualization Manager-P2 (Stretch Feature)

### What it Does
- Displays a color-coded map indicating the number of privacy-related laws in each state.

### Input
- State  

### Output
- The number of privacy-related laws in each state.  

---

## Visualization Manager-P3 (Stretch Feature)

### What it Does
- A dedicated web page summarizing the 7 principles of GDPR.  
- Allows users to query GDPR-related topics similarly to other pages.  
- Helps users compare EU GDPR regulations with state-specific privacy laws, offering insights into how their state’s stance aligns with GDPR’s stringent privacy standards.

### Input
- State  
- Sector  

### Output (TBD)
- A table that compares GDPR with the state’s data privacy law  
- An LLM response  

---

## Visualization Manager-P4

### What it Does
- Takes data from the Data Manager and displays relevant laws on a page for users to see.

### Input
- State  
- Sector  

### Output
- Table of relevant laws
