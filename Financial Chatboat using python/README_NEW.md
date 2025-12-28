# AGI Chatbot System

A simplified yet powerful AGI (Artificial General Intelligence) chatbot with advanced memory, learning, and training capabilities.

## 🧠 Features

- **Advanced Memory System** - Persistent conversation storage with SQLite
- **Multi-Strategy Response Generation** - Intelligent response strategies based on context
- **Sentiment Analysis** - Built-in sentiment understanding
- **Continuous Learning** - Can learn and remember new information
- **Training Simulation** - Complete training interface for model improvement
- **Knowledge Management** - Add and search through knowledge base
- **Real-time Chat Interface** - Modern React-based UI
- **AGI Analytics** - Performance monitoring and analytics

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📂 Project Structure

```
├── backend/
│   ├── main.py              # AGI backend server
│   ├── requirements.txt     # Python dependencies
│   ├── agi_memory.db       # SQLite memory database
│   ├── .env                # Environment variables
│   └── .env.example        # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── App.js          # Main app component
│   ├── package.json        # Node dependencies
│   └── public/             # Static assets
└── README.md               # This file
```

## 🔧 API Endpoints

- `POST /api/v1/chat` - Chat with AGI
- `POST /api/v1/training/start` - Start training session
- `GET /api/v1/training/status` - Get training status
- `POST /api/v1/knowledge/add` - Add knowledge
- `POST /api/v1/memory/search` - Search memories
- `GET /api/v1/memory/stats` - Memory statistics
- `GET /api/v1/model/info` - Model information
- `GET /api/v1/analytics/overview` - Analytics overview

## 🧪 AGI Capabilities

1. **Question Answering** - Intelligent responses using memory and reasoning
2. **Analysis** - Deep analysis of text and conversations
3. **Learning** - Can be taught new information that persists
4. **Conversation** - Natural, context-aware dialogue
5. **Training** - Background training processes for improvement

## 💭 Usage Examples

### Basic Chat
Navigate to "AGI Chat" and start conversing. The AGI will:
- Remember your conversations
- Provide contextual responses
- Analyze sentiment and strategy
- Learn from interactions

### Training
Use "Advanced Training" to:
- Upload training data
- Configure training parameters
- Monitor training progress
- Manage training sessions

### Knowledge Management
Add knowledge through chat:
- "Remember that Python is a programming language"
- "Learn about machine learning concepts"
- "Store this information for future use"

## 🔧 Environment Variables

Create `.env` file in backend directory:
```
# Optional environment variables
DEBUG=True
DATABASE_URL=sqlite:///agi_memory.db
```

## 📊 Technical Details

- **Backend**: FastAPI with Python 3.11+
- **Frontend**: React 18 with Material-UI
- **Database**: SQLite for memory storage
- **AI Features**: Built-in sentiment analysis, strategy selection, memory retrieval
- **Architecture**: RESTful API with real-time capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the system
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ for Advanced AI Conversations**
