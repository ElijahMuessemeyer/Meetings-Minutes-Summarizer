"""
Transcript Parser for Meeting Minutes Summarizer

This module handles the initial processing of meeting transcripts.
It cleans up the raw text and prepares it for further processing.
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedTranscript:
    """
    A container for processed transcript data with extracted metadata.
    """
    raw_text: str
    cleaned_text: str
    speakers: List[str]
    timestamp_markers: List[str]
    total_words: int


class TranscriptParser:
    """
    Processes raw meeting transcripts into a clean, standardized format.
    
    Removes unnecessary formatting, identifies speakers, and prepares text for summarization.
    """
    
    def __init__(self):
        # Speaker identification patterns
        self.speaker_patterns = [
            r'^([A-Z][a-z]+ [A-Z][a-z]+):\s*',  # "John Smith: "
            r'^([A-Z][a-z]+):\s*',              # "John: "
            r'^\[([^\]]+)\]:\s*',               # "[John Smith]: "
            r'^(\w+)\s*-\s*',                   # "John - "
        ]
        
        # Text cleanup patterns
        self.timestamp_pattern = r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?\b'
        self.noise_patterns = [
            r'\[inaudible\]',
            r'\[crosstalk\]', 
            r'\[background noise\]',
            r'\(laughter\)',
            r'\(coughing\)',
            r'um+\b',
            r'uh+\b',
            r'\blike\b(?=\s+\blike\b)',
        ]
    
    def parse(self, raw_transcript: str) -> ParsedTranscript:
        """
        Main function to process a transcript.
        
        Args:
            raw_transcript: The messy meeting transcript text
            
        Returns:
            ParsedTranscript: Clean, structured transcript data
        """
        if not raw_transcript or not raw_transcript.strip():
            raise ValueError("Transcript cannot be empty")
        
        # Clean and extract data
        cleaned_text = self._clean_text(raw_transcript)
        speakers = self._extract_speakers(raw_transcript)
        timestamps = self._extract_timestamps(raw_transcript)
        word_count = len(cleaned_text.split())
        
        return ParsedTranscript(
            raw_text=raw_transcript,
            cleaned_text=cleaned_text,
            speakers=speakers,
            timestamp_markers=timestamps,
            total_words=word_count
        )
    
    def _clean_text(self, text: str) -> str:
        """
        Remove noise and normalize the transcript text.
        """
        cleaned = text
        
        # Remove noise patterns
        for pattern in self.noise_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
        
        # Clean line formatting
        lines = [line.strip() for line in cleaned.split('\n')]
        cleaned = '\n'.join(line for line in lines if line)
        
        return cleaned.strip()
    
    def _extract_speakers(self, text: str) -> List[str]:
        """
        Find all unique speakers mentioned in the transcript.
        """
        speakers = set()
        
        for pattern in self.speaker_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            speakers.update(matches)
        
        return sorted(list(speakers))
    
    def _extract_timestamps(self, text: str) -> List[str]:
        """
        Find timestamp markers in the transcript.
        """
        timestamps = re.findall(self.timestamp_pattern, text)
        return list(set(timestamps))  # Remove duplicates
    
    def estimate_processing_time(self, word_count: int) -> str:
        """
        Estimate how long it will take to process this transcript.
        """
        # Rough estimate: 1000 words per minute of processing
        minutes = max(1, word_count // 1000)
        
        if minutes == 1:
            return "Less than 1 minute"
        elif minutes < 5:
            return f"About {minutes} minutes"
        else:
            return f"About {minutes} minutes"


def validate_transcript_format(text: str) -> Dict[str, bool]:
    """
    Check if the transcript has expected features for optimal processing.
    """
    checks = {
        'has_speakers': bool(re.search(r'^[A-Z][a-z]+:', text, re.MULTILINE)),
        'has_timestamps': bool(re.search(r'\d{1,2}:\d{2}', text)),
        'reasonable_length': 100 < len(text.split()) < 50000,
        'has_dialogue': '"' in text or "'" in text,
    }
    
    return checks


# Example usage
if __name__ == "__main__":
    sample_transcript = """
    John Smith: Good morning everyone, thanks for joining the call.
    [10:00 AM] Sarah Johnson: Thanks John. Should we start with the quarterly review?
    Mike Davis: Yes, I have the numbers ready. Um, let me pull up the spreadsheet.
    [inaudible] 
    John Smith: Great, Mike. Also, Sarah, can you follow up on the client feedback we discussed last week?
    Sarah Johnson: Absolutely. I'll send that report by Friday.
    """
    
    parser = TranscriptParser()
    result = parser.parse(sample_transcript)
    
    logger.info(f"Speakers found: {result.speakers}")
    logger.info(f"Word count: {result.total_words}")
    logger.info(f"Processing estimate: {parser.estimate_processing_time(result.total_words)}")