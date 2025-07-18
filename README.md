# Meeting Minutes Summarizer

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An intelligent AI-powered system that transforms raw meeting transcripts into professional, structured meeting minutes with clear action items and decisions.

## What It Does

- **Input**: Raw meeting transcripts (text from spoken conversation)
- **Output**: Professional meeting minutes with summaries, decisions, and action items
- **Process**: Smart text processing → AI summarization → Structured reporting

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/ElijahMuessemeyer/meeting-minutes-summarizer.git
cd meeting-minutes-summarizer

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install .
```

### Development Installation

```bash
# Clone and install in development mode
git clone https://github.com/ElijahMuessemeyer/meeting-minutes-summarizer.git
cd meeting-minutes-summarizer
pip install -e .

# Install development dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
# Run with a transcript file
python src/main.py tests/sample_transcripts/sample_meeting.txt

# Save output to file
python src/main.py input.txt output.md

# Specify output format
python src/main.py input.txt output.html
```

### Python API Usage

```python
from src.main import MeetingMinutesProcessor, ProcessingConfig

# Configure the processor
config = ProcessingConfig(
    output_format="markdown",
    group_actions_by_owner=True,
    min_action_confidence=0.6
)

processor = MeetingMinutesProcessor(config)

# Process a transcript
with open("transcript.txt", "r") as f:
    transcript = f.read()

meeting_minutes = processor.process_transcript(transcript, "Weekly Team Meeting")
print(meeting_minutes)
```

## Features

### Core Processing
- **Transcript Parsing**: Cleans raw text, identifies speakers, removes noise
- **Smart Chunking**: Breaks long transcripts at natural conversation points
- **AI Summarization**: Extracts key points, decisions, and discussion topics
- **Action Item Detection**: Finds tasks, owners, deadlines, and priorities

### Output Formats
- **Markdown**: GitHub-compatible format with clean structure
- **Plain Text**: Simple format for email distribution
- **HTML**: Web-ready format for sharing and archiving

### Intelligence Features
- **Speaker Recognition**: Identifies who said what
- **Context Preservation**: Maintains conversation flow across chunks
- **Priority Detection**: Classifies action items by urgency
- **Duplicate Removal**: Prevents redundant items in final output

## Example

**Input (Raw Transcript):**
```
John Smith: Can you please send the quarterly report by Friday?
Sarah Johnson: Absolutely, I'll prepare the report and send it by end of day Friday.
Mike Davis: We also need to schedule a follow-up meeting next week.
```

**Output (Meeting Minutes):**
```markdown
## Action Items

### Sarah Johnson
- Prepare and send quarterly report by Friday

### Mike Davis  
- Schedule follow-up meeting for next week
```

## Project Structure

```
meeting-minutes-summarizer/
├── src/
│   ├── main.py              # Main orchestrator
│   ├── transcript_parser.py # Input processing
│   ├── chunker.py          # Text segmentation
│   ├── summarizer.py       # AI summarization
│   ├── action_extractor.py # Action item detection
│   └── report_generator.py # Output formatting
├── tests/
│   └── sample_transcripts/ # Test data
├── templates/              # Output templates
└── examples/              # Sample outputs
```

## Configuration

Customize processing through `ProcessingConfig`:

```python
config = ProcessingConfig(
    max_words_per_chunk=800,        # Chunk size for processing
    output_format="markdown",       # Output format
    group_actions_by_owner=True,    # Group action items by person
    min_action_confidence=0.6       # Confidence threshold for actions
)
```

## Business Value

- **Time Savings**: Reduces manual minute-taking from hours to minutes
- **Consistency**: Standardized format and quality across all meetings
- **Accuracy**: No missed action items or forgotten decisions
- **Accessibility**: Professional format accessible to all stakeholders

## Technical Implementation

1. **Transcript Parser** extracts speakers and cleans text
2. **Chunker** segments long conversations intelligently
3. **Summarizer** processes chunks with AI for key information
4. **Action Extractor** uses pattern matching for precise task detection
5. **Report Generator** formats everything into professional documents

## Development Status

- Core MVP complete with all components
- End-to-end processing pipeline functional
- Multiple output formats supported
- Ready for Claude API integration for production use
- Template customization system in development

## Future Enhancements

- Audio file processing (speech-to-text integration)
- Real-time processing for live meetings
- Calendar integration for automatic action item scheduling
- Multi-language support
- Advanced analytics and meeting insights

## Testing

```bash
# Run the example with sample data
python src/main.py tests/sample_transcripts/sample_meeting.txt

# Test with your own transcript
python src/main.py your_transcript.txt output.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.