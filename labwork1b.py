students = []
courses = []
marks = {}  

def input_students():
    """Inputs the number of students and their details (id, name, DoB)."""
    try:
        num_students = int(input("Enter the number of students in the class: "))
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return

    for _ in range(num_students):
        print("\n--- Enter Student Information ---")
        s_id = input("Student ID: ")
        s_name = input("Student Name: ")
        s_dob = input("Student DoB (e.g., DD/MM/YYYY): ")
        students.append({'id': s_id, 'name': s_name, 'dob': s_dob})

def input_courses():
    """Inputs the number of courses and their details (id, name)."""
    try:
        num_courses = int(input("Enter the number of courses: "))
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return

    for _ in range(num_courses):
        print("\n--- Enter Course Information ---")
        c_id = input("Course ID: ")
        c_name = input("Course Name: ")
        courses.append({'id': c_id, 'name': c_name})
        # Initialize an empty dictionary for this course to store marks
        marks[c_id] = {}

def list_students():
    if not students:
        print("\nNo students have been added yet.")
        return
        
    print("\n--- List of Students ---")
    for student in students:
        print(f"ID: {student['id']} | Name: {student['name']} | DoB: {student['dob']}")

def list_courses():
    """Lists all courses."""
    if not courses:
        print("\nNo courses have been added yet.")
        return
        
    print("\n--- List of Courses ---")
    for course in courses:
        print(f"ID: {course['id']} | Name: {course['name']}")

def input_marks():
    """Selects a course and inputs marks for all students in that course."""
    if not courses or not students:
        print("\nPlease ensure both students and courses have been added before entering marks.")
        return

    list_courses()
    course_id = input("\nSelect a course by entering its ID: ")

    # Validate course ID
    if course_id not in [c['id'] for c in courses]:
        print("Error: Course ID not found.")
        return

    print(f"\n--- Entering marks for Course ID: {course_id} ---")
    for student in students:
        while True:
            try:
                mark = float(input(f"Enter mark for {student['name']} (ID: {student['id']}): "))
                marks[course_id][student['id']] = mark
                break
            except ValueError:
                print("Invalid mark. Please enter a numerical value.")

def show_student_marks():
    """Shows student marks for a given course."""
    if not courses:
        print("\nNo courses have been added yet.")
        return

    list_courses()
    course_id = input("\nEnter the Course ID to view its marks: ")

    if course_id not in [c['id'] for c in courses]:
        print("Error: Course ID not found.")
        return

    print(f"\n--- Student Marks for Course ID: {course_id} ---")
    for student in students:
        
        student_mark = marks[course_id].get(student['id'], "N/A")
        print(f"Student: {student['name']} | ID: {student['id']} | Mark: {student_mark}")

def main():
    while True:
        print("  Practical Work 1: Student Mark Management")
        print("1. Input students in a class")
        print("2. Input courses")
        print("3. Input marks for a course")
        print("4. List students")
        print("5. List courses")
        print("6. Show student marks for a given course")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ")
        
        if choice == '1':
            input_students()
        elif choice == '2':
            input_courses()
        elif choice == '3':
            input_marks()
        elif choice == '4':
            list_students()
        elif choice == '5':
            list_courses()
        elif choice == '6':
            show_student_marks()
        elif choice == '0':
            print("Exiting program. Don't forget to push your work to your GitHub repository!")
            break
        else:
            print("Invalid choice. Please select a number between 0 and 6.")

if __name__ == "__main__":
    main()