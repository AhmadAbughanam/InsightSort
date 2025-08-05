# InsightSort 🧠

**AI-Powered Document Classifier & Organizer (Fully Local)**

InsightSort is an intelligent document management system that automatically classifies, organizes, and extracts insights from your documents using local AI. Keep your data private while enjoying the power of advanced document analysis and organization.

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![AI Powered](https://img.shields.io/badge/AI-Local%20LLM-green.svg)
![Privacy](https://img.shields.io/badge/privacy-100%25%20Local-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🎯 Intelligent Classification
- **Auto-Topic Detection**: Classify documents into categories (Tech, Health, Finance, Education, etc.)
- **Local LLM Processing**: Powered by Mistral-7B model for accurate content understanding
- **Rule-Based Fallback**: Robust classification even when LLM is unavailable
- **Custom Categories**: Easily configure and expand topic classifications

### 📁 Smart Organization
- **Automatic Sorting**: Files organized into `/output/organized/<topic>` folders
- **Batch Processing**: Handle multiple files and entire folders at once
- **Drag & Drop Interface**: Intuitive file upload with modern GUI
- **Folder Structure**: Maintains clean, navigable file organization

### 🔍 Content Analysis
- **Keyword Extraction**: Identify key terms using TF-IDF or LLM analysis
- **Smart Summaries**: Generate concise document summaries automatically
- **Multi-Format Support**: Process PDF, TXT, and DOCX files seamlessly
- **Metadata Extraction**: Capture document properties and creation details

### 🛡️ Privacy & Performance
- **100% Local Processing**: No internet required, no data leaves your machine
- **Offline Operation**: Complete functionality without cloud dependencies
- **Memory Efficient**: Optimized for local hardware with configurable settings
- **Audit Trail**: Complete logging and reporting of all operations

### 📊 Reporting & Tracking
- **CSV Reports**: Detailed processing reports with classifications and insights
- **Local Database**: SQLite storage for processing history and memory
- **Process Logging**: Comprehensive logs for debugging and analysis
- **Performance Metrics**: Track processing times and accuracy

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- 8GB+ RAM (recommended for optimal LLM performance)
- Compatible CPU (AVX support for llama-cpp-python)
- 5GB+ free disk space (for models and processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/InsightSort.git
   cd InsightSort
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the LLM model**
   ```bash
   # Create models directory if it doesn't exist
   mkdir models
   
   # Download Mistral-7B GGUF model (Q4_K_M recommended for balance of speed/quality)
   # Place the model file in: models/mistral-7b-instruct-v0.1.Q2_K.gguf
   ```

4. **Configure the application** (Optional)
   ```bash
   # Edit config.yaml to customize settings
   cp config.yaml.example config.yaml
   ```

5. **Launch InsightSort**
   ```bash
   python app.py
   ```

### First Run Setup
1. The application will create necessary directories (`output/`, `logs/`)
2. Upload your first document or folder using the drag-and-drop interface
3. Watch as documents are automatically classified and organized
4. Check the `output/organized/` folder for sorted documents
5. Review the generated `report.csv` for processing details

## 📖 Usage Guide

### Basic Workflow

1. **Upload Documents**
   - Drag and drop files or folders into the application
   - Supported formats: PDF, TXT, DOCX
   - Batch processing handles multiple files simultaneously

2. **Automatic Processing**
   - Documents are analyzed using local LLM
   - Content is classified into predefined topics
   - Keywords and summaries are extracted

3. **Review Results**
   - Check organized folders for sorted documents
   - Review CSV reports for processing details
   - Use the local database for historical queries

### Advanced Configuration

Edit `config.yaml` to customize behavior:

```yaml
# Classification settings
use_llm_first: true          # Use LLM for classification (fallback to rules if false)
confidence_threshold: 0.7    # Minimum confidence for LLM classification

# Extraction settings
extractor:
  llm_mode: true            # Use LLM for keyword/summary extraction
  max_keywords: 10          # Maximum keywords to extract
  summary_length: 200       # Target summary length in words

# Topic customization
topics:
  - Technology
  - Health & Medicine
  - Finance & Business
  - Education & Research
  - Legal & Compliance
  - Personal & Lifestyle
  # Add your custom topics here

# Performance settings
llm:
  model_path: "models/mistral-7b-instruct-v0.1.Q2_K.gguf"
  n_threads: 4              # CPU threads for processing
  max_tokens: 512           # Maximum tokens for LLM responses
```

## 🏗️ Project Architecture

```
InsightSort/
├── app.py                      # Main GUI application
├── config.yaml                 # Configuration settings
├── requirements.txt            # Python dependencies
├── 
├── core/                       # Core processing modules
│   ├── file_handler.py         # File reading and processing
│   ├── llm_classifier.py       # LLM-based classification
│   ├── rule_based_classifier.py # Fallback classification rules
│   ├── extractor.py            # Keyword and summary extraction
│   ├── memory_store.py         # Local database operations
│   └── utils.py                # Utility functions
├── 
├── models/                     # LLM model files
│   └── mistral-7b-instruct-v0.1.Q2_K.gguf
├── 
├── output/                     # Processing outputs
│   ├── organized/              # Sorted documents by topic
│   │   ├── Technology/
│   │   ├── Health & Medicine/
│   │   └── Finance & Business/
│   ├── report.csv              # Processing report
│   └── insight_memory.db       # Local SQLite database
├── 
└── logs/                       # Application logs
    └── process_log.txt         # Detailed processing logs
```

## 🛠️ Development

### Running in Development Mode
```bash
# Enable debug logging
export INSIGHTSORT_DEBUG=1  # Linux/macOS
set INSIGHTSORT_DEBUG=1     # Windows

python app.py
```

### Testing Individual Components
```bash
# Test file processing
python -m core.file_handler test_document.pdf

# Test LLM classification
python -m core.llm_classifier "sample text content"

# Test rule-based fallback
python -m core.rule_based_classifier "sample text content"
```

### Database Operations
```python
from core.memory_store import MemoryStore

# Initialize database connection
memory = MemoryStore()

# Query processing history
results = memory.get_processing_history(limit=10)
print(results)
```

## 📋 Use Cases

### 🎓 Academic Research
- Organize research papers by field and topic
- Extract key findings and methodologies
- Build searchable knowledge repositories

### 💼 Business Documents
- Sort contracts, reports, and correspondence
- Extract action items and key decisions
- Maintain compliance document libraries

### 📚 Personal Knowledge Management
- Organize downloaded articles and documents
- Build personal learning archives
- Sort documentation and tutorials

### 🏢 Enterprise Document Management
- Classify incoming documents automatically
- Reduce manual sorting time and errors
- Maintain consistent organization standards

## ⚙️ Configuration Options

### Performance Tuning
```yaml
# Optimize for speed (lower quality)
llm:
  model_variant: "Q2_K"       # Smaller quantization
  n_threads: 8                # More CPU threads
  max_tokens: 256             # Shorter responses

# Optimize for quality (slower processing)
llm:
  model_variant: "Q8_0"       # Higher quantization
  n_threads: 4                # Fewer threads for stability
  max_tokens: 1024            # Longer, more detailed responses
```

### Custom Topic Categories
```yaml
topics:
  # Technical domains
  - "Software Development"
  - "Data Science & AI"
  - "Cybersecurity"
  
  # Business areas
  - "Marketing & Sales"
  - "Human Resources"
  - "Project Management"
  
  # Personal categories
  - "Recipes & Cooking"
  - "Travel & Adventure"
  - "Health & Wellness"
```

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Implement your changes** with proper testing
4. **Update documentation** as needed
5. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add unit tests for new features
- Test with various document types and sizes
- Ensure local LLM integration works properly
- Update configuration documentation for new options

## 📋 Roadmap

### Phase 1: Core Enhancements
- [ ] **OCR Support** - Process scanned documents and images
- [ ] **More File Formats** - Support for EPUB, RTF, and Office formats
- [ ] **Batch Configuration** - Different settings for different document types

### Phase 2: Advanced Features
- [ ] **Similarity Detection** - Find and group similar documents
- [ ] **Tag Management** - Custom tagging system beyond categories
- [ ] **Search Interface** - Full-text search across organized documents

### Phase 3: Integration & Scaling
- [ ] **API Interface** - RESTful API for integration with other tools
- [ ] **Watch Folders** - Automatic processing of new files in watched directories
- [ ] **Cloud Sync** - Optional encrypted cloud backup of organization structure

## 🐛 Troubleshooting

### Common Issues

**LLM Model Loading Errors**
```bash
# Verify model file exists and is complete
ls -la models/mistral-7b-instruct-v0.1.Q2_K.gguf

# Check system compatibility
python -c "import llama_cpp; print('llama-cpp-python working')"
```

**Memory Issues**
- Reduce `n_threads` in config.yaml
- Use smaller model quantization (Q2_K instead of Q4_K_M)
- Process documents in smaller batches

**Classification Accuracy**
- Enable `use_llm_first: true` for better accuracy
- Adjust `confidence_threshold` for stricter/looser classification
- Add custom rules in `rule_based_classifier.py`

**GUI Not Responding**
- Check system resources (RAM and CPU usage)
- Reduce concurrent processing in settings
- Enable debug logging to identify bottlenecks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Mistral AI** - For the powerful open-source language model
- **llama.cpp** - For efficient local LLM inference
- **PyMuPDF** - For reliable PDF processing
- **scikit-learn** - For traditional ML fallback methods
- **Tkinter** - For the cross-platform GUI framework

---

**Built with ❤️ by Ahmad Abughanam**

*Bringing AI-powered document organization to your desktop - privately and securely.*

## 📞 Support & Community

- 🐛 [Report Issues](https://github.com/your-username/InsightSort/issues)
- 💬 [Join Discussions](https://github.com/your-username/InsightSort/discussions)
- 📖 [Documentation](https://github.com/your-username/InsightSort/wiki)
- 🔔 [Release Notes](https://github.com/your-username/InsightSort/releases)

### System Requirements Summary
- **Minimum**: Python 3.9+, 4GB RAM, 3GB disk space
- **Recommended**: Python 3.11+, 8GB RAM, 10GB disk space
- **Optimal**: Python 3.11+, 16GB RAM, SSD storage, AVX2 CPU
