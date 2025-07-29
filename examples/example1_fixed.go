package main

import (
    "errors"
    "fmt"
)

// Exception types
type Exception interface {
    Error() string
    Type() string
}

type BaseException struct {
    message string
    exType string
}

func (e *BaseException) Error() string {
    return e.message
}

func (e *BaseException) Type() string {
    return e.exType
}

func NewException(exType, message string) Exception {
    return &BaseException{message: message, exType: exType}
}

type Person struct {
    name string
    age int
}

func NewPerson(n string, a int) *Person {
    obj := &Person{}
    obj.name = "Unknown"
    obj.age = 0
    obj.name = n
    obj.age = a
    return obj
}

func (this *Person) GetName() string {
    return this.name
}

func (this *Person) SetAge(newAge int) {
    if (newAge < 0) {
        {
            panic(NewException("InvalidAge", "Age cannot be negative"))
        }
    }
    this.age = newAge
}

func (this *Person) Greet() {
    fmt.Printf("Hello, I'm %s and I'm %d years old\n", this.name, this.age)
}


type Student struct {
    Person
    school string
}

func NewStudent(n string, a int, s string) *Student {
    obj := &Student{}
    obj.school = "Unknown School"
    obj.Person = *NewPerson(n, a)
    obj.school = s
    return obj
}

func (this *Student) GetSchool() string {
    return this.school
}

func (this *Student) Study() {
    fmt.Printf("%s is studying at %s\n", this.name, this.school)
}


func main() {
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
                    fmt.Printf("Caught exception: %s - %s\n", e.Type(), e.Error())
                }
            }
        }()
        defer func() {
            fmt.Println("Cleanup completed")
        }()
        person := NewPerson("Alice", 25)
        person.Greet()
        student := NewStudent("Bob", 20, "MIT")
        student.Greet()
        student.Study()
        person.SetAge(-5)
    }()
}
