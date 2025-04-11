import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os
import json
import re

# --- Configuration ---
genai.configure(api_key="YOUR_API_KEY") # Replace with your actual key generted from gemini
HISTORY_DIR = "chat_histories"

# --- Ensure History Directory Exists ---
os.makedirs(HISTORY_DIR, exist_ok=True)

# --- Model Initialization ---
model = genai.GenerativeModel('models/gemini-2.0-flash')

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "current_chat_file" not in st.session_state:
    st.session_state["current_chat_file"] = None # Track which file is loaded

# --- Helper Functions ---
def slugify(text):
    """
    Simplifies variable names by removing non-alphanumeric characters and spaces.
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text

def save_chat_history(history, directory):
    """Saves the chat history to a JSON file, using the first user message as the name."""
    if not history:
        return None # Don't save empty chats

    # Extract the first user message as the chat name
    chat_name = "Unnamed Chat"
    for msg in history:
        if msg["role"] == "user":
            chat_name = msg["content"][:50]  # Use first 50 chars
            break

    filename = f"chat_{slugify(chat_name)}.json"
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)
        return filename
    except Exception as e:
        st.error(f"Error saving chat history: {e}")
        return None

def load_chat_history(filename, directory):
    """Loads chat history from a JSON file."""
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            history = json.load(f)
        return history
    except FileNotFoundError:
        st.error(f"Error: Chat history file not found: {filename}")
        return []
    except json.JSONDecodeError:
        st.error(f"Error: Could not decode chat history file: {filename}")
        return []
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        return []

def delete_chat_history(filename, directory):
    """Deletes a chat history file."""
    filepath = os.path.join(directory, filename)
    try:
        os.remove(filepath)
        return True
    except FileNotFoundError:
        st.error(f"Error: Chat history file not found: {filename}")
        return False
    except Exception as e:
        st.error(f"Error deleting chat history: {e}")
        return False

# --- UI Setup ---
st.set_page_config(page_title="AI Chat Assistant", layout="wide")
st.title("🤖 AI Chat Assistant")

# --- Sidebar ---
with st.sidebar:
    st.header("Chat Controls")

    # Button to start a new chat (saves current one first)
    if st.button("Start New Chat"):
        saved_file = save_chat_history(st.session_state["chat_history"], HISTORY_DIR)
        if saved_file:
            st.sidebar.success(f"Saved current chat as {saved_file}")
        st.session_state["chat_history"] = []
        st.session_state["current_chat_file"] = None
        st.rerun()

    st.divider()
    st.header("Previous Chats")

    # List previous chat files
    try:
        history_files = sorted(
            [f for f in os.listdir(HISTORY_DIR) if f.startswith("chat_") and f.endswith(".json")],
            reverse=True # Show newest first
        )

        # Display buttons to load previous chats
        for filename in history_files:
            # Extract readable timestamp from filename if possible
            try:
                chat_name = filename.replace("chat_", "").replace(".json", "").replace("-", " ")
                chat_name = ' '.join(word.capitalize() for word in chat_name.split()) # Title Case
            except:
                chat_name = filename # Fallback

            col1, col2 = st.columns([0.8, 0.2]) # Adjust ratio as needed
            with col1:
                if st.button(chat_name, key=f"load_{filename}", use_container_width=True):
                    loaded_history = load_chat_history(filename, HISTORY_DIR)
                    st.session_state["chat_history"] = loaded_history
                    st.session_state["current_chat_file"] = filename
                    st.rerun() # Rerun to display the loaded chat
            with col2:
                if st.button("❌", key=f"delete_{filename}", help="Delete this chat", use_container_width=True):
                    if delete_chat_history(filename, HISTORY_DIR):
                        st.sidebar.success(f"Deleted chat: {chat_name}")
                    else:
                        st.sidebar.error(f"Failed to delete chat: {chat_name}")
                    st.rerun() # Refresh the sidebar

    except Exception as e:
        st.sidebar.error(f"Error listing history files: {e}")


# --- Display Chat History ---
if st.session_state["current_chat_file"]:
    st.caption(f"Currently viewing: {st.session_state['current_chat_file']}")

for message in st.session_state["chat_history"]:
    role = message.get("role", "unknown") # Use .get for safety with older files
    content = message.get("content", "")
    timestamp = message.get("timestamp", "N/A")
    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
    with st.chat_message(role):
        st.markdown(content)
        st.caption(timestamp)

# --- Chat Input and Processing ---
if prompt := st.chat_input("What would you like to ask?"):
    # 1. Add user message to history and display it
    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["chat_history"].append({"role": "user", "content": prompt, "timestamp": timestamp_now})
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(datetime.now().strftime("%H:%M:%S"))

    # 2. Prepare history for the model
    history_for_model_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state["chat_history"]])

    # 3. Get AI response
    with st.spinner("Thinking..."):
        try:
            response = model.generate_content(history_for_model_prompt)
            # Accessing the text part correctly
            ai_content = response.candidates[0].content.parts[0].text
        except Exception as e:
            st.error(f"Error generating response: {e}")
            ai_content = f"Sorry, I encountered an error: {e}" # Provide error in chat

    # 4. Add AI response to history and display it
    timestamp_ai = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["chat_history"].append({"role": "assistant", "content": ai_content, "timestamp": timestamp_ai})
    with st.chat_message("assistant"):
        st.markdown(ai_content)
        st.caption(datetime.now().strftime("%H:%M:%S"))

    # No need to explicitly clear chat_input, Streamlit handles it.
    # Rerun might be needed if state updates don't reflect immediately, but often not necessary here.
    # st.rerun() # Usually not needed after adding messages
