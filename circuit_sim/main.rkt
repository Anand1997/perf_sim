#lang racket/base

;; Digital Circuit Simulator
;; Entry point: run with `racket main.rkt`

(require "core/wire.rkt")
(require "primitives/delays.rkt")
(require "primitives/gates.rkt")
(require "circuits/half-adder.rkt")
(require "circuits/full-adder.rkt")
(require "circuits/ripple-carry-adder.rkt")
(require "utils/probe.rkt")

;; -------------------------------------------------------------------
;; Demo: Full adder
;; -------------------------------------------------------------------
(define (demo-full-adder)
  (set! the-agenda (make-agenda))

  (define a (make-wire))
  (define b (make-wire))
  (define c-in (make-wire))
  (define sum (make-wire))
  (define c-out (make-wire))

  (probe 'a a)
  (probe 'b b)
  (probe 'c-in c-in)
  (probe 'sum sum)
  (probe 'c-out c-out)

  (full-adder a b c-in sum c-out)

  (displayln "\n=== Setting a=1, b=0, c-in=1 ===")
  (set-signal! a 1)
  (set-signal! c-in 1)
  (propagate)

  (displayln "\n=== Setting b=1 ===")
  (set-signal! b 1)
  (propagate))

;; -------------------------------------------------------------------
;; Demo: 4-bit ripple-carry adder
;; -------------------------------------------------------------------
(define (demo-ripple-adder)
  (set! the-agenda (make-agenda))

  (define a-wires (map (lambda (_) (make-wire)) '(1 2 3 4)))
  (define b-wires (map (lambda (_) (make-wire)) '(1 2 3 4)))
  (define s-wires (map (lambda (_) (make-wire)) '(1 2 3 4)))
  (define c (make-wire))

  ;; Probes on sum wires
  (for-each (lambda (w i)
              (probe (string->symbol (format "s~a" i)) w))
            s-wires
            '(0 1 2 3))

  (ripple-carry-adder a-wires b-wires s-wires c)

  ;; Set A = 0011 (3), B = 0001 (1)
  (displayln "\n=== Ripple Adder: A=0011, B=0001 ===")
  (set-signal! (list-ref a-wires 0) 1)
  (set-signal! (list-ref a-wires 1) 1)
  (set-signal! (list-ref b-wires 0) 1)
  (propagate))

;; Run demos
(demo-full-adder)
(demo-ripple-adder)