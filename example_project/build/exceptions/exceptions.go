package exceptions

import (
    "fmt"
    "errors"
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
