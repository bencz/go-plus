package utils

import (
    "github.com/user/example_project/exceptions"
    "strings"
)

type Validator struct {
}

func NewValidator() *Validator {
    obj := &Validator{}
    return obj
}

func (this *Validator) ValidateName(name string) bool {
    if (len(name) == 0) {
        {
            panic(NewException("EmptyName", "Name cannot be empty"))
        }
    }
    if (len(name) < 2) {
        {
            panic(NewException("ShortName", "Name must have at least 2 characters"))
        }
    }
    return true
}

func (this *Validator) ValidateEmail(email string) bool {
    if !strings.Contains(email, "@") {
        {
            panic(NewException("InvalidEmail", "Email must contain @ symbol"))
        }
    }
    if !strings.Contains(email, ".") {
        {
            panic(NewException("InvalidEmail", "Email must contain a domain"))
        }
    }
    return true
}

func (this *Validator) ValidateAge(age int) bool {
    if (age < 0) {
        {
            panic(NewException("InvalidAge", "Age cannot be negative"))
        }
    }
    if (age > 150) {
        {
            panic(NewException("InvalidAge", "Age cannot be greater than 150"))
        }
    }
    return true
}

