from typing import Generator, Optional

from bs4 import BeautifulSoup


class Parser:

    def __init__(self, page_content: str):
        self.content = BeautifulSoup(page_content, "html5lib")


class StudyParser(Parser):

    def get_course_names_and_links(self) -> Generator[tuple[str, str], None, None]:
        course_entries = self.content.select(".content > .table-holder tr[align='center'][valign='top']")
        for entry in course_entries:
            yield entry.find("th").text, entry.select_one("a.bar")["href"]


class CourseParser(Parser):

    def get_task_names_and_links(self) -> Generator[tuple[str, str], None, None]:
        task_links = self.content.select(".content > form > .table-holder a.bar")
        for link in task_links:
            yield link.text, link["href"]


class TaskParser(Parser):

    def try_get_files_link(self) -> Optional[str]:
        task_links = self.content.select(".content > p > a")
        for link in task_links:
            link_target = link["href"]
            if "course-sf.php" in link_target:
                return link_target

        return None


class TaskFilesParser(Parser):

    def get_file_names_and_links(self) -> Generator[tuple[str, str, str], None, None]:
        year = self.content.find("h1").text.rsplit("/", maxsplit=1)[-1]
        file_links = self.content.select(".content > form > table tr[valign='middle'] > td > a")
        for link in file_links:
            yield link.text, year, link["href"]

        return None
