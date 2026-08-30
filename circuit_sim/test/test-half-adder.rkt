#lang racket/base

(require "../core/wire.rkt")
(require "../primitives/delays.rkt")
(require "../circuits/half-adder.rkt")
(require "../utils/probe.rkt")

(define (test-half-adder)
  ;; Reset global agenda
  (set! the-agenda (make-agenda))

  (define input-1 (make-wire))
  (define input-2 (make-wire))
  (define sum (make-wire))
  (define carry (make-wire))

  (probe 'sum sum)
  (probe 'carry carry)

  (half-adder input-1 input-2 sum carry)

  (displayln "\n--- Setting input-1 to 1 ---")
  (set-signal! input-1 1)
  (propagate)

  (displayln "\n--- Setting input-2 to 1 ---")
  (set-signal! input-2 1)
  (propagate)

  (displayln "\n--- Test complete ---"))

(test-half-adder)