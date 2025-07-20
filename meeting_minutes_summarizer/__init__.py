"""
Meeting Minutes Summarizer

A Python package for converting meeting transcripts into structured meeting minutes.
"""

__version__ = "1.0.1"
__author__ = "Elijah Muessemeyer"

from .main import MeetingMinutesProcessor, ProcessingConfig
from .transcript_parser import TranscriptParser, ParsedTranscript
from .chunker import TranscriptChunker, TextChunk
from .summarizer import MeetingSummarizer, MeetingSummary, ChunkSummary
from .action_extractor import ActionItemExtractor, ActionItem
from .report_generator import MeetingMinutesReportGenerator, ReportConfig

__all__ = [
    "MeetingMinutesProcessor",
    "ProcessingConfig",
    "TranscriptParser",
    "ParsedTranscript",
    "TranscriptChunker",
    "TextChunk",
    "MeetingSummarizer",
    "MeetingSummary",
    "ChunkSummary",
    "ActionItemExtractor",
    "ActionItem",
    "MeetingMinutesReportGenerator",
    "ReportConfig",
]