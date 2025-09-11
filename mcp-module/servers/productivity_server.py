#!/usr/bin/env python3
"""
Productivity MCP Server - Complete Implementation
Implements all three MCP primitives: tools, resources, and prompts
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import os

# Use FastMCP directly
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Productivity MCP Server")

@mcp.tool()
def email_summarizer(email_content: str) -> str:
    """
    Summarize email content for quick review
    
    Args:
        email_content: Full email content to summarize
        
    Returns:
        Email summary as JSON string
    """
    try:
        # Simple summarization logic
        lines = email_content.split('\n')
        subject = lines[0] if lines else "No subject"
        body = '\n'.join(lines[1:]) if len(lines) > 1 else email_content
        
        # Count key metrics
        word_count = len(body.split())
        sentence_count = len([s for s in body.split('.') if s.strip()])
        
        summary = {
            "subject": subject,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "key_points": [
                "Email received and processed",
                f"Contains {word_count} words",
                f"Has {sentence_count} sentences"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Email summarized: {word_count} words")
        return json.dumps(summary)
        
    except Exception as e:
        logger.error(f"Error summarizing email: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def schedule_meeting(title: str, duration: int, participants: List[str]) -> str:
    """
    Schedule a meeting with given parameters
    
    Args:
        title: Meeting title
        duration: Meeting duration in minutes
        participants: List of participant email addresses
        
    Returns:
        Meeting details as JSON string
    """
    try:
        meeting = {
            "title": title,
            "duration_minutes": duration,
            "participants": participants,
            "scheduled_time": datetime.now().isoformat(),
            "meeting_id": f"meeting_{hash(title) % 10000}",
            "status": "scheduled",
            "notes": f"Meeting scheduled for {duration} minutes with {len(participants)} participants"
        }
        
        logger.info(f"Meeting scheduled: {title} with {len(participants)} participants")
        return json.dumps(meeting)
        
    except Exception as e:
        logger.error(f"Error scheduling meeting: {e}")
        return json.dumps({"error": str(e)})

@mcp.resource("productivity://docs/{doc_id}")
def get_document(doc_id: str) -> str:
    """
    Get document content by ID
    
    Args:
        doc_id: Document identifier
        
    Returns:
        Document content as JSON string
    """
    try:
        # Mock document content
        document = {
            "doc_id": doc_id,
            "title": f"Document {doc_id}",
            "content": f"This is the content of document {doc_id}. It contains important information for productivity tasks.",
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "author": "productivity_system",
            "tags": ["productivity", "document", "work"]
        }
        
        logger.info(f"Document retrieved: {doc_id}")
        return json.dumps(document)
        
    except Exception as e:
        logger.error(f"Error getting document {doc_id}: {e}")
        return json.dumps({"error": str(e)})

@mcp.resource("productivity://calendar/{user_id}")
def get_calendar(user_id: str) -> str:
    """
    Get calendar data for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Calendar data as JSON string
    """
    try:
        # Mock calendar data
        calendar = {
            "user_id": user_id,
            "events": [
                {
                    "id": "event_1",
                    "title": "Team Meeting",
                    "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "location": "Conference Room A"
                },
                {
                    "id": "event_2", 
                    "title": "Project Review",
                    "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "location": "Virtual"
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info(f"Calendar retrieved for user: {user_id}")
        return json.dumps(calendar)
        
    except Exception as e:
        logger.error(f"Error getting calendar for {user_id}: {e}")
        return json.dumps({"error": str(e)})

@mcp.prompt("meeting_agenda")
def meeting_agenda_prompt(meeting_context: str) -> str:
    """
    Generate meeting agenda prompt based on context
    
    Args:
        meeting_context: Meeting context or topic
        
    Returns:
        Meeting agenda prompt
    """
    try:
        prompt = f"""
Based on the following meeting context: {meeting_context}

Please create a comprehensive meeting agenda including:

1. **Meeting Objectives**: What are the main goals of this meeting?
2. **Agenda Items**: What topics should be covered and in what order?
3. **Time Allocation**: How much time should be allocated to each agenda item?
4. **Preparation Required**: What should participants prepare before the meeting?
5. **Expected Outcomes**: What decisions or actions should result from this meeting?
6. **Follow-up Actions**: What follow-up tasks should be assigned?

Consider:
- Meeting duration and participant availability
- Priority of topics
- Decision-making requirements
- Information sharing needs
- Action item assignments

Provide a structured agenda that maximizes meeting effectiveness.
"""
        
        logger.info(f"Meeting agenda prompt generated for context: {meeting_context[:50]}...")
        return prompt
        
    except Exception as e:
        logger.error(f"Error generating meeting agenda prompt: {e}")
        return f"Error generating prompt: {str(e)}"

def main():
    """Main server function"""
    logger.info("Starting Productivity MCP Server on port 3002")
    
    try:
        # Run the server using FastMCP's built-in runner
        mcp.run(transport="http", port=3002)
    except Exception as e:
        logger.error(f"Error running Productivity MCP Server: {e}")
        raise

if __name__ == "__main__":
    main()
