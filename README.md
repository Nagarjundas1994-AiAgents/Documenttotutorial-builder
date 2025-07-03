# 🤖 Document to Tutorial Builder

A comprehensive AI-powered system that automatically crawls documentation websites and generates beginner-friendly tutorials using multiple specialized AI agents.

## ✨ Features

- **Multi-Agent Architecture**: Specialized AI agents for crawling, content extraction, analysis, structuring, and tutorial generation
- **Comprehensive Crawling**: Discovers and processes entire documentation websites
- **Vector Search**: Semantic search capabilities using Qdrant and Ollama embeddings
- **Real-time Progress**: Live updates during the generation process
- **Multiple Export Formats**: Download tutorials in Markdown, HTML, PDF, and EPUB formats
- **Interactive UI**: Modern web interface with agent status monitoring

## 🏗️ Architecture

The system consists of 6 specialized AI agents:

1. **🕷️ Crawler Agent**: Discovers and maps all documentation URLs
2. **📖 Content Agent**: Extracts and cleans content from each page
3. **🔍 Analysis Agent**: Identifies key concepts and relationships
4. **🏗️ Structure Agent**: Organizes content into logical sections
5. **💡 Example Agent**: Generates code examples and use cases
6. **✍️ Tutorial Agent**: Creates beginner-friendly explanations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- Ollama (for embeddings)
- API keys for Google Gemini and OpenAI

### 1. Clone and Setup

```bash
git clone <repository-url>
cd "Documenttotutorial builder"
```

### 2. Configure Environment

Copy the `.env` file and add your API keys:

```bash
# .env
GOOGLE_API_KEY="your-google-gemini-api-key"
OPENAI_API_KEY="your-openai-api-key"
DEEPSEEK_API_KEY="your-deepseek-api-key"  # Optional
XAI_API_KEY="your-xai-api-key"            # Optional
```

### 3. Install Ollama and Model

```bash
# Install Ollama (visit https://ollama.ai for instructions)
ollama serve

# Pull the required embedding model
ollama pull snowflake-arctic-embed2:568m
```

### 4. Run the Application

Use the automated startup script:

```bash
python start_app.py
```

Or manually:

```bash
# Start Qdrant database
docker-compose up -d qdrant

# Install Python dependencies
pip install -r requirements.txt

# Start the application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the Application

Open your browser and navigate to: `http://localhost:8000`

## 📖 Usage

1. **Enter Documentation URL**: Provide the base URL of the documentation website
2. **Configure Crawl Settings**: Choose crawl depth and content types
3. **Start Generation**: Click "Start Comprehensive Analysis"
4. **Monitor Progress**: Watch the AI agents work in real-time
5. **Download Tutorial**: Export the generated tutorial in your preferred format

### Example URLs to Try

- `https://docs.python.org/3/`
- `https://fastapi.tiangolo.com/`
- `https://docs.docker.com/`
- `https://kubernetes.io/docs/`

## 🔧 Configuration

### Crawl Depth Options

- **Level 1**: Main sections only (fastest)
- **Level 2**: All subsections (recommended)
- **Level 3**: Deep crawl (comprehensive)
- **Unlimited**: Complete site (slowest)

### Content Types

- ✅ API References
- ✅ Guides & Tutorials
- ✅ Code Examples
- ✅ FAQs & Troubleshooting

### Tutorial Features

- ✅ Analogies & Metaphors
- ✅ Practice Exercises
- ✅ Concept Maps
- ✅ Section Summaries

## 🛠️ Development

### Project Structure

```
Documenttotutorial builder/
├── agents/
│   └── graph.py          # LangGraph workflow definition
├── utils/
│   ├── crawler.py        # Web crawling functionality
│   └── vector_store.py   # Qdrant vector store management
├── static/
│   └── index.html        # Frontend interface
├── main.py               # FastAPI application
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Qdrant database setup
├── start_app.py         # Automated startup script
└── README.md            # This file
```

### Key Components

#### LangGraph Workflow (`agents/graph.py`)

The tutorial generation process is orchestrated using LangGraph:

1. **Generate Outline**: Creates a structured outline from scraped content
2. **Write Sections**: Iteratively writes each tutorial section
3. **Compile Tutorial**: Assembles the final tutorial document

#### Web Crawler (`utils/crawler.py`)

- Asynchronous crawling with configurable depth
- Content extraction using BeautifulSoup and html2text
- Respects robots.txt and handles redirects
- Filters out non-content files (PDFs, images, etc.)

#### Vector Store (`utils/vector_store.py`)

- Qdrant integration for semantic search
- Ollama embeddings using snowflake-arctic-embed2:568m
- Document chunking and metadata storage
- Async query capabilities

### API Endpoints

- `GET /`: Serves the main application interface
- `WebSocket /ws`: Real-time communication for tutorial generation
- `POST /ask`: Q&A endpoint for querying stored documentation

## 🐛 Troubleshooting

### Common Issues

#### "Docker not found"
- Install Docker Desktop from https://docker.com
- Ensure Docker is running before starting the application

#### "Ollama not running"
- Start Ollama: `ollama serve`
- Pull the model: `ollama pull snowflake-arctic-embed2:568m`

#### "API key errors"
- Verify your API keys in the `.env` file
- Ensure keys have proper permissions and quotas

#### "Qdrant connection failed"
- Check if Docker is running: `docker ps`
- Restart Qdrant: `docker-compose restart qdrant`

#### "Tutorial generation fails"
- Check API key quotas and limits
- Verify the documentation URL is accessible
- Try reducing crawl depth for large sites

### Performance Tips

1. **Start Small**: Begin with Level 1 or 2 crawl depth
2. **Monitor Resources**: Large sites can consume significant memory
3. **API Limits**: Be aware of rate limits on your API keys
4. **Network**: Ensure stable internet connection for crawling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Format code
black .
isort .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangGraph**: For the multi-agent workflow framework
- **Qdrant**: For vector database capabilities
- **Ollama**: For local embedding models
- **FastAPI**: For the web framework
- **BeautifulSoup**: For web scraping capabilities

## 📞 Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Review the console output for error messages
3. Ensure all prerequisites are properly installed
4. Verify your API keys and network connectivity

---

**Happy Tutorial Building! 🎉**