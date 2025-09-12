# 📄 Google Docs RAG Chatbot

A **Streamlit app** that lets you authenticate with Google, select your Google Docs, and chat with them using **LangChain + OpenAI + Chroma**.

## ✨ Features

* 🔑 Google OAuth2 login (Drive + Docs API)
* 📂 Browse your Google Docs and select which to use
* 📚 Text is chunked, embedded with OpenAI, and stored in **Chroma vector DB**
* 💬 Chat with your documents (retrieval-augmented generation, RAG)
* 🚀 Deployable on [Render](https://render.com/)

---

## ⚡️ Setup

### 1. Clone this repo

```bash
git clone https://github.com/ArpitaPani/googledocbot.git
cd googledocbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment variables

Create a `.env` file in the root:

```env
OPENAI_API_KEY=your_openai_api_key
```

For Google OAuth:

* Download your `credentials.json` from Google Cloud Console.
* Keep it **locally** (add it to `.gitignore`).

When deploying to Render, instead of uploading the file:

* Add a new environment variable:

  * Key: `GOOGLE_OAUTH_JSON`
  * Value: paste the entire JSON content from `credentials.json`.

---

## 🔑 Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2. Create OAuth 2.0 credentials.
3. Enable APIs:

   * **Google Drive API**
   * **Google Docs API**
4. Add redirect URI:

   ```
   http://localhost:8501/        (for local dev)
   https://your-app.onrender.com/ (for deployment)
   ```
5. Download `credentials.json` (used locally, or paste into Render env var).

---

## ▶️ Run locally

```bash
streamlit run app.py
```

Go to [http://localhost:8501](http://localhost:8501).

---

## 🚀 Deploy on Render

1. Push code to GitHub.
2. Create a new **Web Service** on Render.
3. Configure:

   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Add environment variables in Render dashboard:

   * `OPENAI_API_KEY`
   * `GOOGLE_OAUTH_JSON` (paste contents of credentials.json).
5. Set OAuth redirect URI in Google Cloud to your deployed URL.

---

## 📂 Project Structure

```
.
├── app.py             # Streamlit UI
├── auth.py            # Google OAuth2 handling
├── drive.py           # Google Docs fetching
├── pipeline.py        # RAG pipeline (OpenAI + Chroma)
├── utils.py           # Text chunking helper
├── requirements.txt   # Dependencies
├── .env               # Local API keys (ignored in git)
└── README.md
```

---

## 🧑‍💻 For Interviews / Explanation

* **Auth Flow**:

  * Streamlit shows login link → redirects to Google OAuth → gets `code` → exchanges for `token`.
* **Doc Retrieval**:

  * Uses Google Docs API to extract raw text, including tables and nested content.
* **Chunking + Embeddings**:

  * Splits text into \~1000 char chunks → embeds with OpenAI → stores in Chroma vector DB.
* **Querying**:

  * Retrieves top-k relevant chunks → builds context → sends to ChatOpenAI.

---

## ⚠️ Notes

* Never commit `credentials.json`.
* Use `GOOGLE_OAUTH_JSON` in production.
* OpenAI API costs apply when embedding or answering queries.

---

👉 Through this project, I not only built a working RAG chatbot but also gained deep hands-on experience with integrating OAuth2 authentication, working with Google APIs, and deploying full-stack applications. I polished my understanding of retrieval-augmented generation (RAG) pipelines, vector databases, and embeddings. More importantly, I learned how to take an idea from scratch, connect multiple moving parts, and make it production-ready. This journey has been a huge step forward in my growth as a developer — and I hope it inspires others to dive into building impactful AI-powered applications too.

