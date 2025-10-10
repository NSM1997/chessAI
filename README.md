# Chess AI Browser Extension

A browser extension that provides real-time chess analysis and move suggestions while playing online chess. The extension captures your current board position and provides AI-powered analysis with explanations.

## Features

- 🎯 **Real-time Analysis**: Captures board position and provides instant move suggestions
- 🧠 **AI-Powered**: Uses Stockfish engine for position evaluation
- 📚 **Educational**: Provides explanations for suggested moves
- 🎮 **Multi-Platform**: Works on Chess.com and other chess platforms
- 🔧 **Customizable**: Adjustable skill level and analysis depth

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Browser       │    │   Backend API   │    │   Stockfish     │
│   Extension     │◄──►│   (FastAPI)     │◄──►│   Engine        │
│                 │    │                 │    │                 │
│ • DOM Capture   │    │ • Position      │    │ • Move          │
│ • UI Overlay    │    │   Analysis      │    │   Generation    │
│ • User Interface│    │ • Explanations  │    │ • Evaluation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- Chrome/Edge browser
- Stockfish chess engine

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd explainable-chess-ai
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Download Stockfish**
   - Download from [Stockfish website](https://stockfishchess.org/download/)
   - Place the executable in the `stockfish/` directory
   - Update the path in `backend/app/core/config.py` if needed

4. **Start the backend server**
   ```bash
   cd backend
   python -m app.main
   ```
   The API will be available at `http://localhost:8000`

5. **Load the browser extension**
   - Open Chrome/Edge
   - Go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `frontend/` directory

6. **Test the extension**
   - Visit [Chess.com](https://chess.com)
   - Start a game or puzzle
   - The extension should show an overlay with analysis

## Usage

### Browser Extension

1. **Activation**: The extension automatically activates on supported chess websites
2. **Analysis**: Click "Quick Analysis" to get move suggestions
3. **Explanations**: View detailed explanations for each suggested move
4. **Settings**: Adjust skill level and analysis preferences

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /analyze-position` - Analyze chess position
- `POST /explain-move` - Explain a specific move

### Example API Usage

```python
import requests

# Analyze a position
response = requests.post("http://localhost:8000/analyze-position", json={
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 15,
    "user_skill_level": "intermediate",
    "explanation_type": "comprehensive"
})

analysis = response.json()
print(f"Best move: {analysis['best_moves'][0]['san']}")
print(f"Explanation: {analysis['explanations'][0]['explanation']}")
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# API Configuration
API_HOST=localhost
API_PORT=8000
DEBUG=True

# Chess Engine
STOCKFISH_PATH=/path/to/stockfish
STOCKFISH_DEPTH=15
STOCKFISH_THREADS=2

# ML Configuration
ENABLE_ML_ANALYSIS=True
MODEL_PATH=backend/models/saved_models
```

### Extension Settings

The extension can be configured through the popup interface:
- **Skill Level**: Beginner, Intermediate, Advanced
- **Analysis Depth**: 1-25 (higher = more accurate but slower)
- **Explanation Type**: Basic, Comprehensive, Tactical, Strategic

## Development

### Project Structure

```
explainable-chess-ai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── data/               # Training data
│   ├── models/             # ML models
│   └── requirements.txt    # Python dependencies
├── frontend/               # Browser extension
│   ├── content-scripts/    # Content scripts
│   ├── background/         # Background script
│   ├── popup/              # Extension popup
│   └── manifest.json       # Extension manifest
├── scripts/                # Utility scripts
├── tests/                  # Test files
└── stockfish/              # Chess engine
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/test_backend.py

# Frontend tests
pytest tests/test_frontend.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Troubleshooting

### Common Issues

1. **Extension not loading**
   - Check that the backend server is running
   - Verify the API URL in the extension code
   - Check browser console for errors

2. **Stockfish not found**
   - Ensure Stockfish executable is in the correct location
   - Update the path in `config.py`
   - Check file permissions

3. **Analysis not working**
   - Verify the FEN string is valid
   - Check that the position has legal moves
   - Review server logs for errors

### Debug Mode

Enable debug logging by setting `DEBUG=True` in your environment variables.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Stockfish](https://stockfishchess.org/) - Chess engine
- [python-chess](https://github.com/niklasf/python-chess) - Chess library
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Chess.com](https://chess.com) - Chess platform integration
