# RFP-Analyzer

> Created by @omairionz

A command-line and web tool that extracts structured intelligence from federal government `Request for Proposals (RFPs)`, turning a 60-page solicitation into a one-page debrief.

Here is a [demo.](https://youtu.be/6PNAc1vN_hM)

---
## Architecture

This tool uses a **hybrid extraction approach**, not pure RAG, since different types of RFP data require different extraction approaches.

- **Tier 1: Hard Facts**: Direct LLM extraction over the first ~10 pages. Solicitation numbers, dates, names, NAICS, set-aside type, etc., are all included.
- **Tier 2: Submission Requirements**: RAG-based retrival using ChromaDB. Submission instructions, page limits, formatting, etc., included.
- **Tier 3: Evaluation Criteria**: 2-pass RAG-based retrival using ChromaDB. Evaluation factors, evaluation criteria, past performance, etc., are included.
- **Tier 4: Technical Scope**: RAG intended.

All outputs include a score of `confidence` (`high`, `medium`, and `low`), a `fields_inferred` list for output verification, a `fields_missing` list for extraction performance, and a `model` field for the LLM used.

## Getting Started

#### Prerequisites

1. Do the following before installing the dependencies found in `requirements.txt` file because of current challenges installing `onnxruntime` through `pip install onnxruntime`. 

      - For MacOS users, a workaround is to first install `onnxruntime` dependency for `chromadb` using:

         ```bash
          conda install onnxruntime -c conda-forge
         ```
        See this [thread](https://github.com/microsoft/onnxruntime/issues/11037) for additional help if needed.
   
     - For Windows users, follow the guide [here](https://github.com/bycloudai/InstallVSBuildToolsWindows?tab=readme-ov-file) to install the Microsoft C++ Build Tools. Be sure to follow through to the last step to set the environment variable path.
 
2. Run this command to install dependencies inside `requirements.txt`.
   
```bash
uv pip install -r requirements.txt
```

#### Configure API Keys

Create a `.env` file at the project root and store keys.
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```
- [Get OpenAI API key](https://platform.openai.com/api-keys "OpenAI API Keys Homepage")
- [Get Anthropic API key](https://platform.claude.com/settings/keys "Anthropic API Keys Homepage")

> This project uses **Anthropic API** for LLM calls and **OpenAI API** for vector embeddings.

#### Adding Data
 
- Place PDF files in a subfolder under `data/`:

```
data/
└── RFP-1/
    ├── Solicitation.pdf
    └── Statement-Of-Work.pdf
```

## Running the Project

#### CLI
1. Simply run `analyze.py` inside the CLI using the following command.

```bash
python analyze.py
```
#### Web UI (StreamLit)
1. Simply run `app.py` inside the CLI using the following command.

```bash
streamlit run app.py
```
Opens a browser interface at `localhost:8501`. Select an RFP folder from the sidebar, toggle force-rebuild if you've added new PDFs, and click **Analyze**.

> [!WARNING]
> The prompts used in this system are proprietary and not available for public distribution. Please use your own prompts for testing purposes.

## Output

PDF input is processed by the LLM and is given `.json` outputs, all organized inside a dedicated `outputs` folder.

Each solicitation (RFP) is identified and organized in separate folders inside `outputs` with each folder containing separate `tier#.json` files.

Output Structure: 

```
outputs/
└── Solicitation_Number/
    ├── tier1.json    # Hard facts
    ├── tier2.json    # Submission requirements
    ├── tier3.json    # Evaluation Criteria
    └── tier4.json    # Technical Scope (planned)
```

## Credits 

Built by **[@omairionz](https://github.com/omairionz)**.

Developed with Claude Chat (Anthropic) as a pair programming collaborator.

Architecture decisions, extraction design, and prompt engineering by the author.

> PDF ingestion pattern adapted from [@pixegami](https://github.com/pixegami)'s [RAG + LangChain tutorial](https://www.youtube.com/watch?v=tcqEUSNCn8I).









































