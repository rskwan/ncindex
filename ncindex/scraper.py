import re
import requests
from collections import deque
from bs4 import BeautifulSoup
from . import db
from .models import Instructor, Department, Course, Term, Rating

def run():
    """A breadth-first search on the graph of Ninja Courses data.
    We view each department, course, and instructor as a node,
    to be processed in a function determined by PROCESSORMAP. This reads
    all the departments, then all the courses, and finally all the
    instructors as well as their ratings."""
    
    # there's no way to verify the identity of ratings, since we don't have
    # access to their IDs, so we are forced to delete them all before scraping
    for rating in Rating.query.all():
        db.session.delete(rating)

    queue = deque() 
    queue.append(('root', {"url": 'http://ninjacourses.com/explore/1/'}))
    tracked = set()
    tracked.add('http://ninjacourses.com/explore/1/')
    while len(queue) > 0:
        pair = queue.popleft()
        for child in processormap[pair[0]](pair[1]):
            childurl = child[1]['url']
            if childurl not in tracked:
                tracked.add(childurl)
                queue.append(child)
    db.session.commit()

def scrape_root(data, limit=None):
    """Reads and stores all departments, then returns a list of
    department URL pairs."""
    soup = BeautifulSoup(requests.get(data['url']).text)
    depts = []
    for deptlist in soup.find_all(id=re.compile("^deptlist")):
        if limit and len(depts) > limit:
            break
        for deptentry in deptlist.find_all('li'):
            if limit and len(depts) > limit:
                break
            parts = deptentry.a.string.split(" (")
            dept = Department.query.filter_by(name=parts[0]).first()
            if dept is None:
                dept = Department(name=parts[0], code=parts[1][:-1])
                db.session.add(dept)
            deptdata = { 'department': dept,
                         'url': 'http://ninjacourses.com' + deptentry.a['href'] }
            depts.append(("dept", deptdata))
    return depts

def scrape_dept(data):
    """Return a list of ("course", data) pairs for each course in the
    department specified by DATA['url']."""
    print data['url']
    deptsoup = BeautifulSoup(requests.get(data['url']).text)
    courselist = deptsoup.find(id="dept-course-list")
    courses = []
    if courselist is not None:
        for courseentry in courselist.find_all('li'):
            for content in courseentry.contents:
                try:
                    if content.startswith(' - '):
                        name = content[3:]
                        number = courseentry.a['href'].split("/")[-2]
                        coursedata = { 'department': data['department'],
                                       'number': number,
                                       'name': name,
                                       'url': 'http://ninjacourses.com' \
                                               + courseentry.a['href'] }
                        courses.append(("course", coursedata))
                        break
                except TypeError:
                    pass
    return courses

def scrape_course(data):
    """Initializes the course if it doesn't exist and returns a list of
    ("instructor", data) pairs."""
    print " " + data['url']
    instructors = []
    coursesoup = BeautifulSoup(requests.get(data['url']).text)
    ratingstab = coursesoup.find(id="tab-ratings")
    floatdivs = ratingstab.find_all(class_="float-left")
    if len(floatdivs) > 1 and floatdivs[1].find("span", class_="count"):
        courseid = floatdivs[1].a['href'].split("/")[-2]
        course = Course.query.get(courseid)
        if course is None:
            course = Course(id=courseid,
                            department=data['department'],
                            number=data['number'],
                            name=data['name'])
            db.session.add(course)
        for instructorentry in coursesoup.find_all(class_="ratings-instructor"):
            if instructorentry.find(class_="rating-details-qtip"):
                instructorurl = 'http://ninjacourses.com' + instructorentry.a['href']
                instructors.append(("instructor", { 'url': instructorurl }))
    return instructors

def scrape_instructor(data):
    """Reads any new information about the instructor and calls
    scrape_instructor_page to start scraping ratings. This is where
    our BFS stops, so we return the empty list to indicate that
    this is a leaf node."""
    print "  " + data['url']
    instructorsoup = BeautifulSoup(requests.get(data['url']).text)
    countspan = instructorsoup.find(class_="count")
    if countspan is not None:
        id = int(data['url'].split("/")[-2])
        instructor = Instructor.query.get(id)
        if instructor is None:
            name = instructorsoup.find("span", class_="item fn").string
            instructor = Instructor(id=id, name=name)
        # reassign ratings even if instructor exists; they may have changed
        instructor.numratings = int(countspan.string)
        maindiv = instructorsoup.find(class_="main-rating")
        nums = maindiv.find_all(class_="rating-number")
        instructor.overall = int(nums[0].string)
        instructor.assignments = int(nums[1].string)
        instructor.exams = int(nums[2].string)
        instructor.helpfulness = int(nums[3].string)
        instructor.enthusiasm = int(nums[4].string)
        db.session.add(instructor)
        scrape_instructor_page(instructor, instructorsoup, data['url'])
    return []
        
def scrape_instructor_page(instructor, soup, instructorurl):
    """Scrapes all the ratings on SOUP and on any remaining pages."""
    for ratingouter in soup.find_all("div", class_="recent-rating"):
        scrape_rating(instructor, ratingouter.div)
    pagediv = soup.find("div", class_="pagination")
    if pagediv is not None:
        pageanchor = pagediv.find_all("a")[-1]
        if pageanchor.string.startswith("Next Page"):
            nexturl = instructorurl + pageanchor['href']
            nextsoup = BeautifulSoup(requests.get(nexturl).text)
            scrape_instructor_page(instructor, nextsoup, instructorurl)

def scrape_rating(instructor, ratingentry):
    """Creates the rating in RATINGENTRY for INSTRUCTOR."""
    courseid = int(ratingentry.contents[5]['href'].split("/")[-2])
    course = Course.query.get(courseid)

    termpair = ratingentry.contents[6][2:][:-1].split()
    term = Term.query.filter_by(season=termpair[0],
                                year=int(termpair[1])).first()
    if term is None:
        term = Term(season=termpair[0], year=int(termpair[1]))
        db.session.add(term)

    commentdiv = ratingentry.find(class_="comment")
    comment = "" if commentdiv is None else commentdiv.contents[1].strip()
        
    nums = ratingentry.find_all(class_="rating-number")
    rating = Rating(course=course,
                    term=term,
                    instructor=instructor,
                    overall=int(nums[0].string),
                    assignments=int(nums[1].string),
                    exams=int(nums[2].string),
                    helpfulness=int(nums[3].string),
                    enthusiasm=int(nums[4].string),
                    comment=comment)
    db.session.add(rating)

processormap = {
    "root": scrape_root,
    "dept": scrape_dept,
    "course": scrape_course,
    "instructor": scrape_instructor,
}
