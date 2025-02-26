# Technical Specification 
       
## Problem 1
We need a library to assist with coodinating the embedding of pdf text into vectors and storing to a vector database along with the metadata of the pdf text. This library will also be responsible for the retrieval of the most relevant vectors from the vector database based on a query and coordinating the retrieval of a summary of the most relevant vectors.

| Requirement | Google GenAI | OpenAI |
|-------------|----------|----------|
| Vector DB Input |   | |
| Vector Database |  |  |
| Retrieval |  |  |
| Summary |  |  |

## Problem 2
We need an AL library/provider to cost effectively perform the following: embed our pdf texts into space efficient, quality vectors, and have an LLM to be able to query for summaries related to a text.


| Requirement | Google GenAI | OpenAI |
|-------------|----------|----------|
| Space Efficient Embeddings | 768 dimension text-embedding-004  | 1536 dimension text-embedding-3-small |
| Quality of Embeddings [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) | text-embedding-004 MTEB ranking 12 | text-embedding-3-small MTEB ranking 4 |
| Text Summarization LLM | Both provide similar results based on our tests | Both provide similar results based on our test