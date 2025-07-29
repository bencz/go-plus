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

type Calculator struct {
    result float64
}

func NewCalculator() *Calculator {
    obj := &Calculator{}
    obj.result = 0.0
    return obj
}

func (this *Calculator) Add(a float64, b float64) float64 {
    this.result = (a + b)
    return this.result
}

func (this *Calculator) Divide(a float64, b float64) float64 {
    if (b == 0.0) {
        {
            panic(NewException("DivisionByZero", "Cannot divide by zero"))
        }
    }
    this.result = (a / b)
    return this.result
}

func (this *Calculator) GetResult() float64 {
    return this.result
}


func testCalculator() {
    calc := NewCalculator()
    func() {
        defer func() {
            if r := recover(); r != nil {
                var ex Exception
                if e, ok := r.(Exception); ok {
                    ex = e
                } else {
                    ex = NewException("RuntimeError", fmt.Sprintf("%v", r))
                }

                if ex.Type() == "DivisionByZero" {
                    e := ex
                    fmt.Printf("Math error: %s\n", e.Error())
                } else 
                if ex.Type() == "Exception" {
                    e := ex
                    fmt.Printf("General error: %s\n", e.Error())
                }
            }
        }()
        defer func() {
            fmt.Printf("Final result: %.2f\n", calc.GetResult())
        }()
        result1 := calc.Add(10.0, 5.0)
        fmt.Printf("10 + 5 = %.2f\n", result1)
        result2 := calc.Divide(20.0, 4.0)
        fmt.Printf("20 / 4 = %.2f\n", result2)
        result3 := calc.Divide(10.0, 0.0)
        fmt.Printf("10 / 0 = %.2f\n", result3)
    }()
}

func main() {
    testCalculator()
}
