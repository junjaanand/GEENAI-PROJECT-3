import os
import streamlit as st
from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Email Drafter", page_icon="✉️", layout="centered")

# CrewAI Logic 
def build_email_crew(context: str, tone: str, recipient: str) -> str:
    llm = LLM(
        model="gemini/gemini-3.6-flash",
        temperature=0.3,
        api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
    )

    analyst = Agent(
        role="Email Context Analyst",
        goal="Understand the email context, extract key points, and define the structure",
        backstory="You are an expert business communication analyst who distills complex situations into clear email requirements.",
        llm=llm,
        verbose=False,
    )

    writer = Agent(
        role="Professional Email Writer",
        goal="Draft clear, concise, and effective professional emails",
        backstory="You are a professional copywriter specializing in business emails that get responses.",
        llm=llm,
        verbose=False,
    )

    analyze_task = Task(
        description=f"""Analyze this email requirement:
Context: {context}
Recipient: {recipient}
Desired tone: {tone}

Extract: purpose, key points to cover, call to action, subject line suggestion.""",
        agent=analyst,
        expected_output="Structured email brief: purpose, key points, CTA, and suggested subject line",
    )

    write_task = Task(
        description=f"""Using the analysis, draft a complete professional email.
Tone: {tone}. Recipient: {recipient}.
Include: Subject line, greeting, body paragraphs, closing, signature placeholder.
Keep it concise — under 200 words for the body.""",
        agent=writer,
        expected_output="Complete formatted email ready to send",
        context=[analyze_task],
    )

    crew = Crew(
        agents=[analyst, writer],
        tasks=[analyze_task, write_task],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    return str(result)


# Streamlit UI 
st.title("📧 AI Email Drafting Agent")
st.caption("Powered by CrewAI and Google Gemini")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Reads from .env by default if left blank",
    )
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input

st.subheader("Email Parameters")

recipient = st.text_input(
    "Recipient",
    value="Potential Client",
    placeholder="e.g., Hiring Manager, Team Lead, Client",
)

tone = st.selectbox(
    "Tone",
    options=[
        "Professional and Friendly",
        "Formal and Concise",
        "Direct and Urgent",
        "Casual and Warm",
        "Persuasive and Confident",
    ],
)

context = st.text_area(
    "Context / Purpose",
    value="Follow up on our product demo from last Tuesday. They seemed interested but haven't responded.",
    height=120,
    placeholder="Describe what the email should achieve...",
)

if st.button("Generate Email", type="primary", use_container_width=True):
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        st.error("Please provide a Gemini API Key in the sidebar or your .env file.")
    elif not context.strip():
        st.warning("Please provide context for the email.")
    else:
        with st.spinner("Analyzing context and drafting email..."):
            try:
                email_output = build_email_crew(context, tone, recipient)
                st.success("Email drafted successfully!")
                
                st.markdown("### 📧 Result")
                st.text_area("Drafted Email", value=email_output, height=260)
                
                st.download_button(
                    label="📥 Download Email (.txt)",
                    data=email_output,
                    file_name="drafted_email.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"Error generating email: {str(e)}")