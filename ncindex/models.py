from ncindex import db

class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return "{0}".format(self.name)

    def __repr__(self):
        return "<Instructor: {}>".format(self.name)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    code = db.Column(db.String(50))

    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __str__(self):
        return "{0} ({1})".format(self.name, self.code)

    def __repr__(self):
        return "<Department: {0} ({1})>".format(self.name, self.code)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.relationship('Department',
                                 backref=db.backref('courses',
                                                    lazy='dynamic'))
    number = db.Column(db.String(100))
    name = db.Column(db.String(500))

    def __init__(self, id, department, number):
        self.id = id
        self.department = department
        self.number = number

    def __str__(self):
        return "{0} {1}".format(self.department.code, self.number)

    def __repr__(self):
        return "<Course: {0} {1}>".format(self.department.code,
                                          self.number)

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.String(10))
    year = db.Column(db.Integer)

    def __init__(self, season, year):
        self.season = season
        self.year = year

    def __str__(self):
        return "{0} {1}".format(self.season, self.year)

    def __repr__(self):
        return "<Term: {0} {1}>".format(self.season, self.year)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course',
                             backref=db.backref('ratings', lazy='dynamic'))
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term',
                           backref=db.backref('ratings', lazy='dynamic'))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    instructor = db.relationship('Instructor',
                                 backref=db.backref('ratings', lazy='dynamic'))

    overall = db.Column(db.Integer)
    assignments = db.Column(db.Integer)
    exams = db.Column(db.Integer)
    helpfulness = db.Column(db.Integer)
    enthusiasm = db.Column(db.Integer)
    comment = db.Column(db.Text)

    def __init__(self, course, term, instructor, overall,
                 assignments, exams, helpfulness, enthusiasm, comment):
        self.course = course
        self.term = term
        self.instructor = instructor
        self.overall = overall
        self.assignments = assignments
        self.exams = exam
        self.helpfulness = helpfulness
        self.enthusiasm = enthusiasm
        self.comment = comment

    def __str__(self):
        return "Rating of {0} for {1} ({2})".format(self.instructor,
                                                    self.course,
                                                    self.term)

    def __repr__(self):
        return "<Rating (id={0}): {1}, {2}, {3}>".format(self.id,
                                                         self.instructor,
                                                         self.course,
                                                         self.term)