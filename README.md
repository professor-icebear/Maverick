# Maverick

A sophisticated poker analysis engine combining Monte Carlo simulation with AI-driven decision making.

## Features

### Core Engine
- ✅ Advanced Monte Carlo simulation with multi-opponent support
- ✅ Accurate equity calculation against realistic opponent ranges
- ✅ Comprehensive hand evaluation and ranking
- ✅ Intelligent outs calculation for drawing hands
- ✅ Position-based decision making
- ✅ Performance optimization with vectorization and caching

### Command Line Interface
- ✅ User-friendly CLI for hand analysis
- ✅ Support for all poker streets (preflop to river)
- ✅ Detailed statistics and win probabilities
- ✅ Drawing hand analysis with outs counting
- ✅ Pot odds and EV calculations
- ✅ Action recommendations with bet sizing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/professor-icebear/Maverick.git
cd Maverick
```

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
```bash
# On Unix/macOS
source venv/bin/activate

# On Windows
.\venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Hand Analysis
```bash
python -m maverick.cli "As Kh" -c "Jh Td Qc"
```

### Full Options
```bash
python -m maverick.cli "As Kh" \
    -c "Jh Td Qc" \
    -n 10000 \
    -o 2 \
    -p 100 \
    -b 20 \
    -s 1000 \
    --position button
```

Options:
- `-c, --community`: Community cards
- `-n, --simulations`: Number of Monte Carlo simulations
- `-o, --opponents`: Number of opponents
- `-p, --pot`: Current pot size
- `-b, --bet`: Current bet to call
- `-s, --stack`: Your stack size
- `--position`: Your position (early/middle/late/button)

## Project Structure

```
maverick/
├── core/
│   ├── cards.py         # Card and deck representations
│   ├── evaluator.py     # Hand evaluation logic
│   ├── simulator.py     # Monte Carlo simulation engine
│   ├── decision.py      # Decision making logic
│   ├── outs.py         # Drawing hand analysis
│   └── poker_utils.py   # High-level interface
├── cli.py              # Command-line interface
└── tests/              # Comprehensive test suite
```

## Roadmap

### Phase 1: Opponent Modeling (In Progress)
- [ ] Implement player profiling system
- [ ] Develop range modeling based on position and action history
- [ ] Add hand history analysis for opponent tendencies
- [ ] Integrate historical data analysis

### Phase 2: Real-Time Integration
- [ ] Design RESTful API for live analysis
- [ ] Implement WebSocket support for real-time updates
- [ ] Create microservices architecture for scalability
- [ ] Add database integration for hand history storage

### Phase 3: Advanced AI Components
- [ ] Implement deep learning models for:
  - Opponent hand range prediction
  - Bluff detection
  - Dynamic bet sizing
  - Multi-street strategy optimization
- [ ] Train models on large-scale poker data
- [ ] Integrate with existing Monte Carlo engine

### Phase 4: User Interface & Deployment
- [ ] Develop web-based dashboard
- [ ] Create mobile application
- [ ] Implement real-time HUD overlay
- [ ] Set up cloud infrastructure
- [ ] Add monitoring and analytics

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License 

## Acknowledgments

- Treys library for card evaluation
- NumPy for vectorized calculations
- The poker community for equity calculations and strategy insights 
