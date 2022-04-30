# profileSoftwareInternshipTasks

# PREQUISITES:

You need to install required libraries via:
```
pip3 install -r requirements.txt
```
# USAGE:

To use the script type in console (for example linux terminal or windows cmd/powershell):
```
python3 tasks.py task_name [--name NAME] [--season SEASON] [--output OUTPUT] 
```
where task_name is one of:

  - `grouped-teams` returns all nba teams with the name and abbrevation grouped by division. There are no additional arguments for this task.
  - `players-stats` `--name` argument is required. Returns the tallest and heaviest nba player with their respective height and weight in metric system whose first or last name     equals `--name` argument.
  - `teams-stats` `--season` argument is required, `--output` argument is optional. Returns statistics (wins and loses as respectively home and visitor team) in a given season
  provided by `--season` argument. Optional `--output` argument serves as a way to store the satistics in format provided by `--output`, expected values are:
    - `csv` saves stats in .csv format,
    - `json` saves stats in json format,
    - `sqlite` saves stats to sqlite database,
    - `stdout` prints the stats in console).
  If no `--output` is provided the script uses `--output stdout` by default.

 ###### Filip Zygmuntowicz 2022 internship task for Profile Software
