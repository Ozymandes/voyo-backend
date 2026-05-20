# System Architecture Documentation

Technical architecture and design documentation for the VOYO backend system.

## 🏗️ Architecture Overview

The VOYO backend consists of two main systems:

### 1. Data Pipeline System
Multi-source data fusion pipeline for Egyptian tourist attractions information.

### 2. CLEO AI System  
Agentic AI travel guide powered by large language models.

## 📚 Documentation Files

### Architecture & Design
- **[Pipeline Architecture](PIPELINE_ARCHITECTURE.md)** - Data pipeline design and flow
- **[LLM Integration Analysis](LLM_INTEGRATION_ANALYSIS.md)** - AI/LLM integration details
- **[Master Attractions Integration](MASTER_ATTRACTIONS_INTEGRATION.md)** - Attractions data architecture

## 🎯 System Components

### Data Pipeline
```
Master Attractions List → Google Places API → Wikipedia Scraper → 
Data Fusion → Quality Check → Supabase Database
```

### CLEO AI System
```
User Query → Intent Analysis → Tool Calling → Data Retrieval → 
LLM Processing → Response Generation → Caching
```

## 🔧 Technical Stack

### Backend Technologies
- **Python 3.10+**: Core programming language
- **FastAPI**: REST API framework
- **Supabase**: Database and backend services
- **Redis**: Caching layer

### AI/ML Services
- **Groq API**: LLM inference (Llama 3.3 70B)
- **OpenAI API**: Fallback LLM service
- **OpenWeather**: Weather data integration
- **Tavily**: Web search integration

### Data Processing
- **BeautifulSoup**: Web scraping
- **Requests**: HTTP client
- **Pandas**: Data manipulation

## 🏛️ Database Architecture

### Tables
- **`pois`**: Points of Interest (26 fields)
- **`regions`**: Egyptian geographical regions
- **`itineraries`**: User trip plans
- **`itinerary_items`**: Itinerary activities
- **`user_profiles`**: User preferences and history

### Relationships
- Regions → POIs (one-to-many)
- Users → Itineraries (one-to-many)
- Itineraries → Items (one-to-many)

## 🔄 Data Flow Architecture

### Pipeline Flow
1. **Source Data**: Master attractions list
2. **API Integration**: Google Places for photos/ratings
3. **Content Enrichment**: Wikipedia for historical context
4. **Data Fusion**: Merge and validate
5. **Storage**: Supabase database
6. **Quality Check**: Validation and verification

### CLEO AI Flow
1. **User Input**: Natural language query
2. **Intent Analysis**: Determine user needs
3. **Tool Selection**: Choose appropriate data sources
4. **Data Retrieval**: Fetch relevant information
5. **AI Processing**: Generate contextual response
6. **Result Caching**: Store for future use

## 🔐 Security Architecture

### API Security
- Environment variable-based configuration
- Service key authentication for Supabase
- API key management for external services

### Data Safety
- Input validation and sanitization
- SQL injection prevention
- Rate limiting implementation

## 🚀 Deployment Architecture

### Development Environment
- Local development with virtual environment
- Mock data for testing
- Development database instance

### Production Environment
- Cloud-hosted services (Supabase)
- Managed Redis instance
- Production API keys

## 📊 Performance Considerations

### Optimization Strategies
- **Caching**: Redis for frequently accessed data
- **Batch Processing**: Pipeline processes in batches
- **Async Operations**: Non-blocking I/O for APIs
- **Connection Pooling**: Database connection reuse

### Monitoring
- API response times
- Database query performance
- Cache hit rates
- Error rates and types

## 🔧 Configuration Management

### Environment Variables
```env
# Database
SUPABASE_URL=project_url
SUPABASE_SERVICE_KEY=service_key

# AI Services
GROQ_API_KEY=groq_key
OPENAI_API_KEY=openai_key

# External APIs
GOOGLE_PLACES_API_KEY=google_key
WEATHER_API_KEY=weather_key
SEARCH_API_KEY=search_key

# Caching
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 📖 Related Documentation

- [CLEO System Documentation](../cleo/)
- [Development Guides](../guides/)
- [Pipeline Documentation](../pipeline/)
- [Main Project README](../../README.md)

---

**Last Updated**: 2026-05-20
**Architecture Version**: 2.0
**Status**: Production Ready ✅