# --- 🛡️ CRITICAL FIX FOR PYTHON 3.13 & TORCH ---
import os
import torch
try:
    torch.classes.__path__ = [] 
except AttributeError:
    pass
# -----------------------------------------------

import streamlit as st
import time
from advanced_agent import app

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Australian Innovation Auditor",
    page_icon="🇦🇺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS (Dark Navy & Gold Theme) ---
st.markdown("""
    <style>
    /* 1. BACKGROUND: Deep Aussie Navy Gradient */
    .stApp {
        background-color: #001219;
        background-image: radial-gradient(circle at 50% 30%, #002B49 0%, #000a12 100%);
        background-attachment: fixed;
    }

    /* 2. TYPOGRAPHY: FORCED CENTERING & WHITE TEXT */
    h1 {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
        text-align: center !important;
        letter-spacing: 1px;
        margin-top: 0px;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
    }
    
    .subtitle {
        color: #B0BEC5;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 1.2rem;
        text-align: center !important;
        margin-top: 5px;
        margin-bottom: 40px;
        font-weight: 300;
    }

    /* 3. FORCE CHAT TEXT WHITE */
    div[data-testid="stChatMessageContent"] p, 
    div[data-testid="stChatMessageContent"] li, 
    div[data-testid="stChatMessageContent"] span,
    div[data-testid="stChatMessageContent"] div {
        color: #FFFFFF !important;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    /* 4. INTRO BOX */
    .intro-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 30px;
        margin: 0 auto;
        max-width: 800px;
        text-align: center;
        color: #E0E0E0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .highlight {
        color: #FFD700; /* Aussie Gold */
        font-weight: 600;
    }

    /* 5. INPUT BOX */
    .stChatInput {
        background-color: #FFFFFF !important;
        border: 2px solid #FFD700 !important;
        border-radius: 12px !important;
        padding: 5px !important;
    }
    
    textarea[data-testid="stChatInputTextArea"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        caret-color: #000000 !important;
    }
    
    /* 6. CHAT BUBBLES */
    .stChatMessage {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
    }
    
    div[data-testid="chatAvatarIcon-user"] {
        background-color: #00843D !important; /* Aussie Green */
    }
    div[data-testid="chatAvatarIcon-assistant"] {
        background-color: #FFD700 !important; /* Aussie Gold */
        color: #000000 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. HEADER (ALWAYS VISIBLE) ---
# This guarantees the Flag and Title stay at the top, even when chatting.
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; font-size: 90px; margin-bottom: 10px;'>🇦🇺</div>", 
    unsafe_allow_html=True
)
st.markdown("<h1 style='text-align: center; color: white;'>Australian Innovation & Grants Auditor</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle' style='text-align: center;'>AI-Powered Compliance for R&D Tax, EMDG & ESIC Schemes</div>", unsafe_allow_html=True)


# --- 5. INTRO BOX (CONDITIONAL) ---
# This ONLY shows if the chat is empty. Once you type, this disappears to make room.
if not st.session_state.messages:
    st.markdown("""
    <div class='intro-box'>
        <p style='font-size: 1.1rem; line-height: 1.6;'>
            <b>Welcome.</b> This autonomous agent audits your business activities against the latest Australian legislation.
            It utilizes <span class='highlight'>Hybrid Search</span> (Vector + Keyword) to cross-reference your claims against official government guides, 
            providing instant preliminary compliance assessments.
        </p>
        <br>
        <p style='font-size: 1rem; color: #B0BEC5; margin-bottom: 5px;'><b>📚 Integrated Regulatory Frameworks:</b></p>
        <ul style='list-style-type: none; padding: 0; color: #E0E0E0;'>
            <li>• <span class='highlight'>R&D Tax Incentive</span> (Guide to Interpretation v2.4 & Sector Guides)</li>
            <li>• <span class='highlight'>EMDG Round 4</span> (Market Guidelines & Tier Eligibility)</li>
            <li>• <span class='highlight'>ESIC Startups</span> (100-Point Innovation Test & Early Stage Rules)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- 6. CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. AGENT LOGIC ---
if prompt := st.chat_input("Enter project details, expenditure queries, or eligibility questions..."):
    
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent Response
    with st.chat_message("assistant"):
        status_box = st.status("🧠 **Auditing Compliance...**", expanded=True)
        
        inputs = {"question": prompt}
        full_response = ""
        
        try:
            # Stream Steps
            for output in app.stream(inputs):
                for key, value in output.items():
                    
                    if key == "retrieve":
                        docs = value['documents']
                        source_list = list(set([d.metadata.get('source', 'Unknown').split('/')[-1] for d in docs]))
                        
                        with st.expander(f"🔍 **Legislation Search:** Found {len(docs)} References", expanded=False):
                            st.write("Cross-referenced documents:")
                            for source in source_list:
                                st.caption(f"📄 {source}")

                    elif key == "grade_documents":
                        if value.get("web_search") == "Yes":
                            st.warning("⚠️ Definition check failed. Refining search scope...")
                        else:
                            st.success("✅ Valid Regulatory Match Found.")
            
            # Final Answer
            final_state = app.invoke(inputs)
            response = final_state["generation"]
            
            status_box.update(label="✅ **Assessment Complete**", state="complete", expanded=False)
            
            # Typewriter Stream
            message_placeholder = st.empty()
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"System Error: {str(e)}")