class Course:
    def __init__(self, course_id, name, credits):
        self.id = course_id
        self.name = name
        self.credits = credits

    def __str__(self):
        return f"{self.id:<12}{self.name:<28}{self.credits:<8}"
