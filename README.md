# fantasyolympics
code for drafting and scorekeeping for fantasy olympics

Data source: https://www.kaggle.com/datasets/piterfm/milano-cortina-2026-olympic-winter-games

# Normal execution sequence

## One Time Setup
The following data can and must be configured once per season.

 `roster.csv` is created by `draft.py` on draft day. `events.csv` is created by starting from some kind of query of all events (I think I asked Gemini for it this time) and then
   1. assigning each event to a discipline, and
   2. assigning `is_team` and `is_prestige` values to each event.
   
`set_base_scores.py` should be run by the user any time `events.csv` is updated, to calculate and update the base score for each event according to the discipline.
 
## During the event
From that point on, `update.yml` runs the following sequence on a cadence according to what I sure hope is standard github benavior.

1. `tbd.script` populates `data/medals.csv`
2. update_log produces dashboard_data, including the medal table, standings, and news feed
    - calculates the full daily log every run, this may be a feature it may be a bug
3. index.html displays dashboard_data

# Testing
- to preview the webpage, run `python -m http.server 8000`, then navigate to http://localhost:8000. Apparently the server knows to uh, serve, `index.html`
- `mock_data/` is provided so that `update_log.py` has something to work on. Just set `DATA_DIR= './mock_data'` instead of `./data`. 

# Future Improvements
- during the draft it would be cool if people could select their countries on their own phone instead of passing around a laptop. Also the phones should auto-refresh when a selection is made.
- need a way to validate the data -- some sort of debug index if events or countries aren't matching
