# import gcalcli
import requests 
from bs4 import BeautifulSoup
import re
import HTMLParser
import time

from datetime import datetime
from dateutil import tz
import iso8601
import datetime as DT
from tzlocal import get_localzone
from time import mktime
from constants import headers
from constants import cookies


#short for call Dashboard
base_url = "https://www.bloc.io"

dow = dict(zip('mon tue wed thu fri sat sun'.split(),
           range(7)))


def get_students():
    r = requests.get(base_url + '/dashboard', headers=headers, cookies=cookies)
    # print r.text
    soup = BeautifulSoup(r.text)
    # print soup.prettify()

    print "hello world"
    i = 0

    link = ""
    students = []

    for user_summary in soup.find_all("div", class_="user-summary"):
        i += 1
        print(i)
        # print user_summary.prettify()

        # print name of student
        name = user_summary.find("h5", class_="name").a.string.encode('ascii')
        student = Student(name)

        #print the numbers of days left
        # return user_summary

        days_left_block = user_summary.find(text=re.compile("Days left"))

        if days_left_block:
            days_left_block = days_left_block.parent.parent.text
            days_left = days_left_block.strip().encode('ascii').split("\n")[1]
            student.days_left = days_left

        schedule_a_href = user_summary.find(href=re.compile("/schedule/*"))
        # schedule_a_href = user_summary.find(href=re.compile("/schedule/hugo-pinto"))

        if schedule_a_href:

            extend_url = schedule_a_href.get('href')
            student.schedule_url = base_url + extend_url
            student.query_for_schedule()
            
            link2 = base_url + "/users/"+extend_url.encode('ascii').split("/")[2]+"/checkpoints"
            student.checkpoint_url = link2

            user_progress_info_link = student.query_for_checkpoints()
            
            student.query_for_progress()
            student.calculate_appts()

            # student.print_details()
            # return student
            students.append(student)
            # return student

            # if i==4:
                # return students

    return students

        # break




def stringToLocalDate(date_string):
    print date_string
    datetime = iso8601.parse_date(date_string)
    to_zone = tz.tzlocal()
    return datetime.astimezone(to_zone)


def callBloc():
    r = requests.get('https://www.bloc.io/users/ricky-panzer', headers=headers, cookies=cookies)
    print r.text
    soup = BeautifulSoup(r.text)
    print soup.prettify()

def callBlocMentors():
    r = requests.get('https://www.bloc.io/mentors')
    print r.text

    soup = BeautifulSoup(r.text)
    # mentorScript = soup.head
    print soup.prettify()
    # return soup

def getDateFromDayOf(dateTimeObj, reqDayOf):
    weekday = dateTimeObj.weekday()        
    return dateTimeObj + DT.timedelta(days=(dow[reqDayOf.lower()]-weekday)%7)

def addOneDay(dateTimeObj):      
    return dateTimeObj + DT.timedelta(days=1)


# def getDateFromDayOf(dateTimeObj, reqDayOf):
    # weekday = dateTimeObj.weekday()        
    # return dateTimeObj + DT.timedelta(hours=(dow[reqDayOf.lower()]-weekday)%7)


class Student:

    def __init__(self, name):
        self.name = name

    def calculate_appts(self):

        appts = []

        i = 0
        for appt_string in self.appt_strings:
            print appt_string
            day_of_week = appt_string.split()[0]
            next_appt_date = self.next_appt_date
            # if i==0:
            #     # self.next_appt_date
            #     appt = getDateFromDayOf(next_appt_date, day_of_week)
            #     appts.append(appt)
                
            # else:
            digital_time = re.split("  |- | |-", appt_string)[1]
            today = datetime.today()
            datestring = str(next_appt_date.year) + " " + str(next_appt_date.month) + " " + str(next_appt_date.day) + " " + str(digital_time)
            modified_next_appt_date = time.strptime(datestring, "%Y %m %d %I:%M%p")
            dt = datetime.fromtimestamp(mktime(modified_next_appt_date))
            to_zone = tz.tzlocal()
            dt = dt.replace(tzinfo=to_zone)
            if dt < next_appt_date:
                dt = addOneDay(dt)
            
            appt = getDateFromDayOf(dt, day_of_week)
            appts.append(appt)
            
            i += 1
            # print appt

        self.appts = appts

    def query_for_schedule(self):
        link = self.schedule_url
        r = requests.get(link, headers=headers, cookies=cookies)
        soup = BeautifulSoup(r.text)
        # self.schedule_page = soup
        # print soup.prettify()
        schedule_list = soup.find_all("ul", class_="schedule-list")
        self.schedule_list = schedule_list
        appt_strings = []

        for index, schedule in enumerate(schedule_list):
            if index == 0 or schedule != schedule_list[index-1]:
                for li in schedule.find_all("li"):
                    print li
                    appt_strings.append(li.text.encode('ascii'))
                # print schedule

        self.appt_strings = appt_strings

    def print_details(self):
        print self.name
        print "next appt date "
        print self.next_appt_date
        print "appointments "
        print self.appts

    def query_for_checkpoints(self):
        # print self.checkpoint_url
        r = requests.get(self.checkpoint_url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(r.text)
        # print soup.prettify()
        # return soup
        ng_init = soup.find("div", class_="roadmaps-show").get('ng_init')
        splits = re.split("\(|,|", ng_init.encode('ascii'))
        roadmap_id = splits[1]
        user_id = splits[2]

        self.roadmap_id = roadmap_id
        self.user_id = user_id
        self.progress_url = base_url + "/api/v1/roadmaps/"+ roadmap_id + "/progress/" + user_id

        # https://www.bloc.io/api/v1/roadmaps/10/progress/2302061

    def query_for_progress(self):
        # print self.progress_url
        r = requests.get(self.progress_url, headers=headers, cookies=cookies)
        json = r.json()
        next_appt_date_string = json['mentor']['next_appointment_date'].encode('ascii')

        self.next_appt_date = stringToLocalDate(next_appt_date_string)

        course_end_date_string = json['course_end_date'].encode('ascii')
        self.course_end_date = stringToLocalDate(course_end_date_string)

    def create_event(self, appt, time_zone):
        print self.course_end_date
        end_date_utc = self.course_end_date.astimezone(tz.tzutc())
        print end_date_utc
        end_date_utc_string = end_date_utc.strftime("%Y%m%dT%H%M%SZ")
        event = {
          'summary': self.name + ' (360 Bloc Session)',
          'start': {
            'dateTime': appt.isoformat(),
            'timeZone': time_zone
          },
          'end': {
            'dateTime': (appt + DT.timedelta(minutes=30)).isoformat(),
            'timeZone': time_zone
          },
          'recurrence': [
            'RRULE:FREQ=WEEKLY;UNTIL=' + end_date_utc_string,
          ],
        }
        print event
        return event

# if __name__ == '__main__':
#     main()