#lang racket/base

(provide probe)

(require "../core/wire.rkt")
(require "../core/agenda.rkt")
(require "../primitives/delays.rkt")

(define (probe name wire)
  (add-action! wire
               (lambda ()
                 (newline)
                 (display name)
                 (display " ")
                 (display (current-time the-agenda))
                 (display "  New-value = ")
                 (display (get-signal wire)))))