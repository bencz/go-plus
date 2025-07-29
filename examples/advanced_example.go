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

type Vehicle struct {
    brand string
    year int
}

func NewVehicle(b string, y int) *Vehicle {
    obj := &Vehicle{}
    obj.brand = "Unknown"
    obj.year = 0
    obj.brand = b
    obj.year = y
    return obj
}

func (this *Vehicle) GetInfo() string {
    return fmt.Sprintf("%s (%d)", this.brand, this.year)
}

func (this *Vehicle) Start() {
    fmt.Printf("Starting %s...\n", this.brand)
}


type Car struct {
    Vehicle
    doors int
    fuel float64
}

func NewCar(b string, y int, d int) *Car {
    obj := &Car{}
    obj.doors = 4
    obj.fuel = 0.0
    obj.Vehicle = *NewVehicle(b, y)
    obj.doors = d
    return obj
}

func (this *Car) Refuel(amount float64) {
    if (amount < 0) {
        {
            panic(NewException("InvalidAmount", "Fuel amount cannot be negative"))
        }
    }
    if (amount > 100) {
        {
            panic(NewException("TankOverflow", "Tank capacity exceeded"))
        }
    }
    this.fuel = (this.fuel + amount)
    fmt.Printf("Refueled %s with %.2f liters\n", this.brand, amount)
}

func (this *Car) Drive(distance float64) {
    consumption := (distance * 0.1)
    if (this.fuel < consumption) {
        {
            panic(NewException("InsufficientFuel", "Not enough fuel to drive"))
        }
    }
    this.fuel = (this.fuel - consumption)
    fmt.Printf("Drove %s for %.2f km. Fuel remaining: %.2f\n", this.brand, distance, this.fuel)
}

func (this *Car) GetFuelLevel() float64 {
    return this.fuel
}


func testVehicles() {
    func() {
        defer func() {
            if r := recover(); r != nil {
                var ex Exception
                if e, ok := r.(Exception); ok {
                    ex = e
                } else {
                    ex = NewException("RuntimeError", fmt.Sprintf("%v", r))
                }

                if ex.Type() == "TankOverflow" {
                    e := ex
                    fmt.Printf("Tank error: %s\n", e.Error())
                } else 
                if ex.Type() == "InsufficientFuel" {
                    e := ex
                    fmt.Printf("Fuel error: %s\n", e.Error())
                } else 
                if ex.Type() == "InvalidAmount" {
                    e := ex
                    fmt.Printf("Amount error: %s\n", e.Error())
                } else 
                if ex.Type() == "Exception" {
                    e := ex
                    fmt.Printf("General error: %s\n", e.Error())
                }
            }
        }()
        defer func() {
            fmt.Println("Vehicle test completed")
        }()
        car := NewCar("Toyota", 2020, 4)
        car.Start()
        car.Refuel(50.0)
        car.Drive(100.0)
        car.Drive(200.0)
        car.Refuel(80.0)
    }()
}

func main() {
    fmt.Println("=== Advanced Go-Extended Example ===")
    testVehicles()
    fmt.Println("Program finished successfully!")
}
