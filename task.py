import streamlit as st
import requests
import json

# Azure OpenAI connection details
azure_openai_key = "22ec84421ec24230a3638d1b51e3a7dc"  # Replace with your actual key
azure_openai_endpoint = "https://internshala.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"  # Replace with your actual endpoint

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "You are a helpful assistant."}]

# Function to communicate with Azure OpenAI API
def get_response_from_openai(user_input):
    headers = {
        "Content-Type": "application/json",
        "api-key": azure_openai_key,
    }
    
    data = {
        "messages": st.session_state["messages"],  # Chat history
        "max_tokens": 1500,  # You can adjust the token limit as needed
    }
    
    try:
        response = requests.post(azure_openai_endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Function to handle user input and interaction
def handle_user_input(user_input):
    # Append user message to the chat history
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    # Get the response from OpenAI
    ai_response = get_response_from_openai(user_input)
    
    if ai_response:
        # Append AI response to the chat history
        st.session_state["messages"].append({"role": "assistant", "content": ai_response})

# Function to display chat history
def display_chat_history():
    st.write("### Chat History")
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.write(f"**Assistant:** {message['content']}")
    st.write("---")

# Main function for the app
def main():
    st.title("💬 Azure OpenAI GPT-4 Chat")
    st.subheader("Powered by Azure OpenAI Service")

    # Input from the user
    user_input = st.text_input("Type your message:", key="user_input")

    # Button to send the message
    if st.button("Send"):
        if user_input.strip():  # Only proceed if user input is not empty
            handle_user_input(user_input)
            st.text_input("Type your message:", value="", key="user_input", placeholder="Type here...")  # Clear the input box
        else:
            st.warning("Please enter a message.")

    # Display chat history
    display_chat_history()

if __name__ == "__main__":
    main()
