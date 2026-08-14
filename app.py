import streamlit as st
import time
from dotenv import load_dotenv

# Load environment variables (API Keys)
load_dotenv()

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Support Assistant",
    page_icon="🤖",
    layout="wide"  # Uses more screen space for input and output
)

# ----------------- SESSION STATE -----------------
# Ensure state is maintained across reruns
if "web_loaded" not in st.session_state:
    st.session_state.web_loaded = False

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- CORE LOGIC (UNCHANGED) -----------------
def processing_url(urls = []):
    """
    Core backend logic:
    1. Validates URLs.
    2. Loads web content.
    3. Splits text.
    4. Embeds and stores in VectorStore.
    """
    all_urls = []

    # Validating URLs before loading to prevent application crash
    valid_urls = [u for u in urls if u.startswith(("http://", "https://"))]

    if not valid_urls:
        st.error("No valid URLs found. Make sure every link starts with http:// or https://")
        return False

    # Status indicator within the sidebar
    status_text = st.sidebar.empty()
    progress_bar = st.sidebar.progress(0)

    # DOCUMENT LOADERS
    try:
        status_text.text("Loading web documents...")
        for i, url in enumerate(valid_urls):
            loader = WebBaseLoader(web_path=url)
            docs = loader.load()
            all_urls.extend(docs)
            progress_bar.progress(int((i + 1) / len(valid_urls) * 50))
    except Exception as e:
        status_text.empty()
        progress_bar.empty()
        st.error(f"Error loading URLs: {e}")
        return False

    # SPLIT THE TEXT
    status_text.text("Splitting text into chunks...")
    spliter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
    splitdocs = spliter.split_documents(documents=all_urls)
    progress_bar.progress(70)

    # EMBEDDINGS AND VECTOR STORE
    try:
        status_text.text("Creating vector embeddings (Gemini)...")
        embed = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

        # STORING
        vector_store = InMemoryVectorStore.from_documents(
            documents=splitdocs,
            embedding=embed
        )
        progress_bar.progress(100)
        
        # UPDATE SESSION STATE
        st.session_state.vector_store = vector_store
        st.session_state.web_loaded = True
        
        status_text.empty()
        progress_bar.empty()
        return True

    except Exception as e:
        status_text.empty()
        progress_bar.empty()
        st.error(f"Error creating vector store: {e}")
        return False

# ----------------- UI MAIN LAYOUT -----------------
st.title("🤖 Customer Support AI Assistant")
st.markdown("---")

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.header("Setup Knowledge Base")
    st.markdown("Provide URLs to the documentation you want the AI to use as context.")

    # URL Input Area
    urls_input = st.text_area(
        label="Enter Website URLs (separated by lines or spaces):",
        placeholder="https://docs.example.com\nhttps://example.com/faq",
        height=200,
        help="The AI will split and index the content of these pages."
    )

    # Process Button
    process_btn = st.button("🚀 Load and Index Knowledge Base", use_container_width=True)

    st.markdown("---")
    
    # State Indicators
    st.subheader("Current Status")
    if st.session_state.web_loaded:
        st.success("✅ Knowledge Base Active")
        
        # Management buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("Reset All", use_container_width=True):
                st.session_state.web_loaded = False
                st.session_state.vector_store = None
                st.session_state.messages = []
                st.rerun()
    else:
        st.info("💡 Enter URLs above and click 'Load' to begin.")

# Handle the process button action
if process_btn:
    if urls_input.strip():
        # Core logic call (now with visual feedback within sidebar)
        if processing_url(urls_input.split()):
            st.rerun() # Refresh with updated state
    else:
        st.sidebar.warning("Please enter at least one valid URL.")

# ----------------- MAIN CHAT INTERFACE -----------------
if not st.session_state.web_loaded:
    # Instructions if the knowledge base isn't loaded
    st.warning("👈 Please add knowledge base URLs in the sidebar to activate the chat.")
else:
    # 1. Display Chat History
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        # Standard Streamlit chat rendering
        with st.chat_message(role):
            st.markdown(content)

    # 2. Accept User Input
    query = st.chat_input("Ask a question about the documentation...")

    if query:
        # Save user input
        st.session_state.messages.append({"role":"user","content":query})
        with st.chat_message("user"):
            st.markdown(query)

        # 3. Vector Retrieval (logic unchanged)
        # We perform a similarity search to get relevant context
        with st.spinner("Searching knowledge base..."):
            record = st.session_state.vector_store.similarity_search(query=query, k=6)

            # Separate retrieved chunks into a context block
            context = ""
            for chunk in record:
                context += chunk.page_content + "\n\n"
        
        # 4. LLM Generation (logic unchanged)
        llm = ChatGroq(model="llama-3.3-70b-versatile")
        parser = StrOutputParser()
        
        # Provide context and question to the prompt
        prompt = f"""i will provide you context and question so b`ased on context give the answer of the question
if answer is not in context than simply say i dont know with one smily at last
question:{query}
context: {context}
"""

        # Chain the components (unchanged logic)
        chain = llm | parser

        # Generate answer and update chat history
        with st.chat_message("ai"):
            with st.spinner("Generating answer..."):
                try:
                    data = chain.invoke(prompt)
                    st.markdown(data)
                    st.session_state.messages.append({"role":"ai","content":data})
                except Exception as e:
                    st.error(f"Error during generation: {e}")