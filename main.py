import requests
import uncurl
import time
import json

courses_dicts = [] #a temp list to store course_info dicts
leaf_dicts = [] 

def getProfile():
    def getParams():
        curl = input('Your curl: ')
        curl_parsed = uncurl.parse_context(curl)
        cookies = dict(curl_parsed.cookies)
        headers = dict(curl_parsed.headers)
        return cookies, headers
    cookies, headers = getParams()
    url = 'https://next.xuetangx.com/api/v1/u/user/basic_profile/'
    profile = requests.get(url, cookies=cookies).json()
    return profile, cookies, headers
profile, cookies, headers = getProfile()

class Student:
    def __init__(self, profile):
        self.name = profile['data']['name']
        self.school = profile['data']['school']

    def greet(self):
        print(f'Logged in as {self.name}@{self.school}')

    def getAllCoursesData(self):
        # key "x-csrftoken' must be included or there'll be no returned value.
        url = 'https://next.xuetangx.com/api/v1/lms/user/user-courses/'
        courses = requests.get(url, cookies=cookies, headers=headers).json()
        return courses

    def listAllCourses(self):
        courses_data = self.getAllCoursesData()
        course_count = courses_data['data']['count']
        courses = courses_data['data']['product_list']
        print('No      SIGN                 CID          Course')
        order = 0
        for course in courses:
            sign = course['sign']
            cid = course['classroom_id']
            name = course['name']
            print(f'{order}      {sign}      {cid}      {name}')
            courses_dicts.append({"order": order, "sign": sign, "cid": cid, "name": name})
            order +=1

class Course():

    def __init__(self, sign, cid, cname):
        self.sign = sign
        self.cid = cid
        self.cname = cname #course_name

    def getCourseSchedule(self):
        url = 'https://next.xuetangx.com/api/v1/lms/learn/get_evaluation_detail/'
        params = (
            ('sign', self.sign),
            ('cid', self.cid),
        )
        evaluation_detail = requests.get(url, cookies=cookies, headers=headers, params=params).json()
        return evaluation_detail

    def listCourseInfo(self):
        schedule = self.getCourseSchedule()['data']['score_detail'][0]['schedule']
        cname = self.cname
        print(f'Course: {cname}     Progress: {schedule}%')

    def getUncommitedProblems(self):

        def getUncompletedLeaves():
            chapters = self.getCourseSchedule()['data']['score_detail'][0]['resource']
            for chapter in chapters:
                if 'leaf_list' in chapter: # Chapter is directly divided into leaves
                    leaves = chapter['leaf_list']
                    for leaf in leaves:
                        if leaf['schedule'] != 100: # one or several problem(s) not commited
                            leaf_id = leaf['id']
                            leaf_type_id = requests.get('https://next.xuetangx.com/api/v1/lms/learn/leaf_info/'+ str(self.cid) +'/'+ str(leaf_id)+'/', headers=headers,cookies=cookies, params={"sign":self.sign}).json()['data']['content_info']['leaf_type_id']
                            leaf_dicts.append({'leaf_id':leaf_id,
                                                'leaf_type_id': leaf_type_id
                                                  }
                                             )
                        else:
                            pass
                else: # Chapter is divided into sections and then leaves
                    sections = chapter['section_list']
                    for section in sections:
                        leaves = section['leaf_list']
                        for leaf in leaves:
                            leaf_id = leaf['id']
                            leaf_type_id = requests.get('https://next.xuetangx.com/api/v1/lms/learn/leaf_info/'+ str(self.cid) +'/'+ str(leaf_id)+'/', headers=headers,cookies=cookies, params={"sign":self.sign}).json()['data']['content_info']['leaf_type_id']
                            leaf_dicts.append({'leaf_id': leaf_id,
                                               'leaf_type_id': leaf_type_id
                                               }
                                              )

        def getUncompletedProblems():
            for leafinfo in leaf_dicts:
                leaf_type_id = leafinfo['leaf_type_id']
                url = 'https://next.xuetangx.com/api/v1/lms/exercise/get_exercise_list/' + str(leaf_type_id) + '/'
                data = problems = requests.get(url, cookies=cookies, headers=headers).json()['data']
                problems = data['problems']
                leafinfo['problem_ids'] = [] # a temp list to store problem ids
                for problem in problems:
                    if 'submit_time' in problem['user']:
                        pass
                    else:
                        leafinfo['problem_ids'].append(problem['problem_id'])
        getUncompletedLeaves()
        getUncompletedProblems()
        # 
        # [
        #     {'leaf_id': 11231651, 'leaf_type_id': 1651561561, 'problem_ids':[1,2,3,4,6,7]}
        #     .....
        #     .....
        # ]
    def getAnswerToProblem(self, leaf_type_id, problem_id):
        # Leaf as a unit
        exercise_url = 'https://next.xuetangx.com/api/v1/lms/exercise/get_exercise_list/' + str(leaf_type_id) + '/'
        exercise_dict = requests.get(exercise_url, headers=headers,cookies=cookies).json()
        problems = exercise_dict['data']['problems']
        for problem in problems:
            if problem_id == problem['problem_id']:
                problem_type = problem['content']['Type']
                if problem_type == 'SingleChoice':
                    answer = problem['user']['answer'] # list
                elif problem_type == 'FillBlank':
                    answer = problem['user']['answers']  # a dict
                elif problem_type == 'Judgement':
                    answer = problem['user']['answer']  # list
                elif problem_type == 'MultipleChoice':
                    answer = problem['user']['answer']  # a list
                elif problem_type == 'ShortAnswer': #No answer
                    answer = None
        return answer

    def problemApply(self, leaf_id, leaf_type_id, problem_id, answer):
       if answer == None:
           pass
       else:
            headers_apply = headers
            headers_apply['content-type'] = 'application/json'
            if isinstance(answer,dict):
                data = {
                    "leaf_id": leaf_id,
                    "classroom_id": self.cid,
                    "exercise_id": leaf_type_id,
                    "problem_id": problem_id,
                    "sign": self.sign,
                    "answers":answer, # FillBlank
                    "answer": [] # SingleChoice, MultipleChoice, Judgement
                }
            else:
                data = {
                    "leaf_id": leaf_id,
                    "classroom_id": self.cid,
                    "exercise_id": leaf_type_id,
                    "problem_id": problem_id,
                    "sign": self.sign,
                    "answers":{}, # FillBlank
                    "answer": answer # SingleChoice, MultipleChoice, Judgement
                }
            response = requests.post('https://next.xuetangx.com/api/v1/lms/exercise/problem_apply/', headers=headers_apply, cookies=cookies,data=str(data).replace('\'','\"'))
            print(response.text)

# Create a Student instance
student = Student(profile)

# A simple greeting
student.greet()

# Print all the courses you are learning
student.listAllCourses()

# Select a course and instantiate a course  
num = input('The one you choose(input the order num): ')
for each in courses_dicts:
    if int(num) == each['order']:
        cname = each['name']
        cid = each['cid']
        sign = each['sign']
        course = Course(sign, cid, cname)
    else:
        pass
courses_dicts.clear()

# Print name and progress of choosen course
course.listCourseInfo()

# Acquire all uncommited problems 
course.getUncommitedProblems()

# Answer all the problems by a  for-in iteration 
for leafinfo in leaf_dicts:
    leaf_id = leafinfo['leaf_id']
    leaf_type_id = leafinfo['leaf_type_id']
    problem_ids = leafinfo['problem_ids']
    for problem_id in problem_ids:
        answer = course.getAnswerToProblem(leaf_type_id, problem_id)
        course.problemApply(leaf_id, leaf_type_id, problem_id, answer)
        time.sleep(3)
print("Done")
