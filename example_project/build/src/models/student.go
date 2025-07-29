package models

import (
    "github.com/user/example_project/exceptions"
)

type Student struct {
    Person
    school string
    grade float64
}

func NewStudent(n string, a int, s string) *Student {
    obj := &Student{}
    obj.school = "Unknown School"
    obj.grade = 0.0
    obj.Person = *NewPerson(n, a)
    obj.school = s
    return obj
}

func (this *Student) GetSchool() string {
    return this.school
}

func (this *Student) SetGrade(g float64) {
    if ((g < 0.0) || (g > 10.0)) {
        {
            panic(NewException("InvalidGrade", "Grade must be between 0 and 10"))
        }
    }
    this.grade = g
}

func (this *Student) GetGrade() float64 {
    return this.grade
}

func (this *Student) Study() {
    fmt.Printf("%s is studying at %s\n", this.name, this.school)
}

func (this *Student) GetInfo() string {
    return fmt.Sprintf("%s (%d years old) - Student at %s (Grade: %.1f)", this.name, this.age, this.school, this.grade)
}

