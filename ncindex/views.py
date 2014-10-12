from flask import render_template
from . import app
from .models import Instructor

@app.route('/')
def index():
    return render_template("index.html",
                           instructors=Instructor.query.all())

@app.route('/instructor/<int:instructor_id>')
def instructor(instructor_id):
    instructor = Instructor.query.filter_by(id=instructor_id).first_or_404()
    sorted_ratings = sorted(instructor.ratings, key=lambda rating: str(rating.course))
    return render_template("instructor.html",
                           instructor=instructor,
                           courses=instructor.courses,
                           ratings=sorted_ratings)
