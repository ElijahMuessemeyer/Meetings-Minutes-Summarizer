"""
Main orchestrator for Meeting Minutes Summarizer

Coordinates all components to process transcripts and generate meeting minutes.
This is the entry point that ties together parsing, chunking, summarization, and reporting.
"""

from typing import Optional, List
import sys
import os
from dataclasses import dataclass

# Import our components
from transcript_parser import TranscriptParser, ParsedTranscript
from chunker import TranscriptChunker, TextChunk
from summarizer import MeetingSummarizer, MeetingSummary
from action_extractor import ActionItemExtractor
from report_generator import MeetingMinutesReportGenerator, ReportConfig


@dataclass
class ProcessingConfig:
    """Configuration for the entire processing pipeline."""
    max_words_per_chunk: int = 800
    overlap_words: int = 50
    output_format: str = "markdown"  # "markdown", "text", "html"
    include_confidence_scores: bool = False
    group_actions_by_owner: bool = True
    min_action_confidence: float = 0.6


class MeetingMinutesProcessor:
    """
    Main processor that orchestrates the entire meeting minutes workflow.
    
    Workflow:
    1. Parse raw transcript
    2. Chunk into manageable pieces
    3. Summarize each chunk
    4. Extract action items
    5. Generate final report
    """
    
    def __init__(self, config: ProcessingConfig = None):
        self.config = config or ProcessingConfig()
        
        # Initialize processing components
        self.parser = TranscriptParser()
        self.chunker = TranscriptChunker(
            max_words_per_chunk=self.config.max_words_per_chunk,
            overlap_words=self.config.overlap_words
        )
        self.summarizer = MeetingSummarizer()
        self.action_extractor = ActionItemExtractor()
        
        # Configure report generation
        report_config = ReportConfig(
            include_confidence_scores=self.config.include_confidence_scores,
            group_action_items_by_owner=self.config.group_actions_by_owner
        )
        self.report_generator = MeetingMinutesReportGenerator(report_config)
    
    def process_transcript(self, raw_transcript: str, meeting_title: str = "Meeting") -> str:
        """
        Process a raw transcript into formatted meeting minutes.
        
        Args:
            raw_transcript: The raw meeting transcript text
            meeting_title: Title for the meeting (optional)
            
        Returns:
            Formatted meeting minutes as string
        """
        print(f"Processing transcript for: {meeting_title}")
        print(f"Input length: {len(raw_transcript)} characters")
        
        # Parse transcript
        print("\n1. Parsing transcript...")
        parsed_transcript = self.parser.parse(raw_transcript)
        print(f"   Found {len(parsed_transcript.speakers)} speakers")
        print(f"   Cleaned text: {parsed_transcript.total_words} words")
        print(f"   Processing estimate: {self.parser.estimate_processing_time(parsed_transcript.total_words)}")
        
        # Chunk transcript
        print("\n2. Chunking transcript...")
        chunks = self.chunker.chunk_transcript(
            parsed_transcript.cleaned_text, 
            parsed_transcript.speakers
        )
        chunking_summary = self.chunker.get_chunking_summary(chunks)
        print(f"   Created {chunking_summary['total_chunks']} chunks")
        print(f"   Average chunk size: {chunking_summary['avg_words_per_chunk']} words")
        
        # Summarize chunks
        print("\n3. Summarizing chunks...")
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"   Processing chunk {i+1}/{len(chunks)}")
            
            context = ""
            if chunk_summaries:
                context = chunk_summaries[-1].summary
            
            chunk_summary = self.summarizer.summarize_chunk(
                chunk.content, 
                chunk.chunk_id, 
                context
            )
            chunk_summaries.append(chunk_summary)
        
        # Extract action items
        print("\n4. Extracting action items...")
        additional_actions = self.action_extractor.extract_action_items(
            parsed_transcript.cleaned_text,
            parsed_transcript.speakers
        )
        
        high_confidence_actions = [
            action for action in additional_actions 
            if action.confidence >= self.config.min_action_confidence
        ]
        print(f"   Found {len(high_confidence_actions)} high-confidence action items")
        
        # Generate final summary
        print("\n5. Generating final summary...")
        meeting_summary = self.summarizer.combine_summaries(chunk_summaries)
        
        combined_actions = self._merge_action_items(
            meeting_summary.action_items,
            high_confidence_actions
        )
        meeting_summary.action_items = combined_actions
        
        # Format report
        print("\n6. Formatting report...")
        final_report = self.report_generator.generate_report(
            meeting_summary, 
            self.config.output_format
        )
        
        print(f"\nProcessing complete! Generated {len(final_report)} character report.")
        return final_report
    
    def process_file(self, file_path: str, output_path: str = None) -> str:
        """
        Process a transcript file and optionally save the output.
        
        Args:
            file_path: Path to transcript file
            output_path: Optional path to save the output
            
        Returns:
            Generated meeting minutes
        """
        # Read transcript file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_transcript = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Transcript file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")
        
        # Extract meeting title from filename
        meeting_title = os.path.splitext(os.path.basename(file_path))[0]
        
        # Process transcript
        result = self.process_transcript(raw_transcript, meeting_title)
        
        # Save output if requested
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"Output saved to: {output_path}")
            except Exception as e:
                print(f"Warning: Could not save to {output_path}: {str(e)}")
        
        return result
    
    def _merge_action_items(self, summarizer_actions: List[dict], 
                          extractor_actions: List) -> List[dict]:
        """
        Merge action items from different sources and remove duplicates.
        
        Args:
            summarizer_actions: Actions from the summarizer
            extractor_actions: Actions from the dedicated extractor
            
        Returns:
            Merged list of unique action items
        """
        merged_actions = list(summarizer_actions)
        
        # Convert extractor actions to standardized format
        for action in extractor_actions:
            action_dict = {
                "task": action.task,
                "owner": action.owner or "TBD",
                "deadline": action.deadline or "TBD",
                "priority": action.priority,
                "confidence": action.confidence
            }
            
            # Check for duplicates using text similarity
            is_duplicate = False
            for existing in merged_actions:
                if self._is_similar_action(action_dict, existing):
                    is_duplicate = True
                    # Keep higher confidence action
                    if (action_dict.get('confidence', 0) > existing.get('confidence', 0)):
                        merged_actions.remove(existing)
                        merged_actions.append(action_dict)
                    break
            
            if not is_duplicate:
                merged_actions.append(action_dict)
        
        return merged_actions
    
    def _is_similar_action(self, action1: dict, action2: dict) -> bool:
        """Check if two actions are similar (simple text matching)."""
        task1_words = set(action1['task'].lower().split())
        task2_words = set(action2['task'].lower().split())
        
        if not task1_words or not task2_words:
            return False
        
        # Calculate Jaccard similarity
        intersection = task1_words.intersection(task2_words)
        union = task1_words.union(task2_words)
        similarity = len(intersection) / len(union) if union else 0
        
        return similarity > 0.7


def main():
    """Command line interface for the meeting minutes processor."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <transcript_file> [output_file]")
        print("Example: python main.py sample_transcript.txt meeting_minutes.md")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Configure processor with default settings
    config = ProcessingConfig(
        output_format="markdown",
        group_actions_by_owner=True,
        min_action_confidence=0.6
    )
    
    processor = MeetingMinutesProcessor(config)
    
    try:
        result = processor.process_file(input_file, output_file)
        
        if not output_file:
            print("\n" + "="*60)
            print("GENERATED MEETING MINUTES")
            print("="*60)
            print(result)
            
    except Exception as e:
        print(f"Error processing transcript: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()