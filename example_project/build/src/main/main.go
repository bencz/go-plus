package main

import (
    "github.com/user/example_project/exceptions"
    "models"
    "utils"
)

func createPerson(name string, age int) {
    func() {
        defer func() {
            if r := recover(); r != nil {
                var ex Exception
                if e, ok := r.(Exception); ok {
                    ex = e
                } else {
                    ex = NewException("RuntimeError", fmt.Sprintf("%v", r))
                }

                if ex.Type() == "EmptyName" {
                    e := ex
                    fmt.Printf("Name error: %s\n", e.Error())
                } else 
                if ex.Type() == "ShortName" {
                    e := ex
                    fmt.Printf("Name error: %s\n", e.Error())
                } else 
                if ex.Type() == "InvalidAge" {
                    e := ex
                    fmt.Printf("Age error: %s\n", e.Error())
                } else 
                if ex.Type() == "Exception" {
                    e := ex
                    fmt.Printf("General error: %s\n", e.Error())
                }
            }
        }()
        validator := NewValidator()
        validator.ValidateName(name)
        validator.ValidateAge(age)
        person := NewPerson(name, age)
        person.Greet()
    }()
}

func createStudent(name string, age int, school string) {
    func() {
        defer func() {
            if r := recover(); r != nil {
                var ex Exception
                if e, ok := r.(Exception); ok {
                    ex = e
                } else {
                    ex = NewException("RuntimeError", fmt.Sprintf("%v", r))
                }

                if ex.Type() == "InvalidGrade" {
                    e := ex
                    fmt.Printf("Grade error: %s\n", e.Error())
                } else 
                if ex.Type() == "Exception" {
                    e := ex
                    fmt.Printf("Error creating student: %s\n", e.Error())
                }
            }
        }()
        validator := NewValidator()
        validator.ValidateName(name)
        validator.ValidateAge(age)
        student := NewStudent(name, age, school)
        student.SetGrade(8.5)
        student.Study()
        fmt.Println("Student info:", student.GetInfo())
    }()
}

func main() {
    fmt.Println("=== Go-Extended Multi-File Project Demo ===")
    fmt.Println("\n--- Testing Person Creation ---")
    createPerson("Alice", 25)
    createPerson("Bob", 30)
    createPerson("", 20)
    createPerson("A", 25)
    createPerson("Charlie", -5)
    fmt.Println("\n--- Testing Student Creation ---")
    createStudent("Diana", 20, "MIT")
    createStudent("Eve", 22, "Stanford")
    fmt.Println("\n--- Direct Object Creation ---")
    func() {
        defer func() {
            if r := recover(); r != nil {
                var ex Exception
                if e, ok := r.(Exception); ok {
                    ex = e
                } else {
                    ex = NewException("RuntimeError", fmt.Sprintf("%v", r))
                }

                if ex.Type() == "Exception" {
                    e := ex
                    fmt.Printf("Error in direct creation: %s\n", e.Error())
                }
            }
        }()
        defer func() {
            fmt.Println("\nDemo completed successfully!")
        }()
        person := NewPerson("Frank", 35)
        student := NewStudent("Grace", 19, "Harvard")
        fmt.Println("Person:", person.GetInfo())
        fmt.Println("Student:", student.GetInfo())
        student.SetGrade(9.2)
        fmt.Println("Updated student:", student.GetInfo())
    }()
}
