import streamlit as st
import google.generativeai as genai

# Show title and description.
st.title("🏭 Factory Auditor Chatbot")
st.write(
    "This chatbot is designed to assist auditors in factories with machine and equipment inspections. "
    "Ask questions about specific machines, procedures, or any relevant information to streamline your audit process. "
    "Please provide your Google AI Studio API key to begin. "
)

# Ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # Configure the Gemini API.
    genai.configure(api_key=gemini_api_key)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field.
    if prompt := st.chat_input("Ask about machine inspection, procedures, etc."):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the Gemini API (gemini-2.0-flash-lite).
        model = genai.GenerativeModel('models/gemini-2.0-flash-lite') #Modified Model
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": m["content"]}
            for m in st.session_state.messages[:-1]
        ])
        response = chat.send_message(prompt, stream=True)

        # Stream the response and store it.
        full_response = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})