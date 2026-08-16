Here is the combined, copy-ready `README.md` formatted with accurate paths matching your GitHub repository structure:

```markdown
# ✉️ AI Email Drafting Agent

An autonomous multi-agent email generation system built using **CrewAI**, **Google Gemini**, and **Streamlit**. 

Instead of relying on a single monolithic prompt, this system decomposes email writing into a specialized two-stage cognitive pipeline: context distillation and copy generation.

---

## 📌 System Architecture


```

[User Input: Context + Recipient + Tone]
│
▼
┌─────────────────────────────────────────┐
│   Agent 1: Email Context Analyst        │
│   • Extracts core purpose & CTA         │
│   • Generates strategic subject lines   │
│   • Structures key talking points       │
└────────────────────┬────────────────────┘
│  (Structured Email Brief)
▼
┌─────────────────────────────────────────┐
│   Agent 2: Professional Email Writer    │
│   • Matches tone & persona              │
│   • Enforces concise body (<200 words)  │
│   • Inserts actionable placeholders     │
└────────────────────┬────────────────────┘
│
▼
[Polished Ready-to-Send Email]

```

---

## ✨ Features

- **Multi-Agent Orchestration:** Powered by CrewAI's sequential process workflow.
- **Contextual Handoff:** Upstream analysis feeds directly into downstream writing tasks via task context mapping.
- **Interactive UI:** Built with Streamlit for real-time parameter configuration (tone presets, recipient persona, raw notes).
- **CLI Support:** Optional command-line execution with `argparse`.
- **Export Ready:** One-click `.txt` download for generated email drafts.

---

## 🛠️ Tech Stack

- **Orchestration:** [CrewAI](https://github.com/crewAIInc/crewAI)
- **LLM Engine:** Google Gemini (`gemini-2.0-flash` / `gemini-1.5-flash-latest`)
- **Frontend UI:** Streamlit
- **Package & Environment Management:** Python 3.10+, `uv` / `pip`

---

## 📂 Repository Structure

```text
GEENAI-PROJECT-3/
├── project-1/              # Initial exploration project
├── project2/               # AI Email Drafting Agent
│   └── app.py              # CLI & Streamlit application
├── .env                    # Environment variables (API keys - gitignored)
├── .gitignore              # Git ignore rules
├── requirements.txt        # Shared dependencies
└── README.md

```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone [https://github.com/junjaanand/GEENAI-PROJECT-3.git](https://github.com/junjaanand/GEENAI-PROJECT-3.git)
cd GEENAI-PROJECT-3

```

### 2. Set Up Virtual Environment & Dependencies

Using `uv`:

```bash
uv venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
uv pip install -r requirements.txt

```

Or using standard `pip`:

```bash
python -m venv env
env\Scripts\activate     # Windows
# source env/bin/activate    # macOS/Linux
pip install -r requirements.txt

```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here

```

---

## 💻 Usage

### Run the Streamlit Web UI

```bash
streamlit run project2/app.py

```

Open `http://localhost:8501` in your browser.

### Run via Command Line (CLI)

```bash
python project2/app.py --context "Follow up on product demo from Tuesday" --tone "professional and friendly" --recipient "a potential client"
