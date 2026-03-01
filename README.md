# 🌌 NexusVoice AI: The Autonomous Brand-Engine

**NexusVoice** is a next-generation "Content Multiplier" built for the agent-first era. It leverages **Gemini 3.1 Pro** and an orchestrated multi-agent architecture to transform long-form technical transcripts, blogs, or documentation into a synchronized multi-platform content campaign in seconds.



---

## 🚀 Key Features

* **Multimodal Ingestion:** Drop in a YouTube transcript, a technical whitepaper, or a raw `.mp4` file.
* **Orchestrated Agent Squad:** Parallel execution of platform-specific agents:
    * **The Architect (LinkedIn):** High-authority, technical thought leadership.
    * **The Threader (X/Twitter):** High-velocity, viral hooks and threads.
    * **The Scripter (Shorts/TikTok):** Visual-first storytelling and CTAs.
    * **The Curator (Newsletter):** Structured summaries for Substack/Email.
* **Brand Voice DNA:** Customizable "System Instructions" to ensure the AI sounds like a Cloud & AI Developer, not a generic chatbot.
* **Self-Healing UI:** Built with **Antigravity** to allow real-time feedback loops between agents.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Model** | Gemini 3.1 Pro (via Vertex AI) |
| **Orchestration** | Antigravity Agent Manager |
| **Frontend** | Next.js 15, Tailwind CSS, Zustand |
| **Backend** | FastAPI, Pydantic |
| **Infrastructure** | Google Cloud Run, GCS, Artifact Registry |

---

## 🏗️ Architecture

NexusVoice uses a **Supervisor-Worker** pattern. The Supervisor analyzes the input for "Atomic Insights" and broadcasts them to the Specialist Agents.



```mermaid
graph TD
    A[User Upload] --> B(Supervisor Agent)
    B --> C{The Analyst}
    C --> D[LinkedIn Specialist]
    C --> E[X Threader]
    C --> F[Video Scripter]
    C --> G[Newsletter Editor]
    D & E & F & G --> H[Review Dashboard]
