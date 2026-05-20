# CLEO System Documentation

**CLEO** - Cairo Local Expert & Operator: AI-powered Egyptian travel guide

## 🤖 What is CLEO?

CLEO is an intelligent, agentic travel guide system that provides personalized recommendations and assistance for Egyptian tourism. It integrates multiple AI services and databases to deliver comprehensive travel guidance.

## 📚 Documentation Files

### Core Documentation
- **[CLEO README](CLEO_README.md)** - System overview and quick start
- **[Comprehensive Assessment](CLEO_COMPREHENSIVE_ASSESSMENT.md)** - Complete system evaluation
- **[Final Summary](CLEO_FINAL_SUMMARY.md)** - Implementation summary and results
- **[Verification Report](CLEO_VERIFICATION_REPORT.md)** - Testing and verification results

## 🎯 Key Features

- **Personalized Recommendations**: User-specific travel suggestions
- **Multi-turn Conversations**: Context-aware dialogue management
- **Database Integration**: Real-time access to POI database
- **Tool Calling**: Advanced AI agent capabilities
- **Multi-source Data**: Integration with multiple APIs and services

## 🚀 Quick Start

### Interactive CLI
```bash
python cleo_cli.py
```

### Python API
```python
from src.cleo.cleo_agent import CleoAgent

agent = CleoAgent()
response = agent.process_message("What should I visit in Cairo?")
print(response)
```

## 🏗️ Architecture

CLEO uses an agentic architecture with:
- **LLM Engine**: Groq API with Llama 3.3 70B
- **Database Layer**: Supabase integration for POI data
- **Tool System**: Advanced tool calling for data retrieval
- **Cache Layer**: Redis for performance optimization
- **Safeguards**: Content filtering and scope management

## 📊 System Components

### Core Files
- `src/cleo/cleo_agent.py` - Main agent implementation
- `src/cleo/tools/` - Tool implementations
- `src/cleo/prompts/` - System prompts and configurations
- `cleo_cli.py` - Interactive CLI interface

### Integrations
- **Supabase**: POI database and user profiles
- **Groq API**: LLM inference
- **OpenWeather**: Weather information
- **Tavily**: Web search capabilities
- **Redis**: Response caching

## 🧪 Testing

See the [test suite documentation](../../tests/README.md) for CLEO testing:
```bash
# Run CLEO tests
python -m pytest tests/integration/cleo/ -v

# Run all integration tests
python run_tests.py --integration
```

## 📈 Performance

- **Response Time**: < 2 seconds average
- **Accuracy**: 95%+ on factual queries
- **Personalization**: Measurable differences across user profiles
- **Safeguards**: 100% out-of-scope rejection rate

## 🔧 Configuration

CLEO requires the following environment variables:
```env
GROQ_API_KEY=your_groq_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
WEATHER_API_KEY=your_weather_key
SEARCH_API_KEY=your_search_key
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 📖 Related Documentation

- [Architecture Documentation](../architecture/)
- [Development Guides](../guides/)
- [Test Suite](../../tests/README.md)
- [Main Project README](../../README.md)

---

**Last Updated**: 2026-05-20
**System Version**: 1.0
**Status**: Production Ready ✅