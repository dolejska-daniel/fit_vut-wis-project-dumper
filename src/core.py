import logging
from pathlib import Path
from typing import Generator, Optional

from requests import HTTPError

from .http import Connection
from .io import get_user_credentials
from .objects import Course, CourseTask, TaskFile
from .parsing import StudyParser, CourseParser, TaskParser, TaskFilesParser

log = logging.getLogger("core")


class Downloader:

    connection: Connection = None

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def _get_courses(self, study_id: int) -> Generator[Course, None, None]:
        assert self.connection is not None
        page_content = self.connection.get_courses_page(study_id)
        for course_abbr, course_link in StudyParser(page_content).get_course_names_and_links():
            yield Course(course_abbr, course_link)

    def _get_course_tasks(self, course: Course) -> Generator[CourseTask, None, None]:
        assert self.connection is not None
        page_content = self.connection.get_content(course.link)
        for task_name, task_link in CourseParser(page_content).get_task_names_and_links():
            yield CourseTask(task_name, task_link, course)

    def _try_get_course_task_files_link(self, course_task_link: str) -> Optional[str]:
        assert self.connection is not None
        page_content = self.connection.get_content(course_task_link)
        return TaskParser(page_content).try_get_files_link()

    def _get_course_task_files(self, course_files_link: str, task: CourseTask) -> Generator[TaskFile, None, None]:
        assert self.connection is not None
        page_content = self.connection.get_content(course_files_link)
        for file_name, file_year, file_link in TaskFilesParser(page_content).get_file_names_and_links():
            yield TaskFile(file_name, file_year, file_link, task)

    def _explore_course(self, course: Course):
        log.info("exploring course %s", course.abbr)
        files_downloaded = 0
        for task in self._get_course_tasks(course):
            files_downloaded += self._download_files_from_course_task(task)

        if not files_downloaded:
            log.info("found no project files in %s", course.abbr)
        else:
            log.debug("found and downloaded %d file(s) from %s", files_downloaded, course.abbr)

    def _download_files_from_course_task(self, task: CourseTask) -> int:
        if (course_files_link := self._try_get_course_task_files_link(task.link)) is None:
            log.debug("course task '%s' in %s does not contain any downloadable files", task.name, task.course.abbr)
            return 0

        files_found = 0
        destination_dir = self.output_dir.joinpath(f"{task.course.abbr}/{task.name}")
        for file in self._get_course_task_files(course_files_link, task):
            log.debug("found file '%s', downloading...", file.name)
            file_destination_dir = destination_dir.joinpath(file.year)
            file_destination_dir.mkdir(parents=True, exist_ok=True)
            destination_path = file_destination_dir.joinpath(file.name)
            self.connection.download_file(file.link, destination_path)
            files_found += 1

        if not files_found:
            log.info("found no project files in %s/%s, none submitted maybe? :(", task.course.abbr, task.name)

        return files_found

    def _prepare_output(self):
        try:
            self.output_dir.mkdir()
        except FileExistsError:
            log.critical("The output directory '%s' already exists.", self.output_dir.as_posix())
            exit(1)

    def _setup_connection(self):
        while True:
            credentials = get_user_credentials()
            self.connection = Connection(*credentials)

            try:
                self.connection.get_studies_page()

            except HTTPError as ex:
                if ex.response.status_code == 401:
                    log.error("authentication has failed - the provided credentials were not correct, wanna try again?")
                    continue

                log.error("connection/authentication to WIS failed", exc_info=ex)
                exit(2)

            break

    def run(self):
        log.info("starting the mighty project downloader")

        self._setup_connection()
        self._prepare_output()
        self._explore_studies()

        self.connection.close()

    def _explore_studies(self):
        for study_id in range(1, 6):
            log.info("exploring courses in study %d", study_id)

            has_courses = False
            for course in self._get_courses(study_id):
                self._explore_course(course)
                has_courses = True

            if not has_courses:
                log.info("study %d does not contain any courses, completing the program", study_id)
                break
