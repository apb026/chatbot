import streamlit as st
import requests
import json

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Google's Gemini model to generate responses. "
    "To use this app, you need to provide a Gemini API key, which you can get from Google Cloud."
)

# Ask user for their Gemini API key via st.text_input.
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # Set up the Gemini API endpoint with the provided API key.
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
    
    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via st.chat_message.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message.
    prompt = st.chat_input("What is up?")
    if prompt:
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare the request payload as required by Gemini.
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        # Send the request to the Gemini API.
        response = requests.post(
            GEMINI_API_URL,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )

        # Check the response and handle accordingly.
        if response.status_code == 200:
            # Extract the generated response from the Gemini API.
            response_data = response.json()

            # Extract the text from the response (Gemini response)
            if "candidates" in response_data:
                # Get the model's reply (first candidate)
                gemini_response = response_data["candidates"][0]["content"]["parts"][0]["text"]

                if gemini_response:
                    # Display and store the assistant's response in the chat
                    with st.chat_message("assistant"):
                        st.markdown(gemini_response)

                    st.session_state.messages.append({"role": "assistant", "content": gemini_response})
                else:
                    st.error("No response text found in Gemini API output.")
            else:
                st.error("Unexpected response structure from Gemini API.")
        else:
            st.error(f"Error with Gemini API: {response.status_code} - {response.text}")