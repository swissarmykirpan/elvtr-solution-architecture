# Installing the Capstone Rag Application
This brief guide is for installing the `capstone_rag.py` application. 
Hopefully you will find this a very straight-forward process. 
This process will also install the `rag_test_driver.py` application.
These applications are run from a linux command-line (or similar).

## Prerequisites for installing and running the application

A. `git`: Install git on your server if it is not already installed. 
On an AWS linux instance you might use the following:

`sudo yum install git`

B.`python 3.9 or greater`: Check that you are have Python 3.9 or higher installed and ready for use. 
This is required for the application. Use a command such as the following to determine this:

`python3 --version`

C.`aws`: The `capstone_rag` application will call Amazon Bedrock using `boto3`. 
The code needs to run in an environment where `aws boto3` is enabled.
If this is not enabled, the method of doing this will vary on your test environment.
A common approach to command line use is to install `aws tools` and run `aws configure`. 
The following url provides guidance on this process: 
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html#getting-started-install-instructions

D. The AWS account that you use has to be configured to allow `invoke` API calls to Amazon Bedrock.
Additionally, the Amazon Titan Bedrock models have to be configured for use. 
The Capstone project will use all three Amazon Titan LLMs and an Amazon Titan embeddings model.

## Installing the application code
1. Choose/create the directory where you want to run this application and other Capstone apps.
Then clone the `elvtr-solution-architecture` GitHub repository to that folder.

`git clone https://github.com/toby-fotherby/elvtr-solution-architecture.git`

`cd elvtr-solution-architecture/Class-15/Capstone-Assignment-III/`

2. Setup up a new Python virtual environment for the application.
Activate the new environment
Install the Python modules need for the application

`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

3. System test the installation, by running the application on the command line. 
The first run will exercise much of the code, and if the configuration of the AWS account is not sufficient,
as noted in the pre-requisites above, it will fail. Common issues are (i) AWS account not configured, 
(ii) Amazon Bedrock invoke model not configured, (iii) Amazon Titan Bedrock models not enabled for use. 

`python capstone_rag.py`

When this works correctly, on the first run it will output some logging information.
I will create and cache a FAISS vector datastore. 
This datastore will be used in subsequent running of the code, unless the related files in `llm_faiss_index` are deleted.
Run the rag application again. The second time, it will use the cached datastore and will have less latency.

4. System test the installation of the `rag_test_driver` application. 
This is standard Python code and will call the `capstone_rag` application.
First run the application with no arguments. This will show you its expected parameters.

`python rag_test_driver.py`

Then run it with the following command line options. 
This will test the three Amazon Titan LLMs that should be configured.

`python rag_test_driver.py llm_option_one prompt_option_one "which car expenses can be tax deductable?"`
`python rag_test_driver.py llm_option_two prompt_option_two "does everyone have to pay taxes?"`
`python rag_test_driver.py llm_option_three prompt_option_three "does everyone have to pay state taxes?"`

If the above commands run without error, you have completed the Python application installation process.
Well done.

