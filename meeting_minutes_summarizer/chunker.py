"""
Text Chunking for Meeting Minutes Summarizer

Breaks long transcripts into manageable pieces for processing.
Smart chunking preserves context and speaker continuity.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Container for a piece of transcript with metadata."""
    content: str
    chunk_id: int
    speakers_in_chunk: List[str]
    word_count: int
    start_position: int
    end_position: int


class TranscriptChunker:
    """
    Intelligently splits transcripts into processable chunks.
    
    Strategy:
    1. Try to split at natural conversation breaks
    2. Keep speaker turns together when possible
    3. Maintain reasonable chunk sizes for AI processing
    4. Preserve context with slight overlaps between chunks
    """
    
    def __init__(self, max_words_per_chunk: int = 800, overlap_words: int = 50):
        """
        Initialize chunker with size limits.
        
        Args:
            max_words_per_chunk: Target maximum words per chunk
            overlap_words: Words to overlap between chunks for context
        """
        self.max_words_per_chunk = max_words_per_chunk
        self.overlap_words = overlap_words
        
        # Natural break point patterns
        self.break_patterns = [
            r'\n\n+',
            r'\n(?=[A-Z][a-z]+:)',
            r'\n(?=\[[^\]]+\]:)',
            r'\.[\s\n]+(?=[A-Z])',
        ]
    
    def chunk_transcript(self, text: str, speakers: List[str] = None) -> List[TextChunk]:
        """
        Split transcript into optimally-sized chunks.
        
        Args:
            text: Cleaned transcript text
            speakers: List of known speakers (optional)
            
        Returns:
            List of TextChunk objects
        """
        if not text.strip():
            return []
        
        words = text.split()
        if len(words) <= self.max_words_per_chunk:
            return [self._create_chunk(text, 0, speakers or [])]
        
        chunks = []
        current_position = 0
        chunk_id = 0
        
        while current_position < len(words):
            chunk_end = min(current_position + self.max_words_per_chunk, len(words))
            
            # Find optimal break point
            if chunk_end < len(words):
                chunk_end = self._find_break_point(words, current_position, chunk_end)
            
            # Extract chunk text
            chunk_words = words[current_position:chunk_end]
            chunk_text = ' '.join(chunk_words)
            
            # Find speakers in chunk
            chunk_speakers = self._extract_speakers_from_chunk(chunk_text, speakers or [])
            
            # Create chunk object
            chunk = TextChunk(
                content=chunk_text,
                chunk_id=chunk_id,
                speakers_in_chunk=chunk_speakers,
                word_count=len(chunk_words),
                start_position=current_position,
                end_position=chunk_end
            )
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            overlap_start = max(0, chunk_end - self.overlap_words)
            current_position = overlap_start if chunk_end < len(words) else len(words)
            chunk_id += 1
        
        return chunks
    
    def _find_break_point(self, words: List[str], start: int, target_end: int) -> int:
        """
        Find the best place to split within the target range.
        
        Looks for natural conversation breaks near the target end position.
        """
        # Reconstruct text around target break point
        search_start = max(start, target_end - 100)
        search_text = ' '.join(words[search_start:target_end + 50])
        
        # Try each break pattern in order of preference
        for pattern in self.break_patterns:
            matches = list(re.finditer(pattern, search_text))
            if matches:
                # Find match closest to target
                target_char_pos = len(' '.join(words[search_start:target_end]))
                best_match = min(matches, key=lambda m: abs(m.start() - target_char_pos))
                
                # Convert character position back to word position
                break_text = search_text[:best_match.start()]
                break_words = break_text.split()
                return search_start + len(break_words)
        
        # No good break found - split at target
        return target_end
    
    def _extract_speakers_from_chunk(self, chunk_text: str, known_speakers: List[str]) -> List[str]:
        """Find which speakers appear in this chunk."""
        chunk_speakers = []
        
        # Look for speaker patterns
        speaker_patterns = [
            r'^([A-Z][a-z]+ [A-Z][a-z]+):\s*',
            r'^([A-Z][a-z]+):\s*',
            r'^\[([^\]]+)\]:\s*',
        ]
        
        for pattern in speaker_patterns:
            matches = re.findall(pattern, chunk_text, re.MULTILINE)
            chunk_speakers.extend(matches)
        
        # Check for known speakers mentioned in text
        for speaker in known_speakers:
            if speaker in chunk_text:
                chunk_speakers.append(speaker)
        
        return list(set(chunk_speakers))
    
    def _create_chunk(self, text: str, chunk_id: int, speakers: List[str]) -> TextChunk:
        """Create a TextChunk object from text."""
        return TextChunk(
            content=text,
            chunk_id=chunk_id,
            speakers_in_chunk=speakers,
            word_count=len(text.split()),
            start_position=0,
            end_position=len(text.split())
        )
    
    def get_chunking_summary(self, chunks: List[TextChunk]) -> Dict:
        """Generate summary statistics about the chunking process."""
        if not chunks:
            return {"total_chunks": 0, "total_words": 0}
        
        total_words = sum(chunk.word_count for chunk in chunks)
        avg_words_per_chunk = total_words / len(chunks)
        all_speakers = set()
        for chunk in chunks:
            all_speakers.update(chunk.speakers_in_chunk)
        
        return {
            "total_chunks": len(chunks),
            "total_words": total_words,
            "avg_words_per_chunk": round(avg_words_per_chunk),
            "unique_speakers": len(all_speakers),
            "speakers_found": sorted(list(all_speakers))
        }


# Example usage
if __name__ == "__main__":
    sample_text = """
    John Smith: Good morning everyone. Let's start with the quarterly review.
    
    Sarah Johnson: Thanks John. I have the Q3 numbers ready. Revenue is up 15% compared to last quarter.
    
    Mike Davis: That's great news Sarah. What about the customer acquisition costs?
    
    Sarah Johnson: CAC is down 8%. Our new marketing strategy is working well.
    
    John Smith: Excellent. Mike, can you update us on the product development timeline?
    
    Mike Davis: Sure. The new feature set will be ready for beta testing next month. 
    We need to coordinate with the QA team.
    
    Lisa Chen: I can handle the QA coordination. We should also plan user acceptance testing.
    
    John Smith: Perfect. Sarah, please send the revenue report to the board by Friday.
    """
    
    chunker = TranscriptChunker(max_words_per_chunk=50)
    chunks = chunker.chunk_transcript(sample_text)
    
    logger.info(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        logger.debug(f"Chunk {chunk.chunk_id}: {chunk.word_count} words, speakers: {chunk.speakers_in_chunk}")