;; Quest Domain - Auto-generated
(define (domain quest-domain) ; domain name
  (:requirements :strips :typing :action-costs) ; requirements

  (:types ; type declarations
    agent location item obstacle - object ; basic types
  ) ; end types

  (:predicates ; predicate declarations
    (at ?a - agent ?l - location) ; agent is at location
    (has ?a - agent ?i - item) ; agent has item
    (connected ?l1 ?l2 - location) ; locations are connected
    (guarded_by ?l - location ?o - obstacle) ; location guarded by obstacle
    (alive ?a - agent) ; agent is alive
    (defeated ?o - obstacle) ; obstacle is defeated
    (blocked ?from ?to - location) ; path is blocked
  ) ; end predicates

  (:functions ; fluents
    (total-cost) ; accumulated action cost
  ) ; end functions

  (:action move ; move from one location to another
   :parameters (?a - agent ?from ?to - location) ; agent and locations
   :precondition (and ; requirements to move
     (at ?a ?from) ; agent at starting location
     (connected ?from ?to) ; locations are connected
     (not (blocked ?from ?to)) ; path is not blocked
     (alive ?a) ; agent must be alive
     ) ; end precondition
   :effect (and ; effects of moving
     (not (at ?a ?from)) ; leave old location
     (at ?a ?to) ; arrive at new location
     (increase (total-cost) 1) ; count this action
   ) ; end effect
  ) ; end action
  (:action take ; pick up an item
   :parameters (?a - agent ?i - item ?l - location) ; agent, item, location
   :precondition (and ; requirements to take
     (at ?a ?l) ; agent at location
     (at ?i ?l) ; item at same location
     (alive ?a) ; agent alive
     ) ; end precondition
   :effect (and ; effects of taking
     (has ?a ?i) ; agent now has item
     (not (at ?i ?l)) ; item removed from location
     (increase (total-cost) 1) ; count this action
   ) ; end effect
  ) ; end action
  (:action defeat_obstacle ; defeat a guarding obstacle
   :parameters (?a - agent ?o - obstacle ?l - location) ; agent, obstacle, location
   :precondition (and ; requirements to defeat
     (at ?a ?l) ; agent at location
     (guarded_by ?l ?o) ; obstacle guards location
     (alive ?a) ; agent alive
     (not (defeated ?o)) ; obstacle not already defeated
     ) ; end precondition
   :effect (and ; effects of defeating
     (defeated ?o) ; obstacle defeated
     (not (guarded_by ?l ?o)) ; location unguarded
     (increase (total-cost) 1) ; count this action
   ) ; end effect
  ) ; end action
) ; end domain