# Installing Promptfoo

Promptfoo is the primary test tool that we will be using for the end-to-end evaluation of the RAG solution.
This is a powerful, industry leading, solution that is free and easy to get started with, 
which also happens to have lots of options to explore.

It is recommended for this evaluation that you install Promptfoo onto the same compute instance that
you have install the capstone_rag application. 

## Pre-requisites
A. `node.js`: Promptfoo is a Node.js based application. 
Therefore, to install it, depending on your configuration, you may also need to install Node.js (e.g., npm, npx).

For me, running on a standard Amazon Linux instance, which did not have Node.js support, I did the following:

`curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash`

`source ~/.bashrc`

`nvm install --lts`

`node -e "console.log('Running Node.js ' + process.version)"`

`npm --version`

You may choose a different route. The `node.js` website provides many options: https://nodejs.org/en/download/package-manager

# Installation

1. Installing Promptfoo: Once `npm` is installed, installing `promptfoo` is easy. 
I used the following command line:

`npm install -g promptfoo`

Verify the installation with the following:

`promptfoo --version`

You can choose other options for installing Promptfoo than `npm`. 
The `promptfoo` website describes addition methods, see: https://www.promptfoo.dev/docs/installation/.
This guide assumes that you are using `npm`. Adjust accordingly, if you do otherwise.

2. Initializing Promptfoo: 
Start this short process by checking that you are in the directory where you install the `capstone_rag` application.
We will do all our testing and experimentation from here. 
To initialize `promptfoo`  use the following single line command:

`promptfoo init`

This will process will ask you some questions which will be used to create an initial `promptfooconfig.yaml`.
We will be overwriting that `promptfooconfig.yaml` in a couple of steps, so your answers will not have impact.
Note that, there are options to generate default test content for Amazon Bedrock, OpenAI, and Anthropic LLMs.
This may come in useful later.

3. Establish the initial test configuration for the `capstone_rag` application. 
To do this there are two things, the second of which is optional. 

First, copy the file `promptfooconfig_capstone_starter.yaml` to overwrite `promptfooconfig.yaml`

`cp promptfooconfig_capstone_starter.yaml promptfooconfig.yaml`

Second, and optionally, if you have an Anthropic API key, set and export that value in your environment. 
One way of doing this is:

`export ANTHROPIC_API_KEY="sk-ant-....YOUR_KEY_SPECIFICS...."`

This is used for one style of the testing that you will like want to use, called `llm-rubrik`.
You can use other LLM service providers than Anthropic for this task, including Bedrock.
Using an alternative to the one given here, is a good exercise to try, if you have time.

If you don't have a key, tests using the evaluation method `llm-rubrik` will fail with this configuration.
In which case it is recommended that you delete or modify those tests.

4. System test your installation by running the following command:

`promptfoo eval`

This is the command that is use most with Prompfoo. 
It drives the set of tests that are defined in the test configuration file.
You will see some successes and failures of the tests in the report that is produced.

The FAIL test instances should all be due to the content produced by the LLM not matching the test definition.
There should not be any configuration failures, unless 
    (a) the Anthropic Key has not been set, and,
    (b) the test that has the `llm-rubrik` that calls Anthropic, 
"I am self-employed can I expense dinners with clients?", has not been changed.

Once you have the tests running with repeated test runs using `promptfoo eval`, you have completed the system test process.

Well done!!




