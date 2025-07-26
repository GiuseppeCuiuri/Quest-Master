;; Quest Problem - Auto-generated
(define (problem quest-problem) ; problem name
  (:domain quest-domain) ; associated domain

  (:objects ; declare objects
    hero - agent ; the hero
    start - location ; location
    elyria's_hollow - location ; location
    kaelinor's_spire_of_whispers - location ; location
    the_shadowed_spires_of_erebo - location ; location
    the_forgotten_citadel_of_xeridia - location ; location
    the_whispering_warrens_of_zha'thik - location ; location
    the_celestial_cisterns_of_aethereia - location ; location
    crystal_caverns - location ; location
    start_branch1 - location ; location
    start_branch2 - location ; location
    elyria's_hollow_branch1 - location ; location
    elyria's_hollow_branch2 - location ; location
    elyria's_hollow_branch3 - location ; location
    kaelinor's_spire_of_whispers_branch1 - location ; location
    kaelinor's_spire_of_whispers_branch2 - location ; location
    kaelinor's_spire_of_whispers_branch3 - location ; location
    the_shadowed_spires_of_erebo_branch1 - location ; location
    the_shadowed_spires_of_erebo_branch2 - location ; location
    the_shadowed_spires_of_erebo_branch3 - location ; location
    the_forgotten_citadel_of_xeridia_branch1 - location ; location
    the_forgotten_citadel_of_xeridia_branch2 - location ; location
    the_whispering_warrens_of_zha'thik_branch1 - location ; location
    the_celestial_cisterns_of_aethereia_branch1 - location ; location
    golem - obstacle ; obstacle
  ) ; end objects

  (:init ; initial state
    (at hero start) ; hero starting position
    (alive hero) ; hero is alive
    (= (current-step) 0) ; step counter start
    (= (max-depth) 7) ; maximum depth
    (= (branch-limit start) 4) ; branch limit
    (= (actions-used start) 0) ; actions used
    (= (branch-limit elyria's_hollow) 4) ; branch limit
    (= (actions-used elyria's_hollow) 0) ; actions used
    (= (branch-limit kaelinor's_spire_of_whispers) 4) ; branch limit
    (= (actions-used kaelinor's_spire_of_whispers) 0) ; actions used
    (= (branch-limit the_shadowed_spires_of_erebo) 4) ; branch limit
    (= (actions-used the_shadowed_spires_of_erebo) 0) ; actions used
    (= (branch-limit the_forgotten_citadel_of_xeridia) 4) ; branch limit
    (= (actions-used the_forgotten_citadel_of_xeridia) 0) ; actions used
    (= (branch-limit the_whispering_warrens_of_zha'thik) 4) ; branch limit
    (= (actions-used the_whispering_warrens_of_zha'thik) 0) ; actions used
    (= (branch-limit the_celestial_cisterns_of_aethereia) 4) ; branch limit
    (= (actions-used the_celestial_cisterns_of_aethereia) 0) ; actions used
    (= (branch-limit crystal_caverns) 4) ; branch limit
    (= (actions-used crystal_caverns) 0) ; actions used
    (= (branch-limit start_branch1) 4) ; branch limit
    (= (actions-used start_branch1) 0) ; actions used
    (= (branch-limit start_branch2) 4) ; branch limit
    (= (actions-used start_branch2) 0) ; actions used
    (= (branch-limit elyria's_hollow_branch1) 4) ; branch limit
    (= (actions-used elyria's_hollow_branch1) 0) ; actions used
    (= (branch-limit elyria's_hollow_branch2) 4) ; branch limit
    (= (actions-used elyria's_hollow_branch2) 0) ; actions used
    (= (branch-limit elyria's_hollow_branch3) 4) ; branch limit
    (= (actions-used elyria's_hollow_branch3) 0) ; actions used
    (= (branch-limit kaelinor's_spire_of_whispers_branch1) 4) ; branch limit
    (= (actions-used kaelinor's_spire_of_whispers_branch1) 0) ; actions used
    (= (branch-limit kaelinor's_spire_of_whispers_branch2) 4) ; branch limit
    (= (actions-used kaelinor's_spire_of_whispers_branch2) 0) ; actions used
    (= (branch-limit kaelinor's_spire_of_whispers_branch3) 4) ; branch limit
    (= (actions-used kaelinor's_spire_of_whispers_branch3) 0) ; actions used
    (= (branch-limit the_shadowed_spires_of_erebo_branch1) 4) ; branch limit
    (= (actions-used the_shadowed_spires_of_erebo_branch1) 0) ; actions used
    (= (branch-limit the_shadowed_spires_of_erebo_branch2) 4) ; branch limit
    (= (actions-used the_shadowed_spires_of_erebo_branch2) 0) ; actions used
    (= (branch-limit the_shadowed_spires_of_erebo_branch3) 4) ; branch limit
    (= (actions-used the_shadowed_spires_of_erebo_branch3) 0) ; actions used
    (= (branch-limit the_forgotten_citadel_of_xeridia_branch1) 4) ; branch limit
    (= (actions-used the_forgotten_citadel_of_xeridia_branch1) 0) ; actions used
    (= (branch-limit the_forgotten_citadel_of_xeridia_branch2) 4) ; branch limit
    (= (actions-used the_forgotten_citadel_of_xeridia_branch2) 0) ; actions used
    (= (branch-limit the_whispering_warrens_of_zha'thik_branch1) 4) ; branch limit
    (= (actions-used the_whispering_warrens_of_zha'thik_branch1) 0) ; actions used
    (= (branch-limit the_celestial_cisterns_of_aethereia_branch1) 4) ; branch limit
    (= (actions-used the_celestial_cisterns_of_aethereia_branch1) 0) ; actions used
    (connected start elyria's_hollow) ; connection forward
    (connected elyria's_hollow start) ; connection backward
    (connected start start_branch1) ; connection forward
    (connected start_branch1 start) ; connection backward
    (connected start start_branch2) ; connection forward
    (connected start_branch2 start) ; connection backward
    (connected elyria's_hollow kaelinor's_spire_of_whispers) ; connection forward
    (connected kaelinor's_spire_of_whispers elyria's_hollow) ; connection backward
    (connected elyria's_hollow elyria's_hollow_branch1) ; connection forward
    (connected elyria's_hollow_branch1 elyria's_hollow) ; connection backward
    (connected elyria's_hollow elyria's_hollow_branch2) ; connection forward
    (connected elyria's_hollow_branch2 elyria's_hollow) ; connection backward
    (connected elyria's_hollow elyria's_hollow_branch3) ; connection forward
    (connected elyria's_hollow_branch3 elyria's_hollow) ; connection backward
    (connected kaelinor's_spire_of_whispers the_shadowed_spires_of_erebo) ; connection forward
    (connected the_shadowed_spires_of_erebo kaelinor's_spire_of_whispers) ; connection backward
    (connected kaelinor's_spire_of_whispers kaelinor's_spire_of_whispers_branch1) ; connection forward
    (connected kaelinor's_spire_of_whispers_branch1 kaelinor's_spire_of_whispers) ; connection backward
    (connected kaelinor's_spire_of_whispers kaelinor's_spire_of_whispers_branch2) ; connection forward
    (connected kaelinor's_spire_of_whispers_branch2 kaelinor's_spire_of_whispers) ; connection backward
    (connected kaelinor's_spire_of_whispers kaelinor's_spire_of_whispers_branch3) ; connection forward
    (connected kaelinor's_spire_of_whispers_branch3 kaelinor's_spire_of_whispers) ; connection backward
    (connected the_shadowed_spires_of_erebo the_forgotten_citadel_of_xeridia) ; connection forward
    (connected the_forgotten_citadel_of_xeridia the_shadowed_spires_of_erebo) ; connection backward
    (connected the_shadowed_spires_of_erebo the_shadowed_spires_of_erebo_branch1) ; connection forward
    (connected the_shadowed_spires_of_erebo_branch1 the_shadowed_spires_of_erebo) ; connection backward
    (connected the_shadowed_spires_of_erebo the_shadowed_spires_of_erebo_branch2) ; connection forward
    (connected the_shadowed_spires_of_erebo_branch2 the_shadowed_spires_of_erebo) ; connection backward
    (connected the_shadowed_spires_of_erebo the_shadowed_spires_of_erebo_branch3) ; connection forward
    (connected the_shadowed_spires_of_erebo_branch3 the_shadowed_spires_of_erebo) ; connection backward
    (connected the_forgotten_citadel_of_xeridia the_whispering_warrens_of_zha'thik) ; connection forward
    (connected the_whispering_warrens_of_zha'thik the_forgotten_citadel_of_xeridia) ; connection backward
    (connected the_forgotten_citadel_of_xeridia the_forgotten_citadel_of_xeridia_branch1) ; connection forward
    (connected the_forgotten_citadel_of_xeridia_branch1 the_forgotten_citadel_of_xeridia) ; connection backward
    (connected the_forgotten_citadel_of_xeridia the_forgotten_citadel_of_xeridia_branch2) ; connection forward
    (connected the_forgotten_citadel_of_xeridia_branch2 the_forgotten_citadel_of_xeridia) ; connection backward
    (connected the_whispering_warrens_of_zha'thik the_celestial_cisterns_of_aethereia) ; connection forward
    (connected the_celestial_cisterns_of_aethereia the_whispering_warrens_of_zha'thik) ; connection backward
    (connected the_whispering_warrens_of_zha'thik the_whispering_warrens_of_zha'thik_branch1) ; connection forward
    (connected the_whispering_warrens_of_zha'thik_branch1 the_whispering_warrens_of_zha'thik) ; connection backward
    (connected the_celestial_cisterns_of_aethereia crystal_caverns) ; connection forward
    (connected crystal_caverns the_celestial_cisterns_of_aethereia) ; connection backward
    (connected the_celestial_cisterns_of_aethereia the_celestial_cisterns_of_aethereia_branch1) ; connection forward
    (connected the_celestial_cisterns_of_aethereia_branch1 the_celestial_cisterns_of_aethereia) ; connection backward
    (guarded_by crystal_caverns golem) ; obstacle guarding
  ) ; end init

  (:goal ; goal conditions
    (and ; all goals
    (at hero crystal_caverns) ; goal condition
    (defeated golem) ; goal condition
    ) ; end and
  ) ; end goal
) ; end problem