import os
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, SecretStr
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI

from utils.crawler import Crawler
from utils.vector_store import VectorStoreManager
from agents.graph import create_tutorial_graph, GraphState

load_dotenv()

app = FastAPI(title="Enhanced Document to Tutorial Builder", version="2.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize LLM for Q&A using DeepSeek with proper type handling
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
if deepseek_key:
    llm = ChatOpenAI(
        model="deepseek-chat",
        temperature=0.1,
        api_key=SecretStr(deepseek_key)
    )
else:
    llm = None

# Global instances
vector_store_manager = VectorStoreManager()
tutorial_graph = create_tutorial_graph()

class GenerationRequest(BaseModel):
    url: str
    depth: int

class QuestionRequest(BaseModel):
    query: str

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/tutorial/{filename}")
async def serve_tutorial(filename: str):
    """Serve generated tutorial HTML files"""
    file_path = f"generated_tutorials/{filename}"
    if os.path.exists(file_path) and filename.endswith('.html'):
        return FileResponse(file_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Tutorial not found")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            url = data.get("url")
            depth = int(data.get("depth", 2))

            if not url:
                await websocket.send_json({"type": "error", "message": "URL is required."})
                continue

            # --- 1. CRAWLING ---
            await websocket.send_json({"type": "status", "agent": "crawler", "status": "working", "progress": 10, "message": f"Starting crawl for {url}"})
            crawler = Crawler(base_url=url, max_depth=depth)
            all_pages = []
            urls_found = 0
            async for item in crawler.crawl():
                if item['type'] == 'url_found':
                    urls_found += 1
                    await websocket.send_json({"type": "stats_update", "stats": {"urlsFound": urls_found}})
                elif item['type'] == 'page_crawled':
                    await websocket.send_json({"type": "status", "agent": "content", "status": "working", "progress": 30, "message": f"Processing {item['url']}"})
                elif item['type'] == 'crawl_complete':
                    all_pages = item['content']
                    await websocket.send_json({"type": "status", "agent": "crawler", "status": "completed", "progress": 100, "message": f"Crawl complete. Found {item['total_pages']} pages."})
                    await websocket.send_json({"type": "stats_update", "stats": {"urlsProcessed": item['total_pages']}})

            if not all_pages:
                await websocket.send_json({"type": "error", "message": "Could not find any content to process."})
                continue
            
            # --- 2. VECTOR STORE UPSERT ---
            await websocket.send_json({"type": "status", "agent": "analysis", "status": "working", "progress": 10, "message": "Embedding and storing content..."})
            docs_upserted = vector_store_manager.upsert_documents(all_pages)
            await websocket.send_json({"type": "status", "agent": "analysis", "status": "completed", "progress": 100, "message": f"Stored {docs_upserted} document chunks."})

            # --- 3. LANGGRAPH TUTORIAL GENERATION ---
            full_content = "\n\n---\n\n".join([f"Source URL: {p['url']}\n\n{p['content']}" for p in all_pages])
            
            # Create properly typed initial state
            initial_state: GraphState = {
                "original_query": f"Create a comprehensive tutorial from the documentation at {url}",
                "scraped_content": full_content,
                "tutorial_outline": {},
                "section_drafts": {},
                "final_tutorial": "",
                "html_content": "",
                "error_message": "",
                "current_section_key": "0",
                "enhanced_sections": {},
                "code_examples": {},
                "concept_explanations": {}
            }

            # Stream LangGraph progress
            try:
                final_state: Optional[GraphState] = None
                async for event in tutorial_graph.astream(initial_state):
                    for key, value in event.items():
                        if key == 'generate_outline':
                            await websocket.send_json({"type": "status", "agent": "structure", "status": "working", "progress": 25, "message": "Generating tutorial outline..."})
                        elif key == 'write_section':
                            section_key = value.get('current_section_key', 'unknown') if value else 'unknown'
                            await websocket.send_json({"type": "status", "agent": "tutorial", "status": "working", "progress": 50, "message": f"Writing section: {section_key}"})
                        elif key == 'compile_tutorial':
                            await websocket.send_json({"type": "status", "agent": "tutorial", "status": "working", "progress": 90, "message": "Compiling final tutorial..."})
                            final_state = value
                
                # Fallback if final_state is not captured
                if not final_state:
                    final_state = tutorial_graph.invoke(initial_state)
            except Exception as e:
                print(f"Error in tutorial generation: {e}")
                await websocket.send_json({"type": "error", "message": f"Tutorial generation failed: {str(e)}"})
                continue

            if final_state and final_state.get("error_message"):
                await websocket.send_json({"type": "error", "message": final_state["error_message"]})
            elif final_state:
                # --- 4. SEND FINAL RESULT ---
                await websocket.send_json({"type": "status", "agent": "tutorial", "status": "completed", "progress": 100, "message": "Tutorial generation complete!"})
                
                # Get the tutorial outline safely
                tutorial_outline = final_state.get('tutorial_outline', {})
                section_drafts = final_state.get('section_drafts', {})
                
                # Create a comprehensive result for the frontend
                result_data = {
                    "title": tutorial_outline.get('title', 'Generated Tutorial'),
                    "description": "A comprehensive tutorial generated by the AI agent system.",
                    "html_content": final_state.get('html_content', ''),
                    "sections": [
                        {
                            "title": s.get('title', f'Section {i+1}'), 
                            "content": section_drafts.get(str(i), "")
                        }
                        for i, s in enumerate(tutorial_outline.get('sections', []))
                    ]
                }
                await websocket.send_json({"type": "result", "data": result_data})
            else:
                await websocket.send_json({"type": "error", "message": "Tutorial generation failed: No result returned"})

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"An error occurred: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass

# Enhanced Q&A endpoint
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    if not llm:
        return {"error": "Q&A service not available. Please configure DEEPSEEK_API_KEY."}
    
    try:
        context_docs = await vector_store_manager.query(request.query)
        if not context_docs:
            return {"answer": "I don't have any relevant information to answer your question. Please make sure you've generated a tutorial first.", "sources": []}
        
        context = "\n\n".join([doc['text'] for doc in context_docs])

        prompt = ChatPromptTemplate.from_template(
            """You are a helpful assistant that answers questions based on documentation content.
            Provide clear, accurate answers based on the context provided.
            If the context doesn't contain enough information to answer the question, say so politely.

            Context from documentation:
            {context}

            Question: {question}
            
            Answer:"""
        )
        chain = prompt | llm | StrOutputParser()
        answer = await chain.ainvoke({"context": context, "question": request.query})
        
        # Get unique source URLs
        sources = list(set([doc['metadata']['source_url'] for doc in context_docs if 'metadata' in doc and 'source_url' in doc['metadata']]))
        
        return {"answer": answer, "sources": sources}
    except Exception as e:
        return {"error": f"Failed to process question: {str(e)}"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}