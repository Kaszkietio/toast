# toast

Traffic Orchestration by Agent System (T)

## Overview
Toast is a simulation framework designed to model and analyze traffic systems using agent-based methodologies. It leverages the Mesa library for agent-based modeling and FastAPI for serving the simulation results and metrics.

## Features
- **Agent-Based Modeling**: Simulate traffic systems with various agents such as crossroad controllers, sources, sinks, and special vehicles.
- **Metrics Analysis**: Evaluate traffic metrics like average waiting time, ambulance policies, and light types under different traffic conditions.
- **Frontend Integration**: A modern frontend built with Vite and React for visualizing simulation results and metrics.

## Repository Structure
- **frontend/**: Contains the frontend application built with React and Vite.
  - `src/`: Source code for the frontend.
  - `public/`: Static assets for the frontend.
- **src/**: Backend and simulation logic.
  - `agents/`: Definitions for various traffic agents.
  - `metrics/`: CSV files containing simulation results for different metrics.
  - `server.py`: FastAPI server for serving simulation results.
  - `model.py`: Core simulation model.
  - `graph.py`: Graph utilities for traffic systems.
  - `plots.ipynb`: Jupyter notebook for visualizing metrics.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/toast.git
   cd toast
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Start the FastAPI server:
   ```bash
   python src/server.py
   ```
2. Navigate to the frontend directory and start the development server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Access the application in your browser at `http://localhost:5173`.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.