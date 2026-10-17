"""P4.py — Wire Up Gemini + LangChain

SUMMARY:
Connects Gemini to LangChain ConversationChain and ConversationBufferMemory, then 
checks whether a second turn can recall details from the first.

PREREQUISITES:
- Install: pip install langchain langchain-google-genai python-dotenv. 
Put GEMINI_API_KEY in .env. Classic ConversationChain and memory APIs may be 
deprecated in newer LangChain releases.
Put GEMINI_API_KEY in .env. 
"""


# Import the libraries and framework components required by this example.
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

# Modern LangChain imports replacing deprecated legacy components
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Load environment variables from the local .env file.
load_dotenv()

# Configure the LangChain integration for the Gemini model.
llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.7)

# Create a prompt with a placeholder for conversational history.
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])
