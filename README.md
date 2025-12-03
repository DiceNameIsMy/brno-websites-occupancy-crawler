# Pool Occupancy Crawler

This project is a Python-based crawler that fetches the current number of people in the "Bazény Lužánky" pool from [bazenyluzanky.starez.cz](https://bazenyluzanky.starez.cz/) and logs the data to a CSV file.

## Prerequisites

- Python 3.x
- Google Chrome installed (for Selenium)

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the crawler manually:

```bash
# Ensure the virtual environment is activated or use the full path
venv/bin/python src/crawler.py
```

The data will be appended to `data/occupancy.csv` with a timestamp.

## Scheduling with Cron

You can automate the crawler using `cron` on Linux.

1.  Open the crontab editor:
    ```bash
    crontab -e
    ```

2.  Add a line to schedule the job. Replace `/path/to/project` with the absolute path to your project directory (e.g., `/home/nur/Projects/ims-crawler`).

    **Run every 1 hour (at minute 0):**
    ```cron
    0 * * * * cd /path/to/project && venv/bin/python src/crawler.py >> cron.log 2>&1
    ```

    **Run every 10 minutes:**
    ```cron
    */10 * * * * cd /path/to/project && venv/bin/python src/crawler.py >> cron.log 2>&1
    ```
    *Note: `*/10` means it runs at every 10th minute of the hour (e.g., 14:00, 14:10, 14:20), not 10 minutes from when you save the file.*

3.  Save and exit.

### Explanation of Cron Command
- `cd /path/to/project`: Changes directory to the project root so relative paths work.
- `venv/bin/python`: Uses the Python interpreter from the virtual environment.
- `>> cron.log 2>&1`: Redirects both standard output and error to `cron.log` for debugging.

## Note

This project was vibecoded using **Antigravity**. It was easy to do, and I will definitely keep using LLMs for making small tools like this.
