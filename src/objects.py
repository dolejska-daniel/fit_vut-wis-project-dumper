
class Course:

    def __init__(self, course_abbr: str, course_link: str):
        self.abbr = course_abbr
        self.link = course_link


class CourseTask:

    def __init__(self, task_name: str, task_link: str, course: Course):
        self.name = task_name
        self.link = task_link
        self.course = course


class TaskFile:

    def __init__(self, file_name: str, file_year: str, file_link: str, task: CourseTask):
        self.name = file_name
        self.year = file_year
        self.link = file_link
        self.task = task
