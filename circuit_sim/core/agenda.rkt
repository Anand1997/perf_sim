#lang racket/base

(require "queue.rkt")

(provide make-agenda
         current-time
         set-current-time!
         empty-agenda?
         add-to-agenda!
         first-agenda-item
         remove-first-agenda-item!)

;; -------------------------------------------------------------------
;; Time segment
;; -------------------------------------------------------------------
(define (make-time-segment time queue)
  (cons time queue))

(define (segment-time s) (car s))
(define (segment-queue s) (cdr s))

;; -------------------------------------------------------------------
;; Agenda
;; -------------------------------------------------------------------
(define (make-agenda) (list 0))

(define (current-time agenda) (car agenda))
(define (set-current-time! agenda time)
  (set-car! agenda time))

(define (segments agenda) (cdr agenda))
(define (set-segments! agenda segs)
  (set-cdr! agenda segs))

(define (first-segment agenda) (car (segments agenda)))
(define (rest-segments agenda) (cdr (segments agenda)))

(define (empty-agenda? agenda)
  (null? (segments agenda)))

;; -------------------------------------------------------------------
;; Insert action at given time (maintains time-sorted order)
;; -------------------------------------------------------------------
(define (add-to-agenda! time action agenda)
  (define (belongs-before? segs)
    (or (null? segs)
        (< time (segment-time (car segs)))))
  (define (make-new-time-segment time action)
    (let ((q (make-queue)))
      (insert-queue! q action)
      (make-time-segment time q)))
  (define (add-to-segments! segs)
    (if (= (segment-time (car segs)) time)
        (insert-queue! (segment-queue (car segs)) action)
        (let ((rest (cdr segs)))
          (if (belongs-before? rest)
              (set-cdr! segs
                        (cons (make-new-time-segment time action)
                              (cdr segs)))
              (add-to-segments! rest)))))
  (let ((segs (segments agenda)))
    (if (belongs-before? segs)
        (set-segments! agenda
                       (cons (make-new-time-segment time action)
                             segs))
        (add-to-segments! segs))))

;; -------------------------------------------------------------------
;; Remove / access first item
;; -------------------------------------------------------------------
(define (remove-first-agenda-item! agenda)
  (let ((q (segment-queue (first-segment agenda))))
    (delete-queue! q)
    (if (empty-queue? q)
        (set-segments! agenda (rest-segments agenda)))))

(define (first-agenda-item agenda)
  (if (empty-agenda? agenda)
      (error "Agenda is empty -- FIRST-AGENDA-ITEM")
      (let ((first-seg (first-segment agenda)))
        (set-current-time! agenda (segment-time first-seg))
        (front-queue (segment-queue first-seg)))))