# NCIndex

Scraping and more convenient access to instructor data on Ninja Courses.

## Instructions

Running this requires Python 2.6-2.7, though it hasn't been tested with other
versions, as well as SQLite 3. Use `pip install -r requirements.txt` to install
all required Python packages, `python initdb.py` to initialize the database,
`python runscraper.py` to populate the database, and `python runserver.py` to
start the web application.
