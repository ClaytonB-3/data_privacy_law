# Milestones and Tasks

## Decide on technologies used to execute project 
- Decide on vector database provider  
- Decide where we will store actual PDFs  
- Decide on LLM  
- Decide on algorithm for determining similarity of query to vector chunks  
- Decide on Dashboard platform  
- Decide on vector embedding method  
- Decide on visualization library  
- Decide on framework for managing prompts and interfacing data with LLM (e.g. LangChain, LlamaIndex)  

---

## Build Data Processor – Store PDFs and Metadata in Vector DB
- Chunk PDF into overlapping chunks and embed  
- Link state, sector, full text, page, document name of PDF to each chunk  
- Store in vector database  

---

## Build Data Manager
- Build function to embed prompt  
- Implement process to compare prompt to embedded chunk and select the top few  
- Implement fallback if no chunks meet certain similarity threshold  
- Return chunks and relevant metadata  

---

## Build Model Manager
- Write, test, finalize system prompt including content and structure of response for LLM  
- Write, test, finalize query with response format allowing for data extraction  
- Make prompt builder robust to nonsense inputs  

---

## Build Visualization Manager P1
- Build skeleton app that can run locally  
- Build state, sector, free text input that connects to Model Manager  
- Test end-to-end connection: user input → Data Manager → Model Manager → LLM → Visualization Manager  
- Build component to display list of relevant bills  
- Build PDF display component  
- Build response display component  
- Build quote display component  

---

## Write Unit Tests
- Write function to compare expectation and response from LLM  
- Define set of questions with known answers  
- Write tests  

---

## Stretch Milestones
- Build map visualization  
- Create map visualization  
- Design map hover tooltip  
- Implement steps 2–6 for federal privacy laws  
- Implement steps 2–6 for comprehensive privacy laws  
- Summarize and display GDPR  
