;; Quest Domain - Auto-generated
(define (domain quest-domain)
  (:requirements :strips :typing)

  (:types
    agent location item obstacle - object
  )

  (:predicates
    (at ?a - agent ?l - location)         ; agent is at location
    (has ?a - agent ?i - item)            ; agent has item
    (connected ?l1 ?l2 - location)        ; locations are connected
    (guarded_by ?l - location ?o - obstacle) ; location guarded by obstacle
    (alive ?a - agent)                    ; agent is alive
    (defeated ?o - obstacle)              ; obstacle is defeated
    (blocked ?from ?to - location)        ; path is blocked between two locations
  )

  (:action move
:parameters (?a - agent ?from ?to - location)
:precondition (and
  (at ?a ?from)
  (connected ?from ?to)
  (not (blocked ?from ?to))
  (alive ?a)
)
:effect (and
  (not (at ?a ?from))
  (at ?a ?to)
)
)
  (:action take
:parameters (?a - agent ?i - item ?l - location)
:precondition (and
  (at ?a ?l)
  (at ?i ?l)
  (alive ?a)
)
:effect (and
  (has ?a ?i)
  (not (at ?i ?l))
)
)
  (:action defeat_obstacle
:parameters (?a - agent ?o - obstacle ?l - location)
:precondition (and
  (at ?a ?l)
  (guarded_by ?l ?o)
  (alive ?a)
  (not (defeated ?o))
)
:effect (and
  (defeated ?o)
  (not (guarded_by ?l ?o))
)
)
)