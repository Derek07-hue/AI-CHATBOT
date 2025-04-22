import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_cohere import ChatCohere
from langchain.schema import HumanMessage, AIMessage
import io
import docx
import PyPDF2




# Initialize Chat Model
llm = ChatCohere(
    cohere_api_key="3fqSbt1Wj1ZSmnPaOPdLXRzou6QngA7L0tuLB4Ce",
    model="command-a-03-2025",
    temperature=0.7
)

# Setup Memory
if "messages" not in st.session_state:
    st.session_state.messages = []



# Streamlit UI
st.set_page_config(page_title="Derek.ai", layout="centered")
st.title("🤖 Derek.ai")

st.markdown("""
    <style>
            
        h1 {
            font-family: 'Georgia', serif; /* Font for title */
            font-size: 3rem;  /* Customize the title font size */
            color: blue;  /* Title color */
            text-align: center;
        }
            
        body {
            font-family: 'Georgia', sans-serif;  /* Change to Arial font */
            background-color: #800080 ;  /* Background color */
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Georgia', sans-serif;  /* Apply font to all headers */
        }
    </style>
""", unsafe_allow_html=True)

# Add after st.title() and before the chat messages display

# File upload section
uploaded_file = st.file_uploader("Upload a document (txt, docx, pdf)", type=['txt', 'docx', 'pdf'])

def read_file_content(uploaded_file):
    if uploaded_file is not None:
        # Get the file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        try:
            if file_extension == 'txt':
                content = uploaded_file.getvalue().decode('utf-8')
            elif file_extension == 'docx':
                doc = docx.Document(uploaded_file)
                content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            elif file_extension == 'pdf':
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                content = ''
                for page in pdf_reader.pages:
                    content += page.extract_text()
            return content
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None

if uploaded_file:
    content = read_file_content(uploaded_file)
    if content:
        st.success("Document uploaded successfully!")
        if "document_content" not in st.session_state:
            st.session_state.document_content = content
        
        # Add document summary button
        if st.button("Summarize Document"):
            with st.spinner("Generating summary..."):
                summary_prompt = f"Please summarize this document:\n\n{content}"
                response = llm.invoke(summary_prompt)
                summary_content = response.content if hasattr(response, 'content') else str(response)
                st.markdown("### Document Summary")
                st.markdown(summary_content)

# ...existing code...


# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
# Modify the existing chat input section

if user_input := st.chat_input("Ask anything..."):
    # Display user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display thinking animation
    with st.chat_message("assistant"):
        with st.spinner("Always on your command... 🧠"):
            # Prepare context if document is uploaded
            if "document_content" in st.session_state:
                prompt = f"""Context: {st.session_state.document_content[:1000]}...

Question: {user_input}

Please answer the question based on the context if relevant, or provide a general response if the question is not related to the document."""
            else:
                prompt = user_input
                
            # Get AI response
            response = llm.invoke(prompt)
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Display assistant response
            st.markdown(response_content)
    
    # Save the message to history
    st.session_state.messages.append({"role": "assistant", "content": response_content})