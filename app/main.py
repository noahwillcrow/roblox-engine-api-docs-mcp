import asyncio
import logging
from fastapi import FastAPI, HTTPException, Request
from app.models import RetrievalRequest, RetrievalResponse, RetrievedDocument
from app.retriever import get_retriever
from app.logging_config import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Roblox API RAG Service",
    description="A retrieval-focused API for the Roblox API knowledge base.",
    version="0.1.0",
)

retriever = get_retriever()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Roblox API RAG Service.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Roblox API RAG Service.")

@app.get("/")
async def read_root():
    """
    Root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the Roblox API RAG Service!"}

@app.post("/retrieve", response_model=RetrievalResponse)
async def retrieve(req: Request, request: RetrievalRequest):
    """
    Retrieves relevant document chunks from the vector database based on the query.
    """
    logger.info(f"Received retrieval request from {req.client.host} with query: \"{request.query}\"")
    try:
        # Run the synchronous retrieve method in a separate thread
        response = await asyncio.to_thread(retriever.query, request.query)
        
        # The response object from query_engine has a `response` attribute for the generated answer
        # and `source_nodes` for the retrieved documents.
        retrieved_documents = [
            RetrievedDocument(
                source=node.metadata.get("source", "Unknown"),
                content=node.get_content(),
                metadata=node.metadata,
            )
            for node in response.source_nodes
        ]
        
        logger.info(f"Successfully generated response for query: \"{request.query}\"")
        return RetrievalResponse(answer=str(response), documents=retrieved_documents)
    except Exception as e:
        logger.error(f"An error occurred during retrieval for query \"{request.query}\": {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during document retrieval.")