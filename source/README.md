# The Utility Bill Decoder

A deterministic, offline CLI pipeline that extracts highly structured Level 1 information from K-Electric, LESCO, and IESCO electricity bills, and explains Level 2 answers to customer questions. 

## Python Version
Python 3.11+ (Tested on Python 3.14.4)

## Setup Steps
1. Navigate to the project directory containing `source/`.
2. Install the exact dependencies from `requirements.txt`:
   ```bash
   pip install -r source/requirements.txt
   ```
3. Copy the `.env.example` file to `.env` inside the `source/` folder and insert your valid API Key.
   ```bash
   cp source/.env.example source/.env
   ```

## Run Command
Process bills and generate `output/level1.csv` and `output/level2.csv`:
```bash
python source/main.py --bills test/bills --templates test/csv --out output
```
To run the preflight checks on the generated output:
```bash
python source/scripts/preflight.py --out output --templates test/csv
```

## Architecture
The pipeline relies on a strict **"Extract, Verify, then Explain"** sequence:
1. **Preprocess (`preprocess.py`)**: Uses PIL to parse EXIF rotations and cleanly resize and contrast the image (avoiding hard binarization), sending ~1600px long-side optimized JPEGs to the API to save quota and preserve high accuracy.
2. **Extract (`extract.py` & `google.py`)**: Submits exactly ONE vision call to Gemini, utilizing structured output features with robust Pydantic schemas. It dynamically injects provider-specific glossaries from the `prompts/` directory to resolve mapping rules exactly.
3. **Verify (`validate.py`)**: Advisory logic that verifies mathematical sums (e.g. `sum(charges) == total_charges`), flagging warnings to the console without aggressively overriding printed numbers.
4. **Facts (`facts.py`) & Safe Evaluation (`safe_eval.py`)**: An isolated computation sandbox that processes all averages, mathematical shares, threshold counting, and sums strictly through python using a secure AST traversal pattern—preventing the LLM from executing poor math.
5. **Explain (`explain.py`)**: Implements two deterministic steps (Step A: plan AST mathematical expressions; Step B: answer using the mathematically proven facts). Grounding checks ensure zero hallucinations.
6. **Writer (`writer.py`)**: Strict, deterministic JSON schema dumper enforcing proper CSV escaping and `null` enforcement.
7. **Cache & Throttling (`cache.py`)**: The Google Provider uses deterministic caching (hashing image bytes, prompts, model info) for zero-cost reruns `--verify-rerun`, along with exponential backoff on `HTTP 429/500/503`.

## AI Usage
* **Models:** `gemini-3.5-flash-lite` (via the official `google-genai` SDK) is used exclusively for all extraction and reasoning. *Fallback model `gemini-3.1-flash-lite` is implemented for 429/503 fallback exhaustion.*
* **Services/APIs:** Google AI Studio API.
* **AI Coding Tools:** Google Deepmind's Antigravity system.
* **Other tools:** Streamlit (UI).

## Run the Portfolio UI
Start the interactive retro pixel-art demo application with:
```bash
streamlit run app.py
# or: streamlit run source/demo_app.py
```

## Design Choices
* **Facts-First Python AST Evaluation**: LLMs are notoriously unreliable at evaluating large sums across varying list boundaries. The design offloads calculation into a heavily restricted AST string parser (`safe_eval`), making answers perfectly precise and mathematically valid.
* **Advisory Level 1 Checks**: Enforcing a strict "extract as printed" mandate, `validate.py` performs warnings instead of overwriting mathematically inconsistent bill misprints, adhering flawlessly to instructions.
* **Pydantic Driven**: To avoid the known `additionalProperties` limitations of Gemini's Developer structured schema generation, the application uses completely declarative object lists in `explain.py` and `schema.py`.
* **Zero API Cost Verification**: Advanced hashing in the wrapper intercepts extraction *and* step-b-step reasoning generation, so `--verify-rerun` executes instantly with strictly zero cost.

## Limitations
* No heavy OCR preprocessing implies blurry or intensely smudged grey-boxes heavily obscure line extraction.
* Grounding strictness will replace answers with a structured fallback response if the LLM hallucinates an arbitrary number out of bounds from the calculated facts list.
