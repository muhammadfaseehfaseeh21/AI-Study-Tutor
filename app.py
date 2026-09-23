import os
import json
import streamlit as st
from groq import Groq
from tools import TOOLS_SCHEMA, AVAILABLE_FUNCTIONS

# 1. Page Configuration
st.set_page_config(page_title="AI Study Tutor", page_icon="🎓", layout="centered")
st.title("🎓 AI Personal Study Tutor")
st.caption("Ask questions, generate practice quizzes, or request revision notes!")

# Initialize Groq Client
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is missing! Set it in your environment variables or Render dashboard.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 2. Memory Setup (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "You are an encouraging, expert AI Study Tutor. "
                "Your goal is to explain concepts simply, encourage active learning, "
                "and use tools to generate quizzes, summaries, or solve math problems when requested."
            )
        }
    ]

# Display Chat History
for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"] and msg.get("content"):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Sidebar Control to clear session memory
if st.sidebar.button("Clear Chat Memory"):
    st.session_state.messages = [st.session_state.messages[0]]
    st.rerun()

# 3. User Input Handling
user_query = st.chat_input("Ask a study question (e.g., 'Quiz me on Cell Biology' or 'Summarize Newton's Laws')")

if user_query:
    # Render user prompt in UI
    with st.chat_message("user"):
        st.markdown(user_query)

    # Save to Chat Memory
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Call Groq API
    with st.chat_message("assistant"):
        with st.spinner("Tutor is thinking..."):
            # Initial LLM call
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )

            msg = response.choices[0].message

            # Check if Tool Execution is requested
            if msg.tool_calls:
                st.session_state.messages.append(msg)

                for tool_call in msg.tool_calls:
                    fname = tool_call.function.name
                    fargs = json.loads(tool_call.function.arguments)

                    if fname in AVAILABLE_FUNCTIONS:
                        result = AVAILABLE_FUNCTIONS[fname](**fargs)

                        # Append Tool Output to Memory
                        st.session_state.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": fname,
                            "content": result
                        })

                # Call Groq again to synthesize the final tutor answer
                final_res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages
                )
                output_text = final_res.choices[0].message.content
            else:
                output_text = msg.content

            st.markdown(output_text)
            st.session_state.messages.append({"role": "assistant", "content": output_text})
