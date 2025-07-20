# AI Integration Guide

This document explains how to configure and use AI APIs with the Meeting Minutes Summarizer.

## Supported AI Providers

The summarizer supports multiple AI providers with automatic fallback:

1. **Anthropic Claude** (recommended)
2. **OpenAI GPT**
3. **Basic text processing** (fallback when no AI is available)

## Configuration

### Environment Variables

The simplest way to configure AI APIs is through environment variables:

**For Claude (Anthropic):**
```bash
export ANTHROPIC_API_KEY="your_claude_api_key_here"
# or
export CLAUDE_API_KEY="your_claude_api_key_here"
```

**For OpenAI:**
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### Configuration File (.env)

Create a `.env` file in your project root:

```env
# Claude API configuration
ANTHROPIC_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-haiku-20240307

# OpenAI API configuration  
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### Programmatic Configuration

```python
from meeting_minutes_summarizer import MeetingSummarizer

# Configure AI settings
ai_config = {
    'anthropic_api_key': 'your_claude_key',
    'claude_model': 'claude-4-sonnet-20250514',
    'openai_api_key': 'your_openai_key', 
    'openai_model': 'gpt-4o'
}

summarizer = MeetingSummarizer(ai_config=ai_config)
```

## Getting API Keys

### Anthropic Claude

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account or sign in
3. Navigate to "API Keys"
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

### OpenAI

1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account or sign in
3. Navigate to "API Keys"
4. Create a new secret key
5. Copy the key (starts with `sk-`)

## Model Selection

### Claude Models (Recommended)

- `claude-3-haiku-20240307` - Fast, cost-effective 
- `claude-4-sonnet-20250514'` - Balanced performance and quality (default)
- `claude-4-opus-20250514` - Highest quality, most expensive

### OpenAI Models

- `gpt-4o` - Fast, cost-effective (default)
- `o3-20250416` - Latest model with improved performance and reasoning

## Usage Examples

### Basic Usage (Auto-detection)

```python
from meeting_minutes_summarizer import MeetingMinutesProcessor

# Will automatically use available AI APIs
processor = MeetingMinutesProcessor()
result = processor.process_transcript(transcript_text)
```

### With Specific Configuration

```python
from meeting_minutes_summarizer import MeetingMinutesProcessor, ProcessingConfig

# Configure to prefer Claude
config = ProcessingConfig()
processor = MeetingMinutesProcessor(config)

# AI configuration will be read from environment variables
result = processor.process_transcript(transcript_text)
```

### Testing AI Integration

```python
import os
from meeting_minutes_summarizer.summarizer import MeetingSummarizer

# Set your API key
os.environ['ANTHROPIC_API_KEY'] = 'your_key_here'

# Test the integration
summarizer = MeetingSummarizer()
test_transcript = '''
John: Let's discuss the Q4 budget. I think we need to increase marketing spend.
Sarah: I agree. I'll prepare a proposal by Friday.
Mike: What about engineering resources?
'''

result = summarizer.summarize_chunk(test_transcript, 1)
print(f"Summary: {result.summary}")
print(f"Action items: {result.action_items}")
```

## Fallback Behavior

The system will try AI providers in this order:

1. **Claude** (if `ANTHROPIC_API_KEY` or `CLAUDE_API_KEY` is set)
2. **OpenAI** (if `OPENAI_API_KEY` is set)
3. **Basic processing** (always available as fallback)

If an AI API fails, it will automatically fall back to the next option.

## Error Handling

The system handles common API errors gracefully:

- **Rate limiting**: Automatic retry with exponential backoff
- **Authentication errors**: Falls back to next provider
- **Network errors**: Retries and falls back
- **Invalid responses**: Falls back to basic processing

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** or secure key management
3. **Rotate keys regularly**
4. **Monitor API usage** for unexpected charges
5. **Use least-privilege keys** when possible

## Troubleshooting

### Common Issues

**"No AI API configured"**
- Check that environment variables are set correctly
- Verify API keys are valid and not expired

**"Claude API failed"**
- Check your Anthropic account has available credits
- Verify the model name is correct
- Check for rate limiting

**"OpenAI API failed"**
- Check your OpenAI account has available credits
- Verify the model name is correct
- Check for rate limiting

### Debug Mode

Enable debug logging to see detailed API interactions:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your code to see detailed logs
```

### Testing Without AI

To test the system without AI APIs:

```python
# Don't set any API keys
summarizer = MeetingSummarizer()
# Will use basic text processing
```

## Performance Tips

1. **Use Haiku for large volumes** - Much faster and cheaper
2. **Batch process chunks** - More efficient than one-by-one
3. **Monitor token usage** - Set up billing alerts
4. **Cache results** - Avoid reprocessing the same content
5. **Use appropriate models** - Don't use Opus for simple tasks

## Integration Examples

### With Environment Variables

```bash
# In your .bashrc or .zshrc
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export CLAUDE_MODEL="claude-3-haiku-20240307"

# Run the summarizer
meeting-minutes-summarizer transcript.txt output.md
```

### With Docker

```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Set environment variables
ENV ANTHROPIC_API_KEY="your-key-here"

CMD ["python", "-m", "meeting_minutes_summarizer.main"]
```

### With GitHub Actions

```yaml
name: Process Meeting Minutes
on: [push]
jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Process transcript
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python -m meeting_minutes_summarizer.main transcript.txt
```

## Support

For AI integration issues:
- Anthropic: [support.anthropic.com](https://support.anthropic.com)
- OpenAI: [help.openai.com](https://help.openai.com)
- This project: Check GitHub issues or create a new one