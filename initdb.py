# Run this to initialize the database.
from ncindex import db
from ncindex.models import *
db.create_all()
