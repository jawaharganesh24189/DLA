# 🏛️ Indian Legal AI Advisor

An AI-powered legal assistant for Indian law, providing legal information, case law search, and preliminary legal guidance.

## Overview

This project implements a **basic AI-powered legal assistant** designed to help Indians understand their legal rights and navigate the Indian legal system. The system focuses on providing legal information and preliminary guidance without complex document analysis.

### 🎯 Problem Statement

India faces a severe **access to justice crisis**:
- **1.3 billion people** with only ~1.7 million lawyers
- **35 million pending cases** across Indian courts
- **5-15 years** average case pendency in lower courts
- **High costs** making legal consultation prohibitive for many
- **Language barriers** with 22+ official languages

### ✨ Features (Phase 1 - Basic Query System)

- 📋 **Legal Query Answering**: Natural language queries about Indian law
- ⚖️ **Case Law Search**: Semantic search across Indian Supreme Court and High Court cases
- 📚 **Statute Lookup**: Find applicable laws (IPC, CPA, TOPA, CrPC, etc.)
- 💬 **Interactive Interface**: User-friendly UI with ipywidgets
- 🛡️ **Ethical Safeguards**: Comprehensive disclaimers and warnings
- 📖 **Sample Use Cases**: Real-world scenarios (consumer disputes, property issues, employment)

### 🚀 Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jawaharganesh24189/DLA.git
   cd DLA
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the notebook**:
   ```bash
   jupyter notebook 8F_Indian_Legal_AI_Advisor.ipynb
   ```

4. **Execute all cells** and use the interactive interface to ask legal questions

### 📊 Dataset

The system includes synthetic datasets for demonstration:
- **16 Indian Statutes**: IPC, Consumer Protection Act, Transfer of Property Act, etc.
- **10 Landmark Cases**: Supreme Court and High Court precedents
- **13 Q&A Pairs**: Common legal queries with detailed answers

### 🔧 Technology Stack

- **NLP**: sentence-transformers (semantic search)
- **Vector Search**: FAISS (efficient similarity search)
- **UI**: ipywidgets for Jupyter notebooks
- **Data Processing**: NumPy, Pandas
- **Python**: 3.9+

### 📝 Sample Queries

Try asking:
- "Can I file a complaint if a product I bought online is defective?"
- "My employer terminated me without notice. What are my rights?"
- "My neighbor built a wall blocking sunlight. Is this legal?"
- "What is IPC Section 420?"
- "Builder delayed giving me possession. Can I claim compensation?"

### ⚠️ Important Disclaimer

**This system provides information, NOT legal advice.**

- For educational purposes only
- Does not create attorney-client relationship
- Always consult a qualified lawyer for actual legal matters
- Laws are complex and fact-specific
- Do not make legal decisions based solely on AI output

### 🛣️ Future Roadmap

**Phase 2**: Enhanced features
- Hindi language support
- Larger case law database (1000+ cases)
- PDF document analysis
- Integration with live legal databases

**Phase 3**: Advanced AI
- GPT-4 integration
- Multi-hop reasoning
- Citation network visualization
- Predictive analytics

**Phase 4**: Production deployment
- REST API
- Mobile app
- Regional language support (10+ languages)
- Voice interface

### 📚 Resources

- **Indian Kanoon**: https://indiankanoon.org/
- **IndiaCode**: https://www.indiacode.nic.in/
- **Supreme Court**: https://main.sci.gov.in/
- **Free Legal Aid**: https://nalsa.gov.in/

### 🤝 Contributing

Contributions are welcome! This is an educational project aimed at improving access to justice.

### 📄 License

MIT License - Educational purposes only

### 🙏 Acknowledgments

- Indian Legal System for legal framework
- HuggingFace for transformers
- Facebook AI for FAISS
- Open source community

---

**Version**: 1.0 - Basic Query System  
**Date**: February 2026  
**Status**: Educational Demo

For actual legal matters, always consult qualified legal professionals.