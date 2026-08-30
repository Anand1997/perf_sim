#lang racket/base

(provide the-agenda
         reset-agenda!
         inverter-delay
         and-gate-delay
         or-gate-delay
         after-delay
         propagate)

(require "../core/agenda.rkt")

;; -------------------------------------------------------------------
;; Global agenda and gate delays
;; -------------------------------------------------------------------
(define the-agenda (make-agenda))

(define (reset-agenda!)
  (set! the-agenda (make-agenda)))

(define inverter-delay 2)
(define and-gate-delay 3)
(define or-gate-delay 5)

;; -------------------------------------------------------------------
;; Propagation
;; -------------------------------------------------------------------
(define (after-delay delay action)
  (add-to-agenda! (+ delay (current-time the-agenda))
                  action
                  the-agenda))

(define (propagate)
  (if (empty-agenda? the-agenda)
      'done
      (let ((first-item (first-agenda-item the-agenda)))
        (first-item)
        (remove-first-agenda-item! the-agenda)
        (propagate))))