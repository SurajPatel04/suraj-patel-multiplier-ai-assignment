# Suraj Patel Multiplier Ai Assignment

An analytics dashboard application that visualizes business data, including revenue trends, top customers, category breakdowns, and regional KPIs. Built with React (Vite) and FastAPI, featuring a clean, responsive, and industry-standard light theme UI.

## Features

- **Revenue Trend**: An interactive area chart visualizing monthly revenue with a custom date-range filter.
- **Top Customers Table**: A sortable data table highlighting top spenders and churn status, featuring real-time debounced search.
- **Category Breakdown**: A bar chart displaying revenue distribution across product categories using a cohesive blue color grade.
- **Regional KPIs**: Card-based summaries of essential metrics across different geographic regions.
- **Automated Data Cleaning**: Python scripts that pre-process and normalize raw CSV datasets for clean API consumption.

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS v4, Recharts, Axios
- **Backend**: Python 3.12, FastAPI, Uvicorn, Pandas, Numpy, Pytest
- **Infrastructure**: Docker, Docker Compose

---

## Getting Started

### 0. Clone the repository

```bash
git clone https://github.com/SurajPatel04/multiplier-ai-assignment.git
cd multiplier-ai-assignment
```

### 1. Data Preparation (Required)

Before running the backend, generate the cleaned and processed datasets.

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run data pipeline
python clean_data.py
python analyze.py
```

This will generate all required CSV files inside:

```text
data/processed/
```

If the processed files already exist, this step can be skipped.

### 2. Running the Backend (Docker - Recommended)

The backend is fully Dockerized. The CSV data directory is mapped as a bind-mount, so any updates to the CSVs in the `./data` directory will immediately be available to the application.

```bash
# Build and start the backend container
docker compose -p suraj-patel-assignment up --build

# Run without rebuilding
docker compose -p suraj-patel-assignment up

# To stop the container
docker compose -p suraj-patel-assignment down
```
*The API will be available at `http://localhost:8000`*

### 3. Running the Backend (Locally without Docker)

If you prefer to run the FastAPI server natively:

```bash
# Set up a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn backend.main:app --reload
```

### 4. Running the Frontend

The frontend is built with Vite and runs independently and communicates with the backend API.

*Note: Ensure backend is running on port 8000 before starting frontend. Ensure `.env` is configured properly. You can set `VITE_API_URL` if needed (defaults to `http://localhost:8000/api`).*

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
*The dashboard will be available at `http://localhost:5173`*

---

## Project Structure

- `/backend` - FastAPI routes and core API logic.
- `/frontend` - React application built with Tailwind CSS and Recharts.
- `/data` - Contains the raw and cleaned CSV files (bind-mounted in Docker).
- `/tests` - Pytest suite validating the data cleaning and normalization pipeline.
- `clean_data.py` - Script responsible for normalizing and cleaning the raw CSV data.
- `docker-compose.yml` - Docker compose configuration for the backend service.
