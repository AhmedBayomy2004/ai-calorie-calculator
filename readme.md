# 🍽️ AI Calorie & Nutrition Calculator

An end-to-end, AI-powered nutrition application that converts free-form natural language meal descriptions (in English or Arabic) into structured macro breakdowns and caloric totals.

The system leverages **Qwen2.5-7B-Instruct** (4-bit quantized) for entity extraction and translation, paired with **FAISS** vector search over a 40,000+ USDA food database to provide accurate nutrition estimates.

---

## 🌟 Key Features

* **Natural Language Meal Parsing**: Converts entries like *"2 boiled eggs, an apple, and 200g of grilled chicken breast"* into structured food entities and portion weights.
* **Bilingual Support (English & Arabic)**: Automatically detects Arabic input (e.g., *"أكلت بيضتين مسلوقين وتفاحة"*), translates it to English for precise vector retrieval, and translates the final itemized breakdown back to Arabic.
* **RAG & FAISS Vector Matching**: Embeds queries using `sentence-transformers/all-MiniLM-L6-v2` and searches an indexed USDA food database.
* **Smart 3-Tier Match Heuristic**: Prevents false matches (e.g., matching plain "chicken" to a "chicken sandwich") by prioritizing standard SR Legacy / Foundation whole foods over composite branded items.
* **Interactive Streamlit Dashboard**: Features real-time metric cards, a Plotly macro distribution donut chart (Protein/Carbs/Fat), quick-preset sample buttons, and session-state persistence.
* **Decoupled API Architecture**: FastAPI backend hosted on GPU runtimes (Kaggle/Colab) exposed securely via ngrok tunnels to the Streamlit frontend.

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           Streamlit Frontend                            │
│  • Meal Input (EN / AR)  • Presets  • Plotly Charts  • Itemized Table   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP POST /calculate
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             FastAPI Backend                             │
│  1. Language Detection (Regex)                                          │
│  2. Forward Translation (AR → EN via Qwen2.5-7B)                        │
│  3. LangChain Structured JSON Entity Extraction                         │
│  4. FAISS Vector Search (all-MiniLM-L6-v2) + 3-Tier USDA Filter         │
│  5. Gram Portion & Macro Calculation                                    │
│  6. Batch Back-Translation (EN → AR via Qwen2.5-7B)                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit, Plotly Express, Pandas
* **Backend Framework:** FastAPI, Uvicorn, PyNgrok, Nest-Asyncio
* **LLM Engine:** Qwen/Qwen2.5-7B-Instruct (Quantized using `bitsandbytes` NF4)
* **Frameworks & Orchestration:** LangChain, PyTorch, Hugging Face `transformers` & `accelerate`
* **Vector Search & RAG:** FAISS (`faiss-cpu`), Sentence-Transformers (`all-MiniLM-L6-v2`)
* **Dataset:** USDA Comprehensive Food Dataset (~40,000 records)

---

## 📁 Project Structure

```text
.
├── app.py                      # Streamlit frontend dashboard
├── calorie_calculator.ipynb    # Kaggle GPU notebook (Model, FAISS Index, FastAPI, ngrok)
├── requirements.txt            # Python dependencies for the frontend
└── README.md                   # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

1. A Kaggle or Google Colab account with GPU access (T4 / P100 / L4).
2. An [ngrok account](https://ngrok.com/) and auth token (for tunneling the API).
3. Python 3.10+ installed locally for running the Streamlit dashboard.

---

### Step 1: Launch Backend (Kaggle Notebook)

1. Open `calorie_calculator.ipynb` in Kaggle with **GPU Accelerator** enabled.
2. Add your ngrok authtoken to Kaggle Secrets (`Add-ons` -> `Secrets` -> `NGROK_AUTHTOKEN`).
3. Run all cells:
   * Installs `transformers`, `bitsandbytes`, `langchain`, `faiss-cpu`, and `sentence-transformers`.
   * Loads `Qwen/Qwen2.5-7B-Instruct` in 4-bit NF4 quantization (~5.5 GB VRAM).
   * Embeds and indexes the USDA food dataset in FAISS.
   * Starts the FastAPI server and creates a public ngrok URL.
4. Copy the generated public API URL from the final cell output (e.g., `https://xxxx.ngrok-free.dev`).

---

### Step 2: Launch Frontend (Streamlit)

1. Clone this repository:
   ```bash
   git clone https://github.com/AhmedBayomy2004/ai-calorie-calculator.git
   cd ai-calorie-calculator
   ```

2. Install frontend dependencies:
   ```bash
   pip install streamlit requests pandas plotly
   ```

3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

4. Paste your public ngrok URL into the **Sidebar API Configuration** field in the web UI.

---

## 💡 How the RAG Pipeline Works

1. **Entity Extraction**: The LLM parses the input text and extracts individual food components along with estimated gram weights (inferring standard sizes if quantities like "2 eggs" are given).
2. **FAISS Retrieval**: Each extracted food item is converted into a 384-dimensional dense vector using `all-MiniLM-L6-v2`. The top 15 nearest neighbors are fetched from the FAISS L2 index.
3. **Filtering Heuristic**:
   * **Priority 1**: Match against standard, unbranded whole-food records (SR Legacy / Foundation data types).
   * **Priority 2**: Match against branded items while filtering out composite dish keywords (e.g., excluding "sandwich", "pizza", "burger" when searching for single ingredients).
   * **Priority 3**: Fallback to top vector match.
4. **Macro Scaling**: Calculated calories, protein, carbs, and fat are dynamically scaled based on the weight multiplier:

$$\text{Multiplier} = \frac{\text{Weight (grams)}}{100}$$

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).