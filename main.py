from face_module.face_register import register_employee
from face_module.face_recognize import recognize_faces

def main():
    while True:
        print("\n1 Register Employee")
        print("2 Start Attendance")
        print("3 Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            emp_id = input("Employee ID: ")
            name = input("Employee Name: ")
            register_employee(emp_id, name)
        elif choice == '2':
            recognize_faces()
        elif choice == '3':
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()