import streamlit as st
import google.generativeai as genai
import numpy as np

# Sample food and drink data with vector representations
sample_data = [
    {"name": "Chocolate Cake", "description": "Rich and sweet chocolate cake.", "vector": np.array([0.8, 0.2, 0.1])},
    {"name": "Lemon Tart", "description": "Tangy and sour lemon tart.", "vector": np.array([0.2, 0.9, 0.3])},
    {"name": "Iced Latte", "description": "Sweet and creamy iced coffee.", "vector": np.array([0.7, 0.3, 0.4])},
    {"name": "Fruit Salad", "description": "A mix of fresh, sweet and slightly sour fruits.", "vector": np.array([0.5, 0.6, 0.7])},
    {"name": "Spicy Chicken Wrap", "description": "Spicy and savory chicken wrap.", "vector": np.array([0.1, 0.4, 0.9])},
    {"name": "Black Coffee", "description": "Strong and bitter black coffee.", "vector": np.array([0.05, 0.1, 0.2])},
]

def find_similar_items(user_vector, data, top_n=3):
    similarities = []
    for item in data:
        similarity = np.dot(user_vector, item["vector"]) / (np.linalg.norm(user_vector) * np.linalg.norm(item["vector"]))
        similarities.append((similarity, item))
    similarities.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in similarities[:top_n]]

def get_user_vector(user_input):
    user_vector = np.zeros(3)
    if "sweet" in user_input.lower():
        user_vector[0] += 1
    if "sour" in user_input.lower():
        user_vector[1] += 1
    if "spicy" in user_input.lower() or "savory" in user_input.lower():
        user_vector[2] += 1
    return user_vector

# Streamlit app
st.title("☕ Coffee Shop Staff Chatbot")
st.write("Ask about our food and drink options!")

gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    genai.configure(api_key=gemini_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add system message to session state.
        st.session_state.messages.append({"role": "system", "content": "You are a helpful staff member at a coffee shop. You provide information about the food and drinks we offer, and help customers make selections."})

    for message in st.session_state.messages:
        if message["role"] != "system": #dont show system message.
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("What sweet drinks do you have?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        user_vector = get_user_vector(prompt)
        similar_items = find_similar_items(user_vector, sample_data)

        context = "\n".join([f"{item['name']}: {item['description']}" for item in similar_items])

        gemini_prompt = f"{prompt}. \nBase on this info to response:\n{context}"

        model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
        chat = model.start_chat(history=[
            {"role": m["role"], "parts": m["content"]}
            for m in st.session_state.messages if m["role"] != "system" #dont send system message to model.
        ])
        response = chat.send_message(gemini_prompt, stream=True)

        full_response = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})