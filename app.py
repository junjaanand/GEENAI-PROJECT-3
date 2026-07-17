from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
import time

# creating customr suppor chatbot
st.subheader("Customer Support chatbot....")

# if web_loaded nahi hai sesion state mai to web abhi load nahi hua hai
if "web_loaded" not in st.session_state:
    st.session_state.web_loaded = False

# if vector store nahi hai session state mai to usse nonw rakho
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "messages" not in st.session_state:
    st.session_state.messages =  []
    
def processing_url(urls = []):
    #  this part executes when the web page is loaded so we want to session state to true
    all_urls = []

    # document loaders
    for url in urls:
        loader = WebBaseLoader(web_path=url)
        docs = loader.load()
        all_urls.extend(docs)

    # split the text 
    spliter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
    splitdocs = spliter.split_documents(documents=all_urls)


    # embeddings and vector store
    embed = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

    # storing
    vector_store = InMemoryVectorStore.from_documents(
        documents=splitdocs,
        embedding=embed
    )
    
    st.session_state.vector_store = vector_store
    st.session_state.web_loaded = True
    


if not st.session_state.web_loaded:
    urls = st.text_area(label="Enter URLs......")
    if urls : 
        processing_url(urls.split())
        st.success("url loaded successfully...")
        time.sleep(2)
        st.rerun() # load page with same session state
        
if st.session_state.web_loaded  and st.session_state.vector_store:
    for message in st.session_state.messages:
        role = message["role"] 
        content = message["content"]
        st.chat_message(role).markdown(content)
        
    query = st.chat_input("Ask Anything.....")

    if query:
        st.session_state.messages.append({"role":"user","content":query})
        st.chat_message("user").markdown(query)

        #  now here total 3 similar records are generated so now we separate that into context
        # so that based on context out llm can give the answer of user question.
        #  3 records are not answer it is just similar data tot the question 
        # similarity search gives the most similar records from vector storage so here for my question i got 3 similar datas
        record = st.session_state.vector_store.similarity_search(query=query, k=6)
        # print(len(record),record[-1].page_content)


        #  here je similar data aahe te context madhe append karatoy to make suitable for  our llm
        context = ""
        for chunk in record:
            context += chunk.page_content + "\n\n"
            
            
        # defining llm toget answer of user question based on context generated
        # llm =ChatGoogleGenerativeAI(model="gemini-3.5-flash")
        llm = ChatGroq(model="llama-3.3-70b-versatile")
        #  here we provide context and question to our llm

        #  use output parser for structured output
        parser = StrOutputParser()
        # here jobhi llm ka output hain vo aane ke baad paser mai chala jayega
        chain = llm | parser
        
        
        prompt = f"""i will provide you context and question so b`ased on context give the answer of the question
        if answer is not in context than simply say i dont know with one smily at last
        question:{query}
        context: {context}
        """
        
        data = chain.invoke(prompt)
        st.chat_message("ai").markdown(data)
        st.session_state.messages.append({"role":"ai","content":data})