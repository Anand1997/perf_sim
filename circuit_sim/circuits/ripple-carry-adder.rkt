#lang racket/base

(provide ripple-carry-adder)

(require "../core/wire.rkt")
(require "full-adder.rkt")

(define (ripple-carry-adder a-wires b-wires s-wires c)
  (define (iter a-wires b-wires s-wires c-in)
    (if (null? a-wires)
        'ok
        (let ((c-out (make-wire)))
          (full-adder (car a-wires)
                      (car b-wires)
                      c-in
                      (car s-wires)
                      c-out)
          (iter (cdr a-wires)
                (cdr b-wires)
                (cdr s-wires)
                c-out))))
  (iter a-wires b-wires s-wires c))