from io import StringIO
import sys
import textwrap
import os
from urllib.request import urlretrieve
import numpy as np

import boto3

from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockLLM, BedrockEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader


# Set the RAG prompt template
# This is the default value
# When this script is run from Prompfoo or with the --prompt_template parameter
# this value will be overwritten

default_prompt_template = """

Human: Use the following pieces of context to provide a concise answer to the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
<context>
{context}
</context

Question: {question}

Assistant:"""


# Set the RAG query
# This is the default value
# When this script is run from Prompfoo or with the --query parameter
# this value will be overwritten

default_query = """Is it possible that I get sentenced to jail due to failure in filings?"""


# Set the default model_id to use for RAG
# This implementation is set up for Amazon Bedrock, if you are using an alternative provider
# you will need to make that configuration change as a custom update to this script

default_model_id = "claude-3-5-haiku-20241022"


# Set verbose to False once you have the configuration working as desired
# to reduce the logging output
# When set to True, Promptfoo will receive log/junk in its input, and will not give good results

verbose = False


def validate_cached_index(file_path) -> bool:
    """
        Validate the input file_path for the test data is accessible.
        If the file referenced does not exist, is a not standard file, or cannot be accessed, message the user and exist
        :return: int: 200 if all validations passed
        """
    # first check the top-level directory exists
    if not os.path.exists(file_path):
        return False
    if not os.path.isdir(file_path):
        return False
    # check the two files exist
    if not os.path.isfile(os.path.join(file_path, "index.faiss")):
        return False
    if not os.path.isfile(os.path.join(file_path, "index.pkl")):
        return False
    return True

def validate_source_data(file_path) -> bool:
    """
        Validate the input file_path for the test data is accessible.
        If the file referenced does not exist, is a not standard file, or cannot be accessed, message the user and exist
        :return: int: 200 if all validations passed
        """
    # first check the top-level directory exists
    if not os.path.exists(file_path):
        return False
    if not os.path.isdir(file_path):
        return False
    # check that the path contains one or more .PDF files
    if not any(f.endswith(".pdf") for f in os.listdir(file_path)):
        return False
    return True

def setup_source_data():
    os.makedirs("data", exist_ok=True)
    files = [
        "https://www.irs.gov/pub/irs-pdf/p1544.pdf",
        "https://www.irs.gov/pub/irs-pdf/p15.pdf",
        "https://www.irs.gov/pub/irs-pdf/p1212.pdf",
    ]
    for url in files:
        file_path = os.path.join("data", url.rpartition("/")[2])
        urlretrieve(url, file_path)

def print_ww(*args, width: int = 100, **kwargs):
    """Like print(), but wraps output to `width` characters (default 100)"""
    buffer = StringIO()
    _stdout = None
    try:
        _stdout = sys.stdout
        sys.stdout = buffer
        print(*args, **kwargs)
        output = buffer.getvalue()
    finally:
        sys.stdout = _stdout
    for line in output.splitlines():
        print("\n".join(textwrap.wrap(line, width=width)))


boto3_bedrock = boto3.client('bedrock-runtime', region_name='eu-west-2')

# - configure the embedding models that will be used
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", client=boto3_bedrock)

stored_faiss_index = "llm_faiss_index"

if not validate_cached_index(stored_faiss_index):
    if verbose:
        print("Creating new FAISS index")

    # This code block should be modified / deleted once you have set up your own data
    if not validate_source_data("data"):
        print("Setting up source data")
        setup_source_data()

    loader = PyPDFDirectoryLoader("./data/")

    documents = loader.load()
    # - in our testing Character split works better with this PDF data set
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a chunk size for initial experimentation
        chunk_size = 1000,
        chunk_overlap  = 100,
    )
    docs = text_splitter.split_documents(documents)

    try:
        # this is a system to check if the embedding model is configured and ready for use
        # and the model is accessible
        print("Sample of the document chunk: ", docs[0].page_content)
        sample_embedding = np.array(bedrock_embeddings.embed_query(docs[0].page_content))
        print("Sample embedding of a document chunk: ", sample_embedding)
        print("Size of the embedding: ", sample_embedding.shape)

    except ValueError as error:
        if "AccessDeniedException" in str(error):
            print(f"\x1b[41m{error}\
            \nTo troubeshoot this issue please refer to the following resources.\
             \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
             \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n")
            class StopExecution(ValueError):
                def _render_traceback_(self):
                    pass
            raise StopExecution
        else:
            raise error

    vectorstore_faiss = FAISS.from_documents(docs, bedrock_embeddings)
    vectorstore_faiss.save_local("llm_faiss_index")
else:
    if verbose:
        print("Loading cached FAISS index")
    vectorstore_faiss = FAISS.load_local("llm_faiss_index",
                                         bedrock_embeddings,
                                         allow_dangerous_deserialization=True)

# Wrap the FAISS vector store with LangChainIndex
wrapper_store_faiss = VectorStoreIndexWrapper(vectorstore=vectorstore_faiss)

if verbose:
    query_embedding = vectorstore_faiss.embedding_function.embed_query(default_query)
    np.array(query_embedding)

    relevant_documents = vectorstore_faiss.similarity_search_by_vector(query_embedding)
    print(f'{len(relevant_documents)} documents are fetched which are relevant to the query.')
    print('----')
    for i, rel_doc in enumerate(relevant_documents):
        print_ww(f'## Document {i+1}: {rel_doc.page_content}.......')
        print('---')

# processing command line arguments options for this script
def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--llm_id', type=str, required=False, help='The LLM to use for the RAG process')
    parser.add_argument('--prompt_template', type=str, required=False, help='The prompt template to use for the RAG process')
    parser.add_argument('--query', type=str, required=False, help='The query to use for the RAG process')
    return parser.parse_args()


# If running as a script, then execute the following
# When called from Promptfoo, given the configuration provided, values for --llm_id and --prompt_template
# and --query will be passed
# For stand-alone testing these values do not need to be provided
# and the values specified earlier in this script will be used instead

if __name__ == "__main__":

    args  = parse_args()

    # print(f"Using LLM: {args.llm_id}")
    # print(f"Using prompt template: {args.prompt_template}")
    # print(f"Using query: {args.query}")

    # configure the Bedrock LLM that will be used
    llm_to_use = args.llm_id if args.llm_id else default_model_id
    llm = ChatAnthropic(model=llm_to_use)

    # configure the base prompt template that will be used
    prompt_template_to_use = args.prompt_template if args.prompt_template else default_prompt_template

    # configure the base query that will be used
    query_to_use = args.query if args.query else default_query

    llm_prompt = PromptTemplate(template=prompt_template_to_use, input_variables=["context", "question"])

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore_faiss.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": llm_prompt}
    )
    answer = qa.invoke({"query": query_to_use})
    print_ww(answer['result'])
