# This script provides a facade to a Retrieval Augmented Generation (RAG) process for PromptFoo
# PromptFoo will call this script, this script will call RAG pipeline to get a response
# This makes it so there is less configuration needed in Promptfoo to change
# 1/ which LLM to use
# 2/ The prompt template string to use

# Modify this to match the specifics of your end-to-end RAG testing
# Ideally all you will need to do is update
# 1/ the llm_options to match the LLMs that you are testing with
# 2/ the prompt templates that you are testing with

import os, sys, subprocess

# Change this array to match the LLMs that you want to test with
# These model ids map the llm_option_one, llm_option_two, llm_option_three in the Promptfoo configuration
llm_options = ['amazon.titan-text-lite-v1', 'amazon.titan-text-express-v1', 'amazon.titan-text-premier-v1:0']


def get_llm_id_for_index(index: int) -> str:
    """
    This method will return the id of the LLM to use for the RAG process
    :return:
    """
    if index < 0 or index >= len(llm_options):
        raise ValueError("Index out of range")
    return llm_options[index]


def validate_arg_count(args) -> bool:
    """
    The intent of this method is to validate the number of command line arguments
    This script expects three arguments: the llm_option, the prompt_option and the query
    :param args: the command line arguments
    :return: true if the number of arguments is 4, false otherwise
    """
    return len(args) >= 4


def validate_llm_option_parameter(arg: str) -> bool:
    return arg in get_llm_parameter_options()


def get_llm_option_parameter_index(arg: str) -> int:
    if validate_llm_option_parameter(arg) is False:
        print(f"Usage: <llm_option> must be one of {get_llm_parameter_options()}")
        exit(1)
    options = get_llm_parameter_options()
    return options.index(arg)


def get_llm_parameter_options() -> [str]:
    return ['llm_option_one', 'llm_option_two',  'llm_option_three']


def get_llm_option_from_args(args) -> str:
    """
    This method will return the LLM option to use for the RAG process
    :param args: the command line arguments
    :return: the LLM option to use
    """
    llm_parameter_offset = 1
    if validate_arg_count(args) is False:
        print("Usage: python rag_test_driver.py <llm_option> <prompt_option> <query>")
        exit(1)
    if validate_llm_option_parameter(sys.argv[llm_parameter_offset]) is False:
        print(f"Usage: <llm_option> must be one of {get_llm_parameter_options()}")
        exit(1)
    else:
        target_llm = get_llm_id_for_index(get_llm_option_parameter_index(args[llm_parameter_offset]))
    return target_llm

# Change this and the following example prompt templates to match you needs
# These prompt templates map the prompt_option_one, prompt_option_two, prompt_option_three in the Promptfoo configuration

prompt_template_one = """

Human: Use the following pieces of context to provide a concise answer to the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
<context>
{context}
</context>

Question: {question}

Assistant:
"""

prompt_template_two = """
Use the following pieces of context to provide a concise answer to the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
<context>
{context}
</context>

Question: {question}
"""

prompt_template_three = """
You are an expert in US taxes.
Use the following pieces of context to provide a concise answer to the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Answer in a way that can be readily understood by a person with little specific tax knowledge.
<context>
{context}
</context>

Question: {question}
"""

def get_prompt_parameter_options() -> [str]:
    return ['prompt_option_one', 'prompt_option_two', 'prompt_option_three']


def validate_prompt_option_parameter(arg: str) -> bool:
    return arg in get_prompt_parameter_options()


def get_prompt_option_index(arg: str) -> int:
    if validate_prompt_option_parameter(arg) is False:
        print(f"Usage: <prompt_option> must be one of {get_prompt_parameter_options()}")
        exit(1)
    options = get_prompt_parameter_options()
    return options.index(arg)

def get_prompt_template_for_index(index: int) -> str:
    prompt_templates = [prompt_template_one, prompt_template_two, prompt_template_three]
    if index > len(prompt_templates) - 1 or index < 0:
        print(f"Usage: <prompt_option> must be one of {get_prompt_parameter_options()}")
        exit(1)
    return prompt_templates[index]

def get_prompt_template_from_args(args) -> str:
    """
    This method will return the prompt template to use for the RAG process
    :param args: the command line arguments
    :return: the prompt template to use
    """
    prompt_parameter_offset = 2
    if validate_arg_count(args) is False:
        print("Usage: python rag_test_driver.py <llm_option> <prompt_option> <query>")
        exit(1)
    if validate_prompt_option_parameter(sys.argv[prompt_parameter_offset]) is False:
        print(f"Usage: <prompt_option> must be one of {get_prompt_parameter_options()}")
        exit(1)
    else:
        prompt_template = get_prompt_template_for_index(get_prompt_option_index(args[prompt_parameter_offset]))
    return prompt_template

def get_query_from_args(args) -> str:
    """
    This method will return the query to use for the RAG process
    :param args: the command line arguments
    :return: the query to use
    """
    if validate_arg_count(args) is False:
        print("Usage: python rag_test_driver.py <llm_option> <prompt_option> <query>")
        exit(1)
    return args[3]


# The expectation is that this will called from Promptfoo
# Promptfoo does not provide --name argument tags
# Add to that, that we are using abstract identifiers with the Promptfoo configuration definitions
# That is why we have the code above to carefully parse the runtime arguments and clearly fail if they
# do not parse correctly

if  __name__ == "__main__":

    llm_to_use = get_llm_option_from_args(sys.argv)
    # print(f"Using LLM: {llm_to_use}")

    prompt_template_to_use = get_prompt_template_from_args(sys.argv)
    # print(f"Using prompt template: {prompt_template_to_use}")

    query_to_use = get_query_from_args(sys.argv)
    # print(f"Using query: {query_to_use}")

    python_cmd = "python"   # on some setups, this maybe python3

    path_to_capstone_03_base = os.path.abspath("capstone_rag.py")

    command = [python_cmd, path_to_capstone_03_base,
               "--llm_id", llm_to_use,
               "--prompt_template", prompt_template_to_use,
               "--query", query_to_use]

    output, error = subprocess.Popen(
        command, universal_newlines=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    print('returned value:', output)

