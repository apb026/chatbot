import streamlit as st
import requests
import json
import re

# Streamlit Page Configuration
st.set_page_config(page_title="Healthcare Assistant", page_icon="🏥")

# Title and Description
st.title("🏥 Healthcare Assistant Chatbot")
st.write(
    "This chatbot provides healthcare-related information and can generate medical images using Google's Gemini API."
)

# Gemini API Key Input
gemini_api_key = st.text_input("Enter your Gemini API Key", type="password")

if not gemini_api_key:
    st.warning("Please enter your Gemini API Key to continue.")
else:
    # Gemini API Endpoint
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"

    # Session State for Chat History and Symptoms
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_symptoms" not in st.session_state:
        st.session_state.user_symptoms = {}

    # Display the previous chat messages via `st.chat_message`
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Function for short responses to greetings
    def get_short_response(user_input):
        basic_responses = {
            "hi": "Hello! How can I assist you today?",
            "hello": "Hi there! How can I help you with your healthcare query?",
            "how are you": "I'm here to assist you! How can I help today?",
        }
        return basic_responses.get(user_input.lower(), None)

    # Function to handle specific health-related queries (e.g., "I am not feeling good")
    def handle_general_health_query(user_input):
        if "not feeling good" in user_input.lower():
            return "I'm sorry to hear you're not feeling well. Can you describe your symptoms in more detail?"
        return None

    # Function to handle specific health-related queries like insomnia, cough, headache, upset stomach
    def handle_specific_health_query(user_input):
        if "insomniac" in user_input.lower() or "insomnia" in user_input.lower():
            return ("It seems like you're dealing with insomnia. Could you tell me more about your sleep patterns?\n"
                    "- Do you have trouble falling asleep, staying asleep, or waking up too early?\n"
                    "- How many hours of sleep are you getting on average per night?\n"
                    "- Are you experiencing any stress, anxiety, or other factors that might be affecting your sleep?\n"
                    "This information will help me understand your condition better.")
        elif "cough" in user_input.lower():
            return ("I understand you're experiencing a cough. Could you please provide more details?\n"
                    "- How long have you had the cough?\n"
                    "- Is it dry or with mucus?\n"
                    "- Do you have other symptoms like fever or shortness of breath?\n"
                    "This will help narrow down potential causes.")
        elif "headache" in user_input.lower():
            return ("Can you tell me more about your headache?\n"
                    "- How long have you had the headache?\n"
                    "- Is it throbbing, sharp, or dull?\n"
                    "- Any other symptoms like nausea, vomiting, or dizziness?\n"
                    "Please share as much detail as possible.")
        elif "upset stomach" in user_input.lower():
            return ("Sorry to hear you're feeling unwell. Could you clarify:\n"
                    "- Are you experiencing nausea, vomiting, diarrhea, or pain?\n"
                    "- Where is the pain located? Is it sharp or cramping?\n"
                    "This information will help me understand better.")
        return None

    # Function to validate and clean user input (to prevent malicious or unnecessary input)
    def validate_user_input(user_input):
        # Basic validation: Ensure input is not empty
        if not user_input or len(user_input.strip()) == 0:
            return "Please enter a valid query."
        
        # Check for suspicious content (like special characters)
        if re.search(r'[\<>;|&]', user_input):  # Detect dangerous characters (can expand this list)
            return "Your input contains invalid characters."
        
        return None  # Input is valid

    # Function to parse and store detailed symptoms
    def process_symptoms(user_input):
        if "headache" in user_input.lower():
            details = {}
            if "past" in user_input and "days" in user_input:
                days_match = re.search(r"(\d+)\s*days", user_input)
                if days_match:
                    details['duration'] = days_match.group(1)
            if "dull" in user_input:
                details['type'] = "dull"
            if "vomiting" in user_input:
                details['symptoms'] = "vomiting"
            return details
        elif "upset stomach" in user_input.lower():
            details = {}
            if "pain" in user_input:
                details['pain'] = "pain"
            if "sharp" in user_input:
                details['pain_type'] = "sharp"
            if "cramping" in user_input:
                details['pain_type'] = "cramping"
            return details
        return {}

    # Create a chat input field to allow the user to enter a message
    user_input = st.chat_input("Ask a healthcare question...")

    if user_input:
        # Validate user input
        validation_error = validate_user_input(user_input)
        if validation_error:
            with st.chat_message("assistant"):
                st.markdown(validation_error)
            st.session_state.messages.append({"role": "assistant", "content": validation_error})
        else:
            # Store and display the current user's input message
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Handle simple greetings
            short_response = get_short_response(user_input)
            if short_response:
                with st.chat_message("assistant"):
                    st.markdown(short_response)
                st.session_state.messages.append({"role": "assistant", "content": short_response})
            else:
                # Check if user has provided symptoms, and process it
                symptoms_details = process_symptoms(user_input)
                if symptoms_details:
                    st.session_state.user_symptoms.update(symptoms_details)
                    response = "Thank you for sharing. Based on what you’ve mentioned, here’s what I understand:\n"
                    if 'duration' in symptoms_details:
                        response += f"- Headache duration: {symptoms_details['duration']} days\n"
                    if 'type' in symptoms_details:
                        response += f"- Headache type: {symptoms_details['type']}\n"
                    if 'symptoms' in symptoms_details:
                        response += f"- Other symptoms: {symptoms_details['symptoms']}\n"
                    if 'pain' in symptoms_details:
                        response += f"- Pain type: {symptoms_details.get('pain_type', 'unspecified')}\n"
                    response += "I’ll ask a few more questions to understand better:\n"
                    response += "- Have you experienced any sensitivity to light or sound?\n"
                    response += "- Are you feeling dehydrated or have you had a fever?\n"
                    response += "- Is there any pain in your neck or shoulders?"

                    with st.chat_message("assistant"):
                        st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    # Handle specific health-related queries
                    specific_health_response = handle_specific_health_query(user_input)
                    if specific_health_response:
                        with st.chat_message("assistant"):
                            st.markdown(specific_health_response)
                        st.session_state.messages.append({"role": "assistant", "content": specific_health_response})
                    else:
                        # Default response if no specific condition found
                        response_text = "Can you tell me about your symptoms? I'll ask more specific questions to help you better."

                        with st.chat_message("assistant"):
                            st.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
