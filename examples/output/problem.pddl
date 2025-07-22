;; Quest Problem - Auto-generated
(define (problem quest-problem)
  (:domain quest-domain)

  (:objects
    hero - agent
    start - location
    crystal_caverns - location
    golem - obstacle
  )

  (:init
    (at hero start)
    (alive hero)
    (connected start crystal_caverns)
    (connected crystal_caverns start)
    (guarded_by crystal_caverns golem)
  )

  (:goal
    (and
          (at hero crystal_caverns)
          (defeated golem)
    )
  )
)