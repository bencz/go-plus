package models

import (
    "github.com/user/example_project/exceptions"
)

type Person struct {
    name string
    age int
}

func NewPerson(n string, a int) *Person {
    obj := &Person{}
    obj.name = "Unknown"
    obj.age = 0
    if (a < 0) {
        {
            panic(NewException("InvalidAge", "Age cannot be negative"))
        }
    }
    obj.name = n
    obj.age = a
    return obj
}

func (this *Person) GetName() string {
    return this.name
}

func (this *Person) GetAge() int {
    return this.age
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

func (this *Person) GetInfo() string {
    return fmt.Sprintf("%s (%d years old)", this.name, this.age)
}

