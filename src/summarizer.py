"""
Summarization Engine for Meeting Minutes

Uses Claude AI to create concise summaries from transcript chunks.
Handles the core AI processing that turns raw conversation into structured minutes.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import json


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
    Orchestrates the summarization process using Claude AI.
    
    This class handles:
    1. Processing individual chunks
    2. Combining chunk summaries into final report
    3. Extracting structured data (action items, decisions)
    """
    
    def __init__(self):
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
        # This is where we would call Claude API
        # For now, we'll simulate the response structure
        
        prompt = f"""
        {self.summarization_prompt}
        
        Context from previous discussion: {context}
        
        Transcript chunk to summarize:
        {chunk_content}
        
        Please provide your response in the following JSON format:
        {{
            "summary": "Brief summary of this section",
            "key_points": ["point 1", "point 2"],
            "decisions_made": ["decision 1", "decision 2"],
            "action_items": ["action 1", "action 2"],
            "speakers_mentioned": ["speaker 1", "speaker 2"],
            "topics_discussed": ["topic 1", "topic 2"]
        }}
        """
        
        # Simulate Claude API call
        # In real implementation: response = claude_api.call(prompt)
        simulated_response = self._simulate_claude_response(chunk_content, chunk_id)
        
        return ChunkSummary(
            chunk_id=chunk_id,
            summary=simulated_response["summary"],
            key_points=simulated_response["key_points"],
            decisions_made=simulated_response["decisions_made"],
            action_items=simulated_response["action_items"],
            speakers_mentioned=simulated_response["speakers_mentioned"],
            topics_discussed=simulated_response["topics_discussed"]
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
        You are an expert meeting minutes summarizer. Your task is to extract key information from this meeting transcript segment.
        
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
    
    def _simulate_claude_response(self, content: str, chunk_id: int) -> Dict:
        """
        Simulate Claude API response for development/testing.
        In production, this would be replaced with actual Claude API calls.
        """
        # Simple simulation based on content
        words = content.lower().split()
        
        # Simulate finding action items
        action_items = []
        if "will" in words or "follow up" in content.lower():
            action_items.append("Follow up on discussed items")
        if "by friday" in content.lower() or "next week" in content.lower():
            action_items.append("Complete task by specified deadline")
        
        # Simulate finding decisions
        decisions = []
        if "decide" in words or "agreed" in words:
            decisions.append("Agreement reached on discussed matter")
        
        # Simulate finding speakers
        speakers = []
        import re
        speaker_matches = re.findall(r'^([A-Z][a-z]+ ?[A-Z]?[a-z]*):?', content, re.MULTILINE)
        speakers.extend(speaker_matches)
        
        return {
            "summary": f"Discussion covered various topics with {len(speakers)} participants",
            "key_points": [f"Point {i+1} from chunk {chunk_id}" for i in range(2)],
            "decisions_made": decisions,
            "action_items": action_items,
            "speakers_mentioned": list(set(speakers)),
            "topics_discussed": ["General discussion", "Planning"]
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
        # In production, this would use Claude API
        # For now, create a simple template-based summary
        
        topic_str = ", ".join(topics[:3]) if topics else "various topics"
        word_count = len(combined_text.split())
        
        return f"""
        Meeting covered {topic_str} with substantive discussion across multiple areas. 
        Key decisions were made and action items assigned to team members.
        Discussion was comprehensive with {word_count} words of detailed conversation.
        """.strip()


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
    print(f"Chunk summary: {chunk_summary.summary}")
    print(f"Action items found: {chunk_summary.action_items}")
    print(f"Speakers: {chunk_summary.speakers_mentioned}")