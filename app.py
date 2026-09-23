import os
import json
import streamlit as st
from groq import Groq
from tools import TOOLS_SCHEMA, AVAILABLE_FUNCTIONS

# 1. Page Configuration
st.set_page_config(
    page_title="NEON-AI Study Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Neon Blue & Cyberpunk CSS Injection
st.markdown("""
<style>
    /* Dark Cyber Background */
    .stApp {
        background-color: #080c14;
        color: #e2e8f0;
    }
    
    /* Neon Blue Glowing Title */
    .neon-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00d2ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
        margin-bottom: 5px;
    }

    .neon-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }

    /* Glassmorphic Cards */
    .feature-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .feature-card:hover {
        border-color: rgba(0, 242, 254, 0.6);
        transform: translateY(-2px);
    }

    /* Chat Messages Custom Styling */
    .stChatMessage {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 12px !important;
        margin-bottom: 12px !important;
    }

    /* Input Field Styling */
    .stChatInput > div {
        border-color: rgba(0, 242, 254, 0.4) !important;
        background: rgba(15, 23, 42, 0.9) !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.15) !important;
        border-radius: 12px !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #0b1120 !important;
        border-right: 1px solid rgba(0, 242, 254, 0.15) !important;
    }

    /* Custom Neon Badge */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 20px;
        background: rgba(0, 242, 254, 0.15);
        color: #00f2fe;
        border: 1px solid rgba(0, 242, 254, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# 3. Header & Sidebar Setup
st.markdown('<div class="neon-title">⚡ NEON-AI Tutor</div>', unsafe_allow_html=True)
st.markdown('<div class="neon-subtitle">Autonomous AI Study Agent powered by Llama-3.3 with Real-time Memory & Tool Execution.</div>', unsafe_allow_html=True)

# Sidebar Options
with st.sidebar:
    st.markdown("### ⚙️ Agent Dashboard")
    st.markdown('<span class="badge">GROQ LLM ACTIVE</span>', unsafe_allow_html=True)
    st.write("")
    
    model_choice = st.selectbox(
        "Select Model:",
        ["llama-3.3-70b-versatile", "llama3-8b-8192"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🛠️ Active Tools")
    st.markdown("• **Quiz Generator**: Auto-generates MCQs")
    st.markdown("• **Notes Summarizer**: Key concepts & takeaways")
    st.markdown("• **Math Solver**: Solves mathematical equations")
    
    st.markdown("---")
    if st.button("🧹 Clear Conversation Memory", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# 4. Groq Client Initialization
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("⚠️ GROQ_API_KEY environment variable is not set. Please add it to your secrets or Render environment settings.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 5. Memory Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are an encouraging, highly knowledgeable AI Study Tutor with a high-tech persona. "
                "Explain concepts clearly, format responses neatly using markdown, and trigger tool calls "
                "when the user requests quizzes, summaries, or math solving."
            )
        }
    ]

# Render Quick Feature Prompts
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="feature-card">
        🎯 <b>Quiz Me</b><br/>
        <small style="color:#94a3b8;">"Quiz me on Machine Learning basics"</small>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="feature-card">
        📚 <b>Summarize Notes</b><br/>
        <small style="color:#94a3b8;">"Summarize Photosynthesis into key points"</small>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="feature-card">
        🧮 <b>Math Solver</b><br/>
        <small style="color:#94a3b8;">"Solve 125 * 45 / 3 + 12"</small>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# 6. Display Chat History
for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"] and msg.get("content"):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 7. User Input & Processing Loop
user_query = st.chat_input("Ask a study question, request a quiz, or ask to solve math...")

if user_query:
    # Render user input
    with st.chat_message("user"):
        st.markdown(user_query)

    # Save user message to memory
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Call Groq LLM
    with st.chat_message("assistant"):
        with st.spinner("⚡ AI Agent is processing..."):
            response = client.chat.completions.create(
                model=model_choice,
                messages=st.session_state.messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )

            msg = response.choices[0].message

            # Check for tool call
            if msg.tool_calls:
                st.session_state.messages.append(msg)

                for tool_call in msg.tool_calls:
                    fname = tool_call.function.name
                    fargs = json.loads(tool_call.function.arguments)

                    if fname in AVAILABLE_FUNCTIONS:
                        result = AVAILABLE_FUNCTIONS[fname](**fargs)

                        # Save tool output to memory
                        st.session_state.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": fname,
                            "content": result
                        })

                # Follow-up LLM call to synthesize response
                final_res = client.chat.completions.create(
                    model=model_choice,
                    messages=st.session_state.messages
                )
                output_text = final_res.choices[0].message.content
            else:
                output_text = msg.content

            st.markdown(output_text)
            st.session_state.messages.append({"role": "assistant", "content": output_text})
