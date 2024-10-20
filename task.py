import streamlit as st
import openai
import requests
import json

# Define Azure OpenAI connection details
azure_openai_key = "22ec84421ec24230a3638d1b51e3a7dc"  # Replace with your actual key
azure_openai_endpoint = 'https://internshala.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview'  # Replace with your actual endpoint URL

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "You are a helpful assistant."}]

def get_response_from_openai(user_input):
    headers = {
        "Content-Type": "application/json",
        "api-key": azure_openai_key,
    }
    
    data = {
        "messages": st.session_state["messages"],  # Use the chat history
        "max_tokens": 4096 ,  # You can adjust the token limit
    }
    
    # Send the request to Azure OpenAI
    response = requests.post(azure_openai_endpoint, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

def main():
    st.title("Azure OpenAI GPT-4 Chat")
    
    # Input from the user
    user_input = st.text_input("You: ", "", key="user_input")
    
    # Button to send the message and get a response
    if st.button("Send"):
        if user_input:
            # Append user message to the chat history
            st.session_state["messages"].append({"role": "user", "content": user_input})
            
            # Get the response from OpenAI
            ai_response = get_response_from_openai(user_input)
            
            if ai_response:
                # Append AI response to the chat history
                st.session_state["messages"].append({"role": "assistant", "content": ai_response})
    
    # Display the chat history
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            st.write(f"You: {message['content']}")
        elif message["role"] == "assistant":
            st.write(f"Assistant: {message['content']}")

if __name__ == "__main__":
    main()
