# Pool & Gym Occupancy Crawler

This project is a Python-based crawler that fetches occupancy data from multiple sources:
1.  **Bazény Lužánky** (Pool): Fetches the number of people from [bazenyluzanky.starez.cz](https://bazenyluzanky.starez.cz/).
2.  **Hangar Brno** (Climbing Gym): Fetches the occupancy status (e.g., "Open!", "Busy!") from [hangarbrno.cz](https://hangarbrno.cz/en/home/).

Data is logged to separate CSV files in the `data/` directory.

## Prerequisites

- Python 3.x
- Google Chrome installed (for Selenium)

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    ```

3.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the crawler manually, use the `src/main.py` script. You can specify which source to crawl.

### Run for all sources (default)
```bash
python src/main.py --source all
```

### Run for a specific source
```bash
# Only Luzanky Pool
python src/main.py --source luzanky

# Only Hangar Brno
python src/main.py --source hangar
```

### Output
- **Luzanky**: Data is appended to `data/luzanky.csv` (Timestamp, Occupancy Number).
- **Hangar**: Data is appended to `data/hangar.csv` (Timestamp, Occupancy Status).

## Visualization and Analysis

You can visualize the collected crowd data for **Hangar Brno** using the included script.

```bash
python3 visualize_hangar_crowd.py --file data/hangar.csv
```

This will:
1.  Generate **`hangar_plots.png`** containing:
    -   A time-series plot of crowd levels.
    -   Average occupancy by hour of the day.
    -   Average occupancy by day of the week.
2.  Print a summary analysis to the console, including optimal visiting times.


## Scheduling with Cron

You can automate the crawler using `cron` on Linux.

1.  Open the crontab editor:
    ```bash
    crontab -e
    ```

2.  Add a line to schedule the job. Replace `/path/to/project` with the absolute path to your project directory.

    **Run every 1 hour (at minute 0):**
    ```cron
    0 * * * * cd /path/to/project && .venv/bin/python src/main.py --source all >> cron.log 2>&1
    ```

    **Run every 10 minutes:**
    ```cron
    */10 * * * * cd /path/to/project && .venv/bin/python src/main.py --source all >> cron.log 2>&1
    ```

3.  Save and exit.

## Note

This project was vibecoded using **Antigravity**. It was easy to do, and I will definitely keep using LLMs for making small tools like this.
