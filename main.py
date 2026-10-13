"""Call center resolution system API."""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn
from contextlib import asynccontextmanager
from typing import List, Optional
import logging
import io

from models import CallCenterRequest, CallCenterResponse
from orchestrator import MultiAgentOrchestrator
from config import config
from speech_handler import speech_handler

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    global orchestrator
    logger.info("Starting orchestrator...")
    orchestrator = MultiAgentOrchestrator()
    logger.info("System ready")
    yield
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Call Center Resolution System",
    description="Multi-agent platform for automated call center operational enquiries",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Call Center Resolution System API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "orchestrator_ready": orchestrator is not None
    }


@app.post("/api/v1/inquiry", response_model=CallCenterResponse)
async def handle_inquiry(request: CallCenterRequest):
    """Handle customer inquiry."""
    try:
        if orchestrator is None:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        
        logger.info(f"Processing inquiry for customer {request.customer_id}: {request.inquiry_text[:50]}...")
        
        response = await orchestrator.process_request(request)
        
        logger.info(
            f"Inquiry resolved: {response.resolved}, "
            f"query_type: {response.query_type}, "
            f"execution_time: {response.execution_time_ms:.2f}ms"
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing inquiry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/inquiry/batch", response_model=List[CallCenterResponse])
async def handle_batch_inquiry(requests: List[CallCenterRequest]):
    """Handle batch inquiries."""
    try:
        if orchestrator is None:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        
        logger.info(f"Processing batch of {len(requests)} inquiries")
        
        responses = await orchestrator.process_batch(requests)
        
        logger.info(f"Batch processing complete: {len(responses)} responses generated")
        
        return responses
    
    except Exception as e:
        logger.error(f"Error processing batch inquiry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/stats")
async def get_statistics():
    """Get system statistics."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    stats = {
        "agents": {
            "appointment": len(orchestrator.appointment_agent.history),
            "insurance": len(orchestrator.insurance_agent.history),
            "report": len(orchestrator.report_agent.history),
            "knowledge_base": len(orchestrator.kb_agent.history)
        },
        "status": "operational",
        "speech_services": {
            "stt_configured": speech_handler.speech_client is not None,
            "tts_configured": speech_handler.tts_client is not None,
            "enabled": config.ENABLE_STT_TTS
        }
    }
    
    return stats


@app.post("/api/v1/voice/inquiry")
async def handle_voice_inquiry(
    customer_id: str = Form(...),
    audio_file: UploadFile = File(...),
    phone_number: Optional[str] = Form(None)
):
    """
    Handle a voice inquiry from a customer call.
    Accepts audio file, converts to text, processes through multi-agent system,
    and returns both text and audio response.
    
    Args:
        customer_id: Customer identifier
        audio_file: Audio file (WAV, FLAC, or LINEAR16 format)
        phone_number: Optional phone number
        
    Returns:
        JSON response with text and audio URL, or audio file directly
    """
    try:
        if orchestrator is None:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        
        # Read audio content
        audio_content = await audio_file.read()
        logger.info(f"Received voice inquiry from customer {customer_id}, audio size: {len(audio_content)} bytes")
        
        # Convert speech to text
        transcribed_text, confidence = speech_handler.speech_to_text(audio_content)
        logger.info(f"Transcribed text: {transcribed_text[:100]}... (confidence: {confidence:.2%})")
        
        if not transcribed_text or confidence < 0.3:
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe audio. Please ensure audio is clear and in supported format."
            )
        
        # Create request and process through orchestrator
        request = CallCenterRequest(
            customer_id=customer_id,
            inquiry_text=transcribed_text,
            phone_number=phone_number,
            context={"source": "voice", "stt_confidence": confidence}
        )
        
        response = await orchestrator.process_request(request)
        
        # Convert response text to speech
        audio_response = speech_handler.text_to_speech(response.response_text)
        
        # Return response with audio
        result = {
            "request_id": response.request_id,
            "customer_id": customer_id,
            "transcribed_text": transcribed_text,
            "response_text": response.response_text,
            "query_type": response.query_type.value,
            "resolved": response.resolved,
            "stt_confidence": confidence,
            "execution_time_ms": response.execution_time_ms,
            "audio_available": audio_response is not None and len(audio_response) > 0
        }
        
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing voice inquiry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/voice/inquiry/audio")
async def handle_voice_inquiry_audio(
    customer_id: str = Form(...),
    audio_file: UploadFile = File(...),
    phone_number: Optional[str] = Form(None)
):
    """
    Handle voice inquiry and return audio response directly.
    Perfect for real-time call center integration.
    
    Args:
        customer_id: Customer identifier
        audio_file: Audio file
        phone_number: Optional phone number
        
    Returns:
        Audio file (WAV format) with synthesized response
    """
    try:
        if orchestrator is None:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        
        # Read and transcribe
        audio_content = await audio_file.read()
        transcribed_text, confidence = speech_handler.speech_to_text(audio_content)
        
        if not transcribed_text or confidence < 0.3:
            # Return error message as audio
            error_audio = speech_handler.text_to_speech(
                "I'm sorry, I couldn't understand your request. Please try again."
            )
            if error_audio:
                return Response(
                    content=error_audio,
                    media_type="audio/wav",
                    headers={"Content-Disposition": "attachment; filename=response.wav"}
                )
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # Process inquiry
        request = CallCenterRequest(
            customer_id=customer_id,
            inquiry_text=transcribed_text,
            phone_number=phone_number
        )
        
        response = await orchestrator.process_request(request)
        
        # Convert to speech
        audio_response = speech_handler.text_to_speech(response.response_text)
        
        if not audio_response:
            raise HTTPException(status_code=500, detail="Could not generate audio response")
        
        return Response(
            content=audio_response,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=response.wav",
                "X-Request-ID": response.request_id,
                "X-Resolved": str(response.resolved)
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing voice inquiry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/voice/text-to-speech")
async def text_to_speech_endpoint(text: str = Form(...), language_code: Optional[str] = Form(None)):
    """
    Convert text to speech audio.
    
    Args:
        text: Text to convert to speech
        language_code: Optional language code (defaults to config)
        
    Returns:
        Audio file (WAV format)
    """
    try:
        audio_content = speech_handler.text_to_speech(text, language_code)
        
        if not audio_content:
            raise HTTPException(status_code=500, detail="Could not generate speech")
        
        return Response(
            content=audio_content,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
    
    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/voice/speech-to-text")
async def speech_to_text_endpoint(audio_file: UploadFile = File(...), language_code: Optional[str] = Form(None)):
    """
    Convert speech audio to text.
    
    Args:
        audio_file: Audio file (WAV, FLAC, or LINEAR16 format)
        language_code: Optional language code (defaults to config)
        
    Returns:
        JSON with transcribed text and confidence
    """
    try:
        audio_content = await audio_file.read()
        transcribed_text, confidence = speech_handler.speech_to_text(audio_content, language_code)
        
        return {
            "transcribed_text": transcribed_text,
            "confidence": confidence,
            "success": len(transcribed_text) > 0
        }
    
    except Exception as e:
        logger.error(f"Error in speech-to-text: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.ENVIRONMENT == "development",
        log_level=config.LOG_LEVEL.lower()
    )

