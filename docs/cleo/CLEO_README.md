# CLEO - Cairo Local Expert & Operator

Your AI-powered Egyptian travel guide is ready to help!

## Quick Start

### 1. Interactive CLI (Recommended for Testing)

```bash
python cleo_cli.py
```

**Available Commands:**
- Type your questions about Egypt
- `profile` - View your travel profile
- `debug` - Toggle debug mode (shows reasoning)
- `stats` - View conversation statistics
- `quit` or `exit` - End conversation

### 2. Python Code

```python
from src.cleo.cleo_agent import CleoAgent

# Initialize CLEO
agent = CleoAgent()

# Simple question
response = agent.process_message("Tell me about the Pyramids")
print(response)

# Multi-turn conversation (with user ID)
user_id = "my_user_id"
response1 = agent.process_message("I'm interested in mosques", user_id=user_id)
response2 = agent.process_message("Which should I visit first?", user_id=user_id)
print(response2)  # CLEO remembers you asked about mosques!
```

### 3. REST API (FastAPI)

Start the server:
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Make requests:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the opening hours for the Pyramids?",
    "user_id": "user123",
    "debug": false
  }'
```

## What CLEO Can Do

✅ **Conversational AI**: Multi-turn conversations with context memory
✅ **Egyptian Expert**: Deep knowledge of history, culture, and attractions
✅ **Practical Advice**: Real travel tips (best times, what to bring, etc.)
✅ **Friendly Personality**: Warm, knowledgeable Egyptian travel guide
✅ **Personalized**: Adapts to user interests (when profiles are enabled)

## Current Features

### Working Now:
- ✅ Multi-turn conversations
- ✅ Historical and cultural information
- ✅ Practical travel advice
- ✅ Engaging Egyptian personality
- ✅ Context awareness (remembers previous messages)

### Coming Soon (Teammate's Work):
- ⏳ Route optimization (logical POI ordering)
- ⏳ Distance and cost calculations
- ⏳ Full itinerary planner integration
- ⏳ Tool calls (database queries, weather, web search)

## Configuration

All settings in `.env`:
```
GROQ_API_KEY=your_key_here
LLM_MODEL=llama-3.3-70b-versatile
WEATHER_API_KEY=optional_openweathermap_key
SEARCH_API_KEY=optional_tavily_key
```

## Example Conversations

**Ask about attractions:**
```
You: Tell me about the Pyramids
CLEO: Ah, the Great Pyramids! Let me share their incredible story...
```

**Practical questions:**
```
You: What should I wear visiting mosques?
CLEO: When visiting mosques in Egypt, modest dress is important...
```

**Cultural context:**
```
You: Is tipping customary in Egypt?
CLEO: Yes, tipping (baksheesh) is very much part of Egyptian culture...
```

**Multi-turn:**
```
You: I have 3 days in Cairo
CLEO: Ah, 3 days is great! What interests you most?
You: Islamic architecture
CLEO: Perfect! For Islamic architecture, you must see Sultan Hassan Mosque...
```

## Troubleshooting

**Issue:** "Failed to initialize Redis cache"
- **Solution:** Not critical - CLEO works without cache (just slower)

**Issue:** "Error generating response from Groq"
- **Solution:** Check your GROQ_API_KEY in `.env`

**Issue:** Unicode/emoji errors in CLI
- **Solution:** CLI automatically handles this (emojis removed for Windows console)

**Issue:** Tool call errors
- **Solution:** Tools are temporarily disabled - CLEO works from training knowledge

## Status

- ✅ **CLEO Core**: Fully functional
- ✅ **Groq API**: Connected and working
- ✅ **Conversation Memory**: Working
- ✅ **Personality**: Egyptian travel guide with cultural knowledge
- ⏳ **Tool Calls**: Being refined (coming in next update)

## Next Steps

1. **Test CLEO**: Run `python cleo_cli.py` and chat!
2. **Add POIs**: Enrich your database with more attractions
3. **Build UI**: Create frontend using FastAPI endpoints
4. **Profile System**: Implement user profiling for personalization

**CLEO is ready to help travelers explore Egypt!** 🇪🇬
