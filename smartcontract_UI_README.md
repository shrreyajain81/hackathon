# UI Dashboard README

## Overview

The UI Dashboard provides a user-friendly web interface to view and search for patient payout information. It connects to the backend API running on `localhost:8000`.

## Components

### Files

- **payout_ui_server.py** - Flask server that serves the UI and provides endpoints for the frontend
- **templates/index.html** - Main HTML template with three tabs for different views
- **static/style.css** - Responsive styling for the dashboard
- **static/script.js** - JavaScript for interacting with the backend API

## Setup

### 1. Install Dependencies

Make sure Flask is installed (already in requirements.txt):

```bash
pip install flask
```

### 2. Run the UI Server
```bash
python payout_ui_server.py
```
The server will start on `http://localhost:8000`

You should see:

```Code
Starting Payout UI Server...
```

Open your browser and go to: http://localhost:8000
### 3. Open in Browser
Navigate to: http://localhost:8000