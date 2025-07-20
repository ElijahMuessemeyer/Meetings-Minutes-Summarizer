# Meeting Minutes Summarizer

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An intelligent AI-powered system that transforms raw meeting transcripts into professional, structured meeting minutes using Claude AI or OpenAI GPT, with automatic fallback to basic text processing.

## What It Does

- **Input**: Raw meeting transcripts (text from spoken conversation)
- **Output**: Professional meeting minutes with summaries, decisions, and action items
- **Process**: Smart text processing → AI summarization (Claude/OpenAI) → Structured reporting

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

## AI Configuration (Optional but Recommended)

The system supports multiple AI providers for high-quality summarization:

### Option 1: Claude AI (Recommended)

1. Get an API key from [console.anthropic.com](https://console.anthropic.com/)
2. Create a `.env` file in the project root:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   CLAUDE_MODEL=claude-3-haiku-20240307
   ```

### Option 2: OpenAI

1. Get an API key from [platform.openai.com](https://platform.openai.com/)
2. Add to `.env` file:
   ```bash
   OPENAI_API_KEY=sk-your-openai-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   ```

### No API Key?

The system will automatically fall back to basic text processing if no AI APIs are configured. You'll still get functional meeting minutes, just with less sophisticated analysis.

## Quick Start

### Basic Usage

```bash
# Run with a transcript file
python -m meeting_minutes_summarizer.main tests/sample_transcripts/sample_meeting.txt

# Save output to file
python -m meeting_minutes_summarizer.main input.txt output.md

# Specify output format
python -m meeting_minutes_summarizer.main input.txt output.html
```

### Python API Usage

```python
from meeting_minutes_summarizer.main import MeetingMinutesProcessor, ProcessingConfig

# Configure the processor (AI will be auto-detected from environment)
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

### AI-Powered Processing
- **Claude AI Integration**: High-quality summarization using Anthropic's Claude
- **OpenAI Integration**: Alternative GPT-based processing
- **Automatic Fallback**: Basic text processing when AI is unavailable
- **Smart API Selection**: Tries Claude first, then OpenAI, then basic processing

### Core Processing
- **Transcript Parsing**: Cleans raw text, identifies speakers, removes noise
- **Smart Chunking**: Breaks long transcripts at natural conversation points
- **AI Summarization**: Uses Claude/OpenAI to extract key points, decisions, and discussion topics
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
├── meeting_minutes_summarizer/
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
- Basic text processing implemented (AI integration pending)
- Template customization system in development

**Note**: Currently uses basic text processing for summarization. AI integration (Claude, OpenAI, etc.) is planned for future releases.

## Future Enhancements

- Audio file processing (speech-to-text integration)
- Real-time processing for live meetings
- Calendar integration for automatic action item scheduling
- Multi-language support
- Advanced analytics and meeting insights

## Testing

```bash
# Run the example with sample data
python -m meeting_minutes_summarizer.main tests/sample_transcripts/sample_meeting.txt

# Test with your own transcript
python -m meeting_minutes_summarizer.main your_transcript.txt output.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.