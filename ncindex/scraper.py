import re
import requests
from bs4 import BeautifulSoup
from . import db
from .models import Instructor, Department, Course, Term, Rating

def run():
    r = requests.get('http://ninjacourses.com/explore/1/')
    soup = BeautifulSoup(r.text)
    for deptlist in soup.find_all(id=re.compile("^deptlist")):
        for deptentry in deptlist.find_all('li'):
            scrape_dept(deptentry)
    db.session.commit()

def scrape_dept(deptentry):
    parts = deptentry.a.string.split(" (")
    dept = Department.query.filter_by(name=parts[0]).first()
    if dept is None:
        dept = Department(name=parts[0], code=parts[1][:-1])
        db.session.add(dept)
    depturl = 'http://ninjacourses.com' + deptentry.a['href'] 
    print depturl
    deptreq = requests.get(depturl)
    deptsoup = BeautifulSoup(deptreq.text)
    courselist = deptsoup.find(id="dept-course-list")
    if courselist is not None:
        for courseentry in courselist.find_all('li'):
            scrape_course(dept, courseentry)

def scrape_course(dept, courseentry):
    courseurl = 'http://ninjacourses.com' + courseentry.a['href'] 
    print " " + courseurl
    coursesoup = BeautifulSoup(requests.get(courseurl).text)
    # check if course id is available
    floatdivs = coursesoup.find(id="tab-ratings").\
                           find_all("div", class_="float-left")
    if len(floatdivs) > 0 and floatdivs[1].find("a") is not None:
        number = courseentry.a['href'].split("/")[-2]
        course = Course.query.filter_by(department=dept, number=number).first()
        if course is None:
            id = int(floatdivs[1].a['href'].split("/")[-2])
            name = courseentry.contents[-1][3:]
            course = Course(id=id, department=dept, number=number, name=name)
            db.session.add(course)
        for instructorentry in coursesoup.find_all(class_="ratings-instructor"):
            if instructorentry.find(class_="rating-details-qtip"):
                scrape_instructor(instructorentry)

def scrape_instructor(instructorentry):
    instructorurl = 'http://ninjacourses.com' + instructorentry.a['href']
    print "  " + instructorurl
    instructorreq = requests.get(instructorurl)
    instructorsoup = BeautifulSoup(instructorreq.text)
    name = instructorsoup.find("span", class_="item fn").string
    instructor = Instructor.query.filter_by(name=name).first()
    if instructor is None:
        id = int(instructorurl.split("/")[-2])
        instructor = Instructor(id=id, name=name)
        db.session.add(instructor)
    # need to delete ratings, since there's no way to confirm identity
    for rating in instructor.ratings.all():
        db.session.delete(rating)
    scrape_instructor_page(instructor, instructorsoup, instructorurl)
        
def scrape_instructor_page(instructor, soup, instructorurl):
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
    courseid = int(ratingentry.contents[5]['href'].split("/")[-2])
    course = Course.query.get(courseid)
    
    termpair = ratingentry.contents[6][2:][:-1].split()
    term = Term.query.filter_by(season=termpair[0],
                                year=int(termpair[1])).first()
    if term is None:
        term = Term(season=termpair[0], year=int(termpair[1]))
        db.session.add(term)

    commentdiv = ratingentry.find(class_="comment")
    comment = "" if commentdiv is None else commentdiv.text
        
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
