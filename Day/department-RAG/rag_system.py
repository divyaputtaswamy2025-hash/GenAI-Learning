from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

# 1. Paths
BASE_DIR = Path(__file__).parent
DOCUMENTS_DIR = BASE_DIR / "documents"
DB_DIR = BASE_DIR / "chroma_db"

# 2. Ollama models
LLM_MODEL = "llama3.2"
EMBED_MODEL = "nomic-embed-text"


def build_rag():
    # Load department PDF documents
    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {DOCUMENTS_DIR}. "
            "Add your department PDF and try again."
        )

    documents = []
    for pdf_file in pdf_files:
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()

        # Keep the source filename in metadata
        for doc in docs:
            doc.metadata["source"] = pdf_file.name

        documents.extend(docs)

    print(f"Loaded {len(documents)} pages.")

    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    # Create local embeddings
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    # Store vectors persistently in ChromaDB
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_DIR),
        collection_name="department_documents"
    )

    print("Documents indexed successfully!")
    return vectorstore


def ask_question(vectorstore, question):
    # Retrieve relevant document chunks
    results = vectorstore.similarity_search(question, k=4)

    if not results:
        print("No relevant information was found.")
        return

    context = "\n\n".join(
        f"Source: {doc.metadata.get('source', 'Unknown')}\n"
        f"Content: {doc.page_content}"
        for doc in results
    )

    prompt = ChatPromptTemplate.from_template("""
You are a department information assistant.

Answer the question using ONLY the supplied context.
If the answer is not in the context, say:
"I couldn't find this information in the department documents."

Do not invent student details or facts.

Context:
{context}

Question:
{question}
""")

    llm = ChatOllama(model=LLM_MODEL, temperature=0)

    chain = prompt | llm
    response = chain.invoke({
        "context": context,
        "question": question
    })

    print("\nAnswer:")
    print(response.content)

    print("\nSources:")
    for doc in results:
        print(
            f"- {doc.metadata.get('source', 'Unknown')}, "
            f"page {doc.metadata.get('page', 'Unknown')}"
        )


if __name__ == "__main__":
    try:
        vectorstore = build_rag()

        print("\nDepartment RAG system is ready!")
        print("Type 'exit' to stop.\n")

        while True:
            question = input("Ask a question: ").strip()

            if question.lower() == "exit":
                break

            if question:
                ask_question(vectorstore, question)

    except Exception as error:
        print(f"\nError: {error}")