#lang racket/base

(provide half-adder)

(require "../core/wire.rkt")
(require "../primitives/gates.rkt")

(define (half-adder a b s c)
  (let ((d (make-wire)) (e (make-wire)))
    (or-gate a b d)
    (and-gate a b c)
    (inverter c e)
    (and-gate d e s)
    'ok))