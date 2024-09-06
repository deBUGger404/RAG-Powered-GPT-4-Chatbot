import argparse
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
# from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from IPython.display import Markdown, HTML, display  

import argparse
import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document


# // READ DATA AND CREATE CHROMA DB

def load_documents(DATA_PATH):
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(CHROMA_PATH2, embedding_function, chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH2, embedding_function=embedding_function
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        # db.persist()
    else:
        print("No new documents to add")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id
        # break
    return chunks

# def clear_database():
    # if os.path.exists(CHROMA_PATH):
        # shutil.rmtree(CHROMA_PATH)

# // LOAD CHROMA DB AND QUERY THE USER QUESTION
def printmd(string):
    display(Markdown(string))

# CHROMA_PATH = "/home/rakesh/chroma"

DOCSEARCH_PROMPT_TEXT = """## On your ability to answer questions based on fetched documents (sources):
- Given extracted parts (CONTEXT) from one or multiple documents, answer the question thoroughly with citations/references.
- If there are conflicting information or multiple definitions or explanations, detail them all in your answer.
- In your answer, **You MUST use** all relevant extracted parts that are relevant to the question.
- **YOU MUST** place inline citations directly after the sentence they support using this Markdown format: `[[number]](url?query_parameters)`.
- The reference **MUST** be taken directly from the `id` found in the `source:` section of the extracted parts. Do not create a reference from any other part of the content; only use the `id` provided in the `source:` of the extracted parts.
- Reference document's URL can include query parameters. Include these references in the document URL using this Markdown format: [[number]](url?query_parameters)
- **You MUST ONLY answer the question from information contained in the extracted parts (CONTEXT) below**, DO NOT use your prior knowledge.
- Never provide an answer without references.
- Below your output, list the references used in the output as per the examples below.
- The examples provided are solely for reference and demonstration purposes; do not use them in your output.
- You will be seriously penalized with negative 10000 dollars if you don't provide citations/references in your final answer.
- You will be rewarded 10000 dollars if you provide citations/references on paragraph and sentences.

# Examples
- These are examples of how you must provide the answer:

--> Beginning of examples

Example 1:

Total hip replacement (THR) is a highly successful and cost-effective surgical procedure aimed at relieving pain and restoring function. Cemented THRs have shown superiority in short-term outcomes, particularly in pain relief and early weight-bearing, when compared to uncemented THRs [[1]](data/Abdulkarim_2013.pdf:6:4). However, there are instances where uncemented THRs are preferred due to specific patient characteristics or long-term considerations [[2]](data/Abdulkarim_2013.pdf:0:7). Further research is needed to identify patient subgroups that would benefit most from either approach [[3]](data/Abdulkarim_2013.pdf:0:2).

- Reference:
  1. data/Abdulkarim_2013.pdf:6:4
  2. data/Abdulkarim_2013.pdf:0:7
  3. data/Abdulkarim_2013.pdf:0:2

Example 2:

A meta-analysis comparing cemented and uncemented total hip replacements (THRs) has highlighted the advantages and disadvantages of both methods. Cemented THRs are associated with lower revision rates due to aseptic loosening in certain patient groups [[1]](data/Abdulkarim_2013.pdf:10:9). Conversely, uncemented THRs have been found to offer better integration with the bone in younger, more active patients, potentially leading to better long-term outcomes [[2]](data/Abdulkarim_2013.pdf:9:9). The choice between these methods should be guided by patient-specific factors and long-term goals [[3]](data/Abdulkarim_2013.pdf:0:2).

- Reference:
  1. data/Abdulkarim_2013.pdf:10:9
  2. data/Abdulkarim_2013.pdf:9:9
  3. data/Abdulkarim_2013.pdf:0:2

Example 3:

# Comparative Outcomes of Cemented vs. Uncemented Total Hip Arthroplasty

The table below summarizes key findings from studies comparing cemented and uncemented THRs.

| Outcome                  | Cemented THR      | Uncemented THR    | Reference                                          |
|--------------------------|-------------------|-------------------|----------------------------------------------------|
| **Pain Relief**          | Superior          | Inferior          | [[1]](data/Abdulkarim_2013.pdf:6:4)                |
| **Revision Rate**        | Lower             | Higher            | [[2]](data/Abdulkarim_2013.pdf:10:9)               |
| **Bone Integration**     | Lower             | Higher            | [[3]](data/Abdulkarim_2013.pdf:9:9)                |
| **Early Weight-bearing** | Superior          | Inferior          | [[4]](data/Abdulkarim_2013.pdf:6:4)                |

### Insights

- **Pain Management:** Cemented THRs offer superior pain relief and early mobility compared to uncemented THRs [[1]](data/Abdulkarim_2013.pdf:6:4).
- **Longevity:** Uncemented THRs might be more suitable for younger, more active patients, providing better long-term outcomes through improved bone integration [[2]](data/Abdulkarim_2013.pdf:9:9).
- **Procedure Selection:** The decision between cemented and uncemented THRs should be made considering the patient’s age, activity level, and specific health conditions [[3]](data/Abdulkarim_2013.pdf:0:2).

- Reference:
  1. data/Abdulkarim_2013.pdf:6:4
  2. data/Abdulkarim_2013.pdf:10:9
  3. data/Abdulkarim_2013.pdf:9:9
  4. data/Abdulkarim_2013.pdf:0:2

<-- End of examples

"""

DOCSEARCH_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", DOCSEARCH_PROMPT_TEXT + "\n\nCONTEXT:\n{context}\n\n"),
        MessagesPlaceholder(variable_name="history", optional=True),
        ("human", "{question}"),
    ]
)


def get_openai_callback(input, output):
    input_cost = (input*0.03)/1000
    output_cost = (output*0.06)/1000
    return input_cost + output_cost
