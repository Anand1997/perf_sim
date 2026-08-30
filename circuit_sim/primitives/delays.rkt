#lang racket/base

;; Gate delays and discrete-event scheduling via the Simulation Collection.
;; Install with: raco pkg install --auto planet-williams-simulation3

(provide inverter-delay
         and-gate-delay
         or-gate-delay
         after-delay
         propagate
         reset-agenda!
         current-time)

(require williams/simulation3/simulation)

(define inverter-delay 2)
(define and-gate-delay 3)
(define or-gate-delay 5)

(define (reset-agenda!)
  (current-simulation-environment (make-simulation-environment)))

(define (current-time)
  (current-simulation-time))

(define (after-delay delay action)
  (make-and-schedule-event (+ delay (current-simulation-time))
                           0
                           #f
                           action
                           '()))

(define (propagate)
  (start-simulation)
  'done)
