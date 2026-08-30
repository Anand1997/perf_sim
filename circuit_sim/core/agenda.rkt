#lang racket/base

(require racket/mpair)
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
  (mcons time queue))

(define (segment-time s) (mcar s))
(define (segment-queue s) (mcdr s))

;; -------------------------------------------------------------------
;; Agenda
;; -------------------------------------------------------------------
(define (make-agenda) (mcons 0 '()))

(define (current-time agenda) (mcar agenda))
(define (set-current-time! agenda time)
  (set-mcar! agenda time))

(define (segments agenda) (mcdr agenda))
(define (set-segments! agenda segs)
  (set-mcdr! agenda segs))

(define (first-segment agenda) (mcar (segments agenda)))
(define (rest-segments agenda) (mcdr (segments agenda)))

(define (empty-agenda? agenda)
  (null? (segments agenda)))

;; -------------------------------------------------------------------
;; Insert action at given time (maintains time-sorted order)
;; -------------------------------------------------------------------
(define (add-to-agenda! time action agenda)
  (define (belongs-before? segs)
    (or (null? segs)
        (< time (segment-time (mcar segs)))))
  (define (make-new-time-segment time action)
    (let ((q (make-queue)))
      (insert-queue! q action)
      (make-time-segment time q)))
  (define (add-to-segments! segs)
    (if (= (segment-time (mcar segs)) time)
        (insert-queue! (segment-queue (mcar segs)) action)
        (let ((rest (mcdr segs)))
          (if (belongs-before? rest)
              (set-mcdr! segs
                         (mcons (make-new-time-segment time action)
                                rest))
              (add-to-segments! rest)))))
  (let ((segs (segments agenda)))
    (if (belongs-before? segs)
        (set-segments! agenda
                       (mcons (make-new-time-segment time action)
                              segs))
        (add-to-segments! segs))))

;; -------------------------------------------------------------------
;; Remove / access first item
;; -------------------------------------------------------------------
(define (remove-first-agenda-item! agenda)
  (let ((q (segment-queue (first-segment agenda))))
    (delete-queue! q)
    (if (empty-queue? q)
        (set-segments! agenda (rest-segments agenda))
        'ok)))

(define (first-agenda-item agenda)
  (if (empty-agenda? agenda)
      (error "Agenda is empty -- FIRST-AGENDA-ITEM")
      (let ((first-seg (first-segment agenda)))
        (set-current-time! agenda (segment-time first-seg))
        (front-queue (segment-queue first-seg)))))
