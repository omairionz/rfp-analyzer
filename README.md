# RFP-Analyzer

> Created by @omairionz

This project enables the extraction of structured data and compliance requirements from government-written `Request for Proposals`.

## Installing / Getting Started

1. Do the following before installing the dependencies found in `requirements.txt` file because of current challenges installing `onnxruntime` through `pip install onnxruntime`. 

      - For MacOS users, a workaround is to first install `onnxruntime` dependency for `chromadb` using:

         ```python
          conda install onnxruntime -c conda-forge
         ```
        See this [thread](https://github.com/microsoft/onnxruntime/issues/11037) for additional help if needed.
   
     - For Windows users, follow the guide [here](https://github.com/bycloudai/InstallVSBuildToolsWindows?tab=readme-ov-file) to install the Microsoft C++ Build Tools. Be sure to follow through to the last step to set the environment variable path.
 
2. Run this command to install dependencies inside `requirements.txt`.
   
```python
uv pip install -r requirements.txt
```
#### Running Project

1. Simply run `analyze.py` inside the CLI using the following command.

```python
python analyze.py
```

#### API Keys

This project uses **Anthropic API** for LLM calls and **OpenAI API** for vector embeddings.

Use the following links to create your API keys:
> API Keys: [OpenAI API](https://platform.openai.com/api-keys "OpenAI API Keys Homepage") and [Anthropic API](https://platform.claude.com/settings/keys "Anthropic API Keys Homepage")

## Features / Outputs

This project includes '4 tiers' of data and requirements extraction.

1. Hard Facts & Structured Data
2. Submission Requirements
3. Evaluation Criteria
4. Technical Scope

#### Output

PFD input is processed by the LLM and is given `.json` outputs, all organized inside a dedicated `/outputs` folder.

Each solicitation (RFP) is identified and organized in separate folders inside `/outputs` with each folder containing separate `tier#.json` files.

Output Structure: 

`/output/[solicitation #]/tier1.json`

`/output/[solicitation #]/tier2.json`

`/output/[solicitation #]/tier3.json`

`/output/[solicitation #]/tier4.json`

## Credits 

This project was made by **@omairionz** and the debugging of **Claude**.

Portions of the data ingestion were originally created by @pixegami

> Link to the video: [RAG+Langchain Python Project: Easy AI/Chat For Your Docs](https://www.youtube.com/watch?v=tcqEUSNCn8I&ab_channel=pixegami).










































