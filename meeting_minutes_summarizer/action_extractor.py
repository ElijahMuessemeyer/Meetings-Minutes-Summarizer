"""
Action Item Extraction for Meeting Minutes

Advanced extraction and structuring of action items from meeting transcripts.
Identifies tasks, owners, deadlines, and priorities with high accuracy.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ActionItem:
    """Structured action item with all relevant details."""
    task: str
    owner: Optional[str]
    deadline: Optional[str]
    priority: str  # "high", "medium", "low"
    status: str    # "pending", "in_progress", "completed"
    context: str   # Surrounding conversation for reference
    confidence: float  # How confident we are this is actually an action item


class ActionItemExtractor:
    """
    Extracts and structures action items from meeting transcripts.
    
    Uses multiple techniques:
    1. Pattern matching for common action phrases
    2. Context analysis for ownership and timing
    3. Priority assessment based on language and urgency
    """
    
    def __init__(self):
        # Patterns that typically indicate action items
        self.action_patterns = [
            r"(.*?)\s+will\s+(.*?)(?:\.|$)",
            r"(.*?)\s+should\s+(.*?)(?:\.|$)",
            r"(.*?)\s+needs? to\s+(.*?)(?:\.|$)",
            r"(.*?)\s+can you\s+(.*?)(?:\.|$)",
            r"please\s+(.*?)(?:\.|$)",
            r"I'll\s+(.*?)(?:\.|$)",
            r"we need to\s+(.*?)(?:\.|$)",
            r"action item:?\s*(.*?)(?:\.|$)",
            r"follow up on\s+(.*?)(?:\.|$)",
            r"(.*?)\s+to do\s+(.*?)(?:\.|$)",
        ]
        
        # Deadline indicators
        self.deadline_patterns = [
            r"by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"by\s+(next week|this week|end of week)",
            r"by\s+(tomorrow|today|end of day)",
            r"by\s+(\d{1,2}/\d{1,2})",
            r"by\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}",
            r"in\s+(\d+)\s+(days?|weeks?|months?)",
            r"(asap|urgent|immediately)",
        ]
        
        # Priority indicators
        self.priority_indicators = {
            "high": ["urgent", "asap", "critical", "immediately", "priority", "important"],
            "medium": ["soon", "this week", "next week", "should"],
            "low": ["when possible", "eventually", "nice to have", "if time permits"]
        }
        
        # Common name patterns for ownership
        self.name_patterns = [
            r"\b([A-Z][a-z]+)\s+will\b",
            r"\b([A-Z][a-z]+)\s+can\b",
            r"\b([A-Z][a-z]+)\s+should\b",
            r"\b([A-Z][a-z]+),?\s+please\b",
            r"^([A-Z][a-z]+):\s",  # Speaker attribution
        ]
    
    def extract_action_items(self, text: str, speakers: List[str] = None) -> List[ActionItem]:
        """
        Extract all action items from transcript text.
        
        Args:
            text: Meeting transcript or chunk
            speakers: Known speakers for better name recognition
            
        Returns:
            List of structured ActionItem objects
        """
        action_items = []
        sentences = self._split_into_sentences(text)
        
        for i, sentence in enumerate(sentences):
            # Check if sentence contains action item patterns
            for pattern in self.action_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    action_item = self._build_action_item(
                        sentence, match, sentences, i, speakers or []
                    )
                    if action_item and action_item.confidence > 0.5:
                        action_items.append(action_item)
        
        # Deduplicate similar action items
        return self._deduplicate_actions(action_items)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for analysis."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _build_action_item(self, sentence: str, match: re.Match, 
                          all_sentences: List[str], sentence_idx: int,
                          speakers: List[str]) -> Optional[ActionItem]:
        """
        Build structured ActionItem from pattern match.
        
        Args:
            sentence: The sentence containing the action
            match: Regex match object
            all_sentences: All sentences for context
            sentence_idx: Index of current sentence
            speakers: Known speakers
        """
        # Extract task description
        if match.groups():
            if len(match.groups()) >= 2:
                owner_part = match.group(1).strip()
                task_part = match.group(2).strip()
            else:
                owner_part = ""
                task_part = match.group(1).strip()
        else:
            task_part = sentence
            owner_part = ""
        
        # Skip if task is too short or generic
        if len(task_part.split()) < 2:
            return None
        
        # Extract owner
        owner = self._extract_owner(sentence, owner_part, speakers)
        
        # Extract deadline
        deadline = self._extract_deadline(sentence)
        
        # Determine priority
        priority = self._determine_priority(sentence)
        
        # Get context (surrounding sentences)
        context = self._get_context(all_sentences, sentence_idx)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(sentence, owner, deadline, task_part)
        
        return ActionItem(
            task=task_part,
            owner=owner,
            deadline=deadline,
            priority=priority,
            status="pending",
            context=context,
            confidence=confidence
        )
    
    def _extract_owner(self, sentence: str, owner_part: str, speakers: List[str]) -> Optional[str]:
        """Extract the person responsible for the action."""
        # First check the owner_part from pattern match
        if owner_part:
            # Check if it's a known speaker
            owner_words = owner_part.split()
            for word in owner_words:
                if any(word.lower() in speaker.lower() for speaker in speakers):
                    return word
        
        # Look for name patterns in the sentence
        for pattern in self.name_patterns:
            match = re.search(pattern, sentence)
            if match:
                potential_owner = match.group(1)
                if any(potential_owner.lower() in speaker.lower() for speaker in speakers):
                    return potential_owner
        
        # Check for pronouns that might indicate self-assignment
        if re.search(r'\bI\'ll\b|\bI will\b|\bI can\b', sentence, re.IGNORECASE):
            # Try to find the speaker from context
            speaker_match = re.match(r'^([A-Z][a-z]+):', sentence)
            if speaker_match:
                return speaker_match.group(1)
        
        return None
    
    def _extract_deadline(self, sentence: str) -> Optional[str]:
        """Extract deadline information from sentence."""
        sentence_lower = sentence.lower()
        
        for pattern in self.deadline_patterns:
            match = re.search(pattern, sentence_lower)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        
        return None
    
    def _determine_priority(self, sentence: str) -> str:
        """Determine priority level based on language used."""
        sentence_lower = sentence.lower()
        
        for priority, indicators in self.priority_indicators.items():
            if any(indicator in sentence_lower for indicator in indicators):
                return priority
        
        # Default to medium if no clear indicators
        return "medium"
    
    def _get_context(self, sentences: List[str], current_idx: int, context_size: int = 1) -> str:
        """Get surrounding sentences for context."""
        start = max(0, current_idx - context_size)
        end = min(len(sentences), current_idx + context_size + 1)
        context_sentences = sentences[start:end]
        return " ".join(context_sentences)
    
    def _calculate_confidence(self, sentence: str, owner: Optional[str], 
                            deadline: Optional[str], task: str) -> float:
        """Calculate confidence score for action item detection."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for clear action verbs
        action_verbs = ["will", "send", "prepare", "schedule", "follow up", "review", "complete"]
        if any(verb in sentence.lower() for verb in action_verbs):
            confidence += 0.2
        
        # Boost for clear ownership
        if owner:
            confidence += 0.2
        
        # Boost for deadline
        if deadline:
            confidence += 0.15
        
        # Boost for specific task description
        if len(task.split()) >= 3:
            confidence += 0.1
        
        # Reduce for vague language
        vague_terms = ["maybe", "perhaps", "might", "could"]
        if any(term in sentence.lower() for term in vague_terms):
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def _deduplicate_actions(self, actions: List[ActionItem]) -> List[ActionItem]:
        """Remove duplicate or very similar action items."""
        if not actions:
            return actions
        
        unique_actions = []
        
        for action in actions:
            is_duplicate = False
            for existing in unique_actions:
                # Simple similarity check
                if (self._similarity_score(action.task, existing.task) > 0.8 and
                    action.owner == existing.owner):
                    is_duplicate = True
                    # Keep the one with higher confidence
                    if action.confidence > existing.confidence:
                        unique_actions.remove(existing)
                        unique_actions.append(action)
                    break
            
            if not is_duplicate:
                unique_actions.append(action)
        
        return sorted(unique_actions, key=lambda x: x.confidence, reverse=True)
    
    def _similarity_score(self, text1: str, text2: str) -> float:
        """Simple text similarity score."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


# Example usage
if __name__ == "__main__":
    extractor = ActionItemExtractor()
    
    sample_text = """
    John Smith: Sarah, can you please send the quarterly report by Friday?
    Sarah Johnson: Absolutely, I'll prepare the report and send it by end of day Friday.
    Mike Davis: We also need to schedule a follow-up meeting next week.
    John Smith: Good point Mike. Sarah, please coordinate with everyone's calendars.
    Sarah Johnson: Will do. I'll send out calendar invites by tomorrow.
    """
    
    speakers = ["John Smith", "Sarah Johnson", "Mike Davis"]
    actions = extractor.extract_action_items(sample_text, speakers)
    
    logger.info(f"Found {len(actions)} action items:")
    for action in actions:
        logger.debug(
            f"- {action.task} (Owner: {action.owner}, "
            f"Deadline: {action.deadline}, Priority: {action.priority})"
        )
        logger.debug(f"  Confidence: {action.confidence:.2f}")