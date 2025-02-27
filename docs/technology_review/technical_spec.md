# Technical Specification 

[Link to demos of each library used](https://drive.google.com/drive/folders/189A5Rd2ii0tr5pdyWXlaqp83j2qZdOWM?usp=sharing)
       
## Problem 1
We need a library to assist with coodinating the embedding of pdf text into vectors and storing to a vector database along with the metadata of the pdf text. This library will also be responsible for the retrieval of the most relevant vectors from the vector database based on a query and coordinating the retrieval of a summary of the most relevant vectors.

| Requirement | LlamaIndex | LangChain |
|-------------|----------|----------|
| Vector DB Input | True | True |
| Integrate with FAISS | True | True |
| Integrate with Gemini | True | True |
| Cost Effectiveness | Free | Free | 

### Vector Database Decision
Both of these libraries fufill all of our requirements. We will use LangChain for this task, as it more easily enables multi-step workflows that we may need to implement for explainability (quote retrieval) of our text summaries.

## Problem 2
We need an AL library/provider to cost effectively perform the following: embed our pdf texts into space efficient, quality vectors, and have an LLM to be able to query for summaries related to a text.


| Requirement | Google GenAI | OpenAI |
|-------------|----------|----------|
| Space Efficient Embeddings | 768 dimension text-embedding-004  | 1536 dimension text-embedding-3-small |
| Quality of Embeddings [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) | text-embedding-004 MTEB ranking 12 | text-embedding-3-small MTEB ranking 4 |
| Text Summarization LLM | Both provide similar results based on our tests | Both provide similar results based on our tests |
| Cost Effectiveness | [pricing:](https://ai.google.dev/gemini-api/docs/pricing) $0.10/$0.40 input/output per 1M tokens | [pricing:](https://platform.openai.com/docs/pricing) $0.15/$0.60 input/output per 1M tokens |
| API ease of use | Very similar between both model platforms | Very similar between both model platforms |

### AI Model Provider Decision 
Primarily due to the cost effectiveness of the Google GenAI models and the availability of the small embedding model, we will use Google GenAI for this task. 

## Problem 3
We need a vector database to cost effectively store the embeddings and metadata about the pdf texts. 

| Requirement | Chroma | FAISS |
|-------------|----------|----------|
| Cost Effectiveness | Free | Free |
| Supports metadata storage | True | True |
| Retrieval | True | True |
| Ease of use | We found this DB to be extremely difficult to use with unhelpful error messages and poor documentation | We were able to get a basic implementation up and running in a few hours |

### Vector Database Decision
Due to the difficulty of using the Chroma DB, we will use FAISS for this task. 

## Problem 4
We need to be able to display a front end interactive app with the ability to display a map, dataframes as tables, and a pdf viewer. 

| Requirement |  Streamlit | Dash |
|-------------|----------|----------|
| Interactive | True | True |
| Map | Built in functionality | Capable but requires more configuration |
| Dataframe | True | True |
| PDF Viewer | Not a standard out of the box component, but an indevelopment custom component | Built as an open source component, not a standard out of the box component |
| Summary | Generally easier and more straight forward to use, but less configuration | More configuarability, but more complex to set up as a result |

### Front End Decision
We will use Streamlit for this task, as it is generally easier and more straight forward to use, with all the configuration complexity we need. Neither of these libraries have out of the box component for a pdf view, but both are capable. 

