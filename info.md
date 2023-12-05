# NBA Game Stats API

## Overview

This Flask application leverages the NBA API to retrieve and display detailed statistics for NBA games. The API provides information about game scores, schedules, team logos, and player statistics.

## Dependencies

- `flask`: Web framework for building the API endpoints.
- `requests`: Library for making HTTP requests to the NBA API.
- `nba_api`: Python wrapper for the NBA API, allowing easy access to NBA data.

## Functionality

1. **Game IDs Retrieval:**
   - `get_game_ids(day_offset=-1)`: Retrieves NBA game IDs for a specified day offset (default is yesterday).
   - `get_tomorrows_game_ids()`: Retrieves NBA game IDs for the next day.

2. **Logo Retrieval:**
   - `getlogo(teamid)`: Constructs the logo path for a given NBA team ID.

3. **Game Data Processing:**
   - `process_game_data(game_id)`: Retrieves detailed statistics for a specific NBA game, including scores, team logos, and player statistics.

4. **Flask Endpoints:**
   - `/`: Returns a JSON object containing detailed statistics for all NBA games played on the current day.
   - `/next_games`: Returns a JSON object with NBA game IDs scheduled for the next day.

## Running the Application

- Ensure that the required dependencies are installed (`flask`, `requests`, `nba_api`).
- Execute the script `nba_game_stats.py` to run the Flask application.
- Access the endpoints locally:
  - `http://127.0.0.1:5000/`: Detailed statistics for all NBA games played on the current day.
  - `http://127.0.0.1:5000/next_games`: NBA game IDs scheduled for the next day.

## Notes

- The application uses the NBA API to fetch real-time data, so an internet connection is required.
- Errors such as timeouts or JSON decoding issues are handled gracefully.

