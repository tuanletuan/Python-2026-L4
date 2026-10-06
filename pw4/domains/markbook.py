import math

import numpy as np

MAX_MARK = 20.0  


class MarkBook:
    """Holds students, courses and marks, and does all the maths."""

    def __init__(self):
        self.students = []
        self.courses = []
        self.marks = {}  # {course_id: {student_id: mark}}

    # ---- lookups -----------------------------------------------------
    def find_student(self, student_id):
        return next((s for s in self.students if s.id == student_id), None)

    def find_course(self, course_id):
        return next((c for c in self.courses if c.id == course_id), None)

    # ---- adding data -------------------------------------------------
    def add_student(self, student):
        if self.find_student(student.id):
            raise ValueError(f"Student ID '{student.id}' already exists.")
        self.students.append(student)

    def add_course(self, course):
        if self.find_course(course.id):
            raise ValueError(f"Course ID '{course.id}' already exists.")
        self.courses.append(course)
        self.marks[course.id] = {}

    # ---- marks (math.floor) -----------------------------------------
    @staticmethod
    def floor_mark(mark):
        """Round DOWN to 1 decimal digit, e.g. 15.79 -> 15.7.
        round(..., 9) removes float noise such as 8.2*10 = 81.99999999."""
        return math.floor(round(mark * 10, 9)) / 10

    def set_mark(self, course_id, student_id, raw_mark):
        if not 0 <= raw_mark <= MAX_MARK:
            raise ValueError(f"Mark must be between 0 and {MAX_MARK:g}.")
        mark = self.floor_mark(raw_mark)
        self.marks[course_id][student_id] = mark
        return mark

    def get_mark(self, course_id, student_id):
        return self.marks[course_id].get(student_id)

    # ---- GPA (numpy) -------------------------------------------------
    def gpa(self, student):
        """Weighted average: sum(mark * credits) / sum(credits)."""
        scores, credits = [], []
        for course in self.courses:
            mark = self.get_mark(course.id, student.id)
            if mark is not None:
                scores.append(mark)
                credits.append(course.credits)
        if not credits:
            return 0.0
        scores = np.array(scores, dtype=float)
        credits = np.array(credits, dtype=float)
        return float(np.sum(scores * credits) / np.sum(credits))

    def sort_by_gpa(self):
        """Sort the student list by GPA, highest first."""
        gpas = np.array([self.gpa(s) for s in self.students], dtype=float)
        order = np.argsort(-gpas, kind="stable")
        self.students = [self.students[i] for i in order]
