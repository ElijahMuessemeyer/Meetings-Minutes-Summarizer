"""
Summarization Engine for Meeting Minutes

Uses Claude AI to create concise summaries from transcript chunks.
Handles the core AI processing that turns raw conversation into structured minutes.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
import logging
import os
import re
from datetime import datetime

# AI integrations (optional imports)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ChunkSummary:
    """Container for summarized chunk data."""
    chunk_id: int
    summary: str
    key_points: List[str]
    decisions_made: List[str]
    action_items: List[str]
    speakers_mentioned: List[str]
    topics_discussed: List[str]


@dataclass
class MeetingSummary:
    """Complete meeting summary combining all chunks."""
    overall_summary: str
    key_decisions: List[str]
    action_items: List[Dict[str, str]]  # {"task": "...", "owner": "...", "deadline": "..."}
    attendees: List[str]
    main_topics: List[str]
    chunk_summaries: List[ChunkSummary]


class MeetingSummarizer:
    """
    Orchestrates the summarization process using AI APIs (Claude, OpenAI).
    
    This class handles:
    1. Processing individual chunks with AI
    2. Combining chunk summaries into final report
    3. Extracting structured data (action items, decisions)
    4. Fallback to basic processing when AI is unavailable
    """
    
    def __init__(self, ai_config: Dict[str, Any] = None):
        self.ai_config = ai_config or {}
        self.summarization_prompt = self._build_summarization_prompt()
        self.final_summary_prompt = self._build_final_summary_prompt()
    
    def summarize_chunk(self, chunk_content: str, chunk_id: int, context: str = "") -> ChunkSummary:
        """
        Summarize a single chunk of transcript.
        
        Args:
            chunk_content: Text content of the chunk
            chunk_id: Unique identifier for this chunk
            context: Additional context from previous chunks
            
        Returns:
            ChunkSummary with extracted information
        """
        # Process with AI if available, otherwise fall back to basic processing
        ai_result = self._process_with_ai(chunk_content, context)
        
        basic_summary = ai_result
        
        return ChunkSummary(
            chunk_id=chunk_id,
            summary=basic_summary["summary"],
            key_points=basic_summary["key_points"],
            decisions_made=basic_summary["decisions_made"],
            action_items=basic_summary["action_items"],
            speakers_mentioned=basic_summary["speakers_mentioned"],
            topics_discussed=basic_summary["topics_discussed"]
        )
    
    def combine_summaries(self, chunk_summaries: List[ChunkSummary]) -> MeetingSummary:
        """
        Combine individual chunk summaries into final meeting summary.
        
        Args:
            chunk_summaries: List of summarized chunks
            
        Returns:
            Complete MeetingSummary
        """
        # Aggregate data from all chunks
        all_decisions = []
        all_action_items = []
        all_speakers = set()
        all_topics = set()
        
        for chunk_summary in chunk_summaries:
            all_decisions.extend(chunk_summary.decisions_made)
            all_action_items.extend(chunk_summary.action_items)
            all_speakers.update(chunk_summary.speakers_mentioned)
            all_topics.update(chunk_summary.topics_discussed)
        
        # Create structured action items
        structured_actions = self._structure_action_items(all_action_items)
        
        # Generate overall summary
        combined_text = " ".join([cs.summary for cs in chunk_summaries])
        overall_summary = self._generate_overall_summary(combined_text, list(all_topics))
        
        return MeetingSummary(
            overall_summary=overall_summary,
            key_decisions=list(set(all_decisions)),  # Remove duplicates
            action_items=structured_actions,
            attendees=sorted(list(all_speakers)),
            main_topics=sorted(list(all_topics)),
            chunk_summaries=chunk_summaries
        )
    
    def _build_summarization_prompt(self) -> str:
        """Create the prompt template for chunk summarization."""
        return """
        You are an expert meeting minutes summarizer. Your task is to extract key 
        information from this meeting transcript segment.
        
        Focus on:
        1. Main discussion points and decisions
        2. Action items with clear owners when mentioned
        3. Important topics and themes
        4. Who spoke and their key contributions
        
        Be concise but comprehensive. Capture the essential meaning without unnecessary detail.
        """
    
    def _build_final_summary_prompt(self) -> str:
        """Create the prompt template for final summary generation."""
        return """
        Create a cohesive overall summary from these meeting segment summaries.
        Focus on the main themes, outcomes, and flow of the discussion.
        Keep it executive-level - clear and actionable.
        """
    
    def _create_basic_summary(self, content: str, chunk_id: int) -> Dict[str, Any]:
        """
        Create a basic summary using simple text processing.
        This is a fallback when AI integration is not available.
        """
        import re
        
        words = content.lower().split()
        sentences = content.split('.')
        
        # Extract speakers using pattern matching
        speakers = []
        speaker_matches = re.findall(r'^([A-Z][a-z]+ ?[A-Z]?[a-z]*):?', content, re.MULTILINE)
        speakers.extend(speaker_matches)
        
        # Extract potential action items using keyword patterns
        action_items = []
        action_patterns = [
            r'will ([^.]+)',
            r'need to ([^.]+)',
            r'should ([^.]+)',
            r'follow up ([^.]+)',
            r'complete ([^.]+)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content.lower())
            action_items.extend(matches[:2])  # Limit to 2 per pattern
        
        # Extract potential decisions using keyword patterns
        decisions = []
        if any(word in words for word in ['decide', 'decided', 'agreed', 'approve', 'approved']):
            decisions.append("Decision made during discussion")
        
        # Extract key topics (simplified approach)
        key_words = [word for word in words if len(word) > 5 and word.isalpha()]
        topics = list(set(key_words[:3]))  # Take first 3 unique long words as topics
        
        # Create key points from first few sentences
        key_points = [sentence.strip() for sentence in sentences[:2] if sentence.strip()]
        
        return {
            "summary": (
                f"Discussion segment {chunk_id} with {len(set(speakers))} participants "
                f"covering {len(topics)} main topics"
            ),
            "key_points": key_points[:3],  # Limit to 3 key points
            "decisions_made": decisions[:2],  # Limit to 2 decisions
            "action_items": action_items[:3],  # Limit to 3 action items
            "speakers_mentioned": list(set(speakers)),
            "topics_discussed": topics
        }
    
    def _structure_action_items(self, raw_actions: List[str]) -> List[Dict[str, str]]:
        """Convert raw action items into structured format."""
        structured = []
        
        for action in raw_actions:
            # Try to extract owner and deadline from text
            owner = "TBD"
            deadline = "TBD"
            task = action
            
            # Simple pattern matching for common formats
            if " by " in action.lower():
                parts = action.lower().split(" by ")
                if len(parts) == 2:
                    task = parts[0].strip()
                    deadline = parts[1].strip()
            
            # Look for names (simple heuristic)
            import re
            name_match = re.search(r'\b([A-Z][a-z]+)\b', action)
            if name_match:
                owner = name_match.group(1)
            
            structured.append({
                "task": task,
                "owner": owner,
                "deadline": deadline
            })
        
        return structured
    
    def _generate_overall_summary(self, combined_text: str, topics: List[str]) -> str:
        """Generate executive summary from combined chunk summaries."""
        
        topic_str = ", ".join(topics[:3]) if topics else "various topics"
        word_count = len(combined_text.split())
        
        return f"""
        Meeting covered {topic_str} with substantive discussion across multiple areas. 
        Key decisions were made and action items assigned to team members.
        Discussion was comprehensive with {word_count} words of detailed conversation.
        """.strip()
    
    def _process_with_ai(self, content: str, context: str = "") -> Dict[str, Any]:
        """
        Process text using AI API (Claude, OpenAI, etc.)
        
        Args:
            content: Text to process
            context: Previous context for continuity
            
        Returns:
            Dictionary with summary data
        """
        # Try Claude (Anthropic) first if available
        if self._is_anthropic_configured():
            try:
                return self._process_with_claude(content, context)
            except Exception as e:
                logger.warning(f"Claude API failed: {str(e)}, falling back to OpenAI")
        
        # Try OpenAI if available
        if self._is_openai_configured():
            try:
                return self._process_with_openai(content, context)
            except Exception as e:
                logger.warning(f"OpenAI API failed: {str(e)}, falling back to basic processing")
        
        # Fall back to basic processing
        logger.warning("No AI API configured or available - using basic text processing")
        return self._create_basic_summary(content, 0)
    
    def _is_anthropic_configured(self) -> bool:
        """Check if Anthropic (Claude) API is configured and available."""
        if not ANTHROPIC_AVAILABLE:
            return False
        
        api_key = (
            self.ai_config.get('anthropic_api_key') or 
            os.getenv('ANTHROPIC_API_KEY') or 
            os.getenv('CLAUDE_API_KEY')
        )
        return bool(api_key)
    
    def _is_openai_configured(self) -> bool:
        """Check if OpenAI API is configured and available."""
        if not OPENAI_AVAILABLE:
            return False
        
        api_key = (
            self.ai_config.get('openai_api_key') or 
            os.getenv('OPENAI_API_KEY')
        )
        return bool(api_key)
    
    def _process_with_claude(self, content: str, context: str = "") -> Dict[str, Any]:
        """Process text using Anthropic's Claude API."""
        logger.info("Processing with Claude API")
        
        api_key = (
            self.ai_config.get('anthropic_api_key') or 
            os.getenv('ANTHROPIC_API_KEY') or 
            os.getenv('CLAUDE_API_KEY')
        )
        
        client = Anthropic(api_key=api_key)
        
        # Build the prompt
        prompt = self._build_ai_prompt(content, context)
        
        # Get model from config or use default
        model = self.ai_config.get('claude_model', 'claude-3-haiku-20240307')
        
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return self._parse_ai_response(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise
    
    def _process_with_openai(self, content: str, context: str = "") -> Dict[str, Any]:
        """Process text using OpenAI's GPT API."""
        logger.info("Processing with OpenAI API")
        
        api_key = (
            self.ai_config.get('openai_api_key') or 
            os.getenv('OPENAI_API_KEY')
        )
        
        client = openai.OpenAI(api_key=api_key)
        
        # Build the prompt
        prompt = self._build_ai_prompt(content, context)
        
        # Get model from config or use default
        model = self.ai_config.get('openai_model', 'gpt-3.5-turbo')
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert meeting minutes assistant. Extract structured information from meeting transcripts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return self._parse_ai_response(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _build_ai_prompt(self, content: str, context: str = "") -> str:
        """Build a comprehensive prompt for AI processing."""
        prompt_parts = [
            "Please analyze this meeting transcript segment and extract structured information.",
            "",
            "Extract the following information in JSON format:",
            "{",
            '  "summary": "Brief 2-3 sentence summary of this segment",',
            '  "key_points": ["List of 2-4 key discussion points"],',
            '  "decisions_made": ["List of concrete decisions made"],',
            '  "action_items": ["List of specific actions to be taken"],',
            '  "speakers_mentioned": ["List of people who spoke"],',
            '  "topics_discussed": ["List of main topics covered"]',
            "}",
            "",
            "Guidelines:",
            "- Only include information explicitly mentioned in the transcript",
            "- Action items should be specific and actionable",
            "- Decisions should be concrete outcomes, not just discussions",
            "- Use exact names when mentioned",
            "- Focus on substantive content, not casual remarks",
            ""
        ]
        
        if context:
            prompt_parts.extend([
                "Previous context for continuity:",
                f"{context}",
                ""
            ])
        
        prompt_parts.extend([
            "Transcript segment to analyze:",
            f"{content}",
            "",
            "Please provide only the JSON response without additional commentary:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured data."""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Validate and clean the response
                return {
                    'summary': parsed.get('summary', ''),
                    'key_points': parsed.get('key_points', []),
                    'decisions_made': parsed.get('decisions_made', []),
                    'action_items': parsed.get('action_items', []),
                    'speakers_mentioned': parsed.get('speakers_mentioned', []),
                    'topics_discussed': parsed.get('topics_discussed', [])
                }
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse AI response as JSON: {str(e)}")
            # Fall back to basic text processing of the AI response
            return self._extract_from_text_response(response_text)
    
    def _extract_from_text_response(self, response_text: str) -> Dict[str, Any]:
        """Extract information from AI response when JSON parsing fails."""
        logger.info("Extracting from text response as fallback")
        
        # This is a fallback when AI doesn't return proper JSON
        # We'll do basic pattern matching on the response
        
        lines = response_text.split('\n')
        summary = ""
        key_points = []
        action_items = []
        decisions = []
        speakers = []
        topics = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'summary' in line.lower() and ':' in line:
                current_section = 'summary'
                summary = line.split(':', 1)[1].strip().strip('"')
            elif 'key' in line.lower() and 'point' in line.lower():
                current_section = 'key_points'
            elif 'action' in line.lower() and 'item' in line.lower():
                current_section = 'action_items'
            elif 'decision' in line.lower():
                current_section = 'decisions'
            elif 'speaker' in line.lower():
                current_section = 'speakers'
            elif 'topic' in line.lower():
                current_section = 'topics'
            elif line.startswith('-') or line.startswith('*') or line.startswith('•'):
                # List item
                item_text = line[1:].strip()
                if current_section == 'key_points':
                    key_points.append(item_text)
                elif current_section == 'action_items':
                    action_items.append(item_text)
                elif current_section == 'decisions':
                    decisions.append(item_text)
                elif current_section == 'speakers':
                    speakers.append(item_text)
                elif current_section == 'topics':
                    topics.append(item_text)
        
        # If we didn't extract much, fall back to basic processing
        if not summary and not key_points and not action_items:
            return self._create_basic_summary(response_text, 0)
        
        return {
            'summary': summary or f"AI processing of {len(response_text.split())} words of meeting content",
            'key_points': key_points,
            'decisions_made': decisions,
            'action_items': action_items,
            'speakers_mentioned': speakers,
            'topics_discussed': topics
        }


# Usage example
if __name__ == "__main__":
    summarizer = MeetingSummarizer()
    
    sample_chunk = """
    John Smith: Let's discuss the Q4 budget allocation. I think we need to increase marketing spend.
    Sarah Johnson: I agree, John. Our CAC has been improving. I'll prepare a detailed proposal by Friday.
    Mike Davis: What about the engineering budget? We need more resources for the new feature development.
    John Smith: Good point Mike. Sarah, please include engineering resources in your proposal.
    """
    
    chunk_summary = summarizer.summarize_chunk(sample_chunk, 0)
    logger.debug(f"Chunk summary: {chunk_summary.summary}")
    logger.debug(f"Action items found: {chunk_summary.action_items}")
    logger.debug(f"Speakers: {chunk_summary.speakers_mentioned}")