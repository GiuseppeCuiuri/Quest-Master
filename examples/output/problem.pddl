;; Quest Problem - Auto-generated
(define (problem quest-problem) ; problem name
  (:domain quest-domain) ; associated domain

  (:objects ; declare objects
    hero - agent ; the hero
    start - location ; location
    loc_1 - location ; location
    loc_2 - location ; location
    loc_3 - location ; location
    loc_4 - location ; location
    loc_5 - location ; location
    loc_6 - location ; location
    loc_7 - location ; location
    crystal_caverns - location ; location
    start_branch1 - location ; location
    start_branch2 - location ; location
    start_branch3 - location ; location
    loc_1_branch1 - location ; location
    loc_1_branch2 - location ; location
    loc_1_branch3 - location ; location
    loc_2_branch1 - location ; location
    loc_3_branch1 - location ; location
    loc_4_branch1 - location ; location
    loc_5_branch1 - location ; location
    loc_5_branch2 - location ; location
    loc_6_branch1 - location ; location
    loc_6_branch2 - location ; location
    loc_6_branch3 - location ; location
    loc_7_branch1 - location ; location
    loc_7_branch2 - location ; location
    golem - obstacle ; obstacle
  ) ; end objects

  (:init ; initial state
    (at hero start) ; hero starting position
    (alive hero) ; hero is alive
    (= (current-step) 0) ; step counter start
    (= (max-depth) 8) ; maximum depth
    (= (branch-limit start) 4) ; branch limit
    (= (actions-used start) 0) ; actions used
    (= (branch-limit loc_1) 4) ; branch limit
    (= (actions-used loc_1) 0) ; actions used
    (= (branch-limit loc_2) 4) ; branch limit
    (= (actions-used loc_2) 0) ; actions used
    (= (branch-limit loc_3) 4) ; branch limit
    (= (actions-used loc_3) 0) ; actions used
    (= (branch-limit loc_4) 4) ; branch limit
    (= (actions-used loc_4) 0) ; actions used
    (= (branch-limit loc_5) 4) ; branch limit
    (= (actions-used loc_5) 0) ; actions used
    (= (branch-limit loc_6) 4) ; branch limit
    (= (actions-used loc_6) 0) ; actions used
    (= (branch-limit loc_7) 4) ; branch limit
    (= (actions-used loc_7) 0) ; actions used
    (= (branch-limit crystal_caverns) 4) ; branch limit
    (= (actions-used crystal_caverns) 0) ; actions used
    (= (branch-limit start_branch1) 4) ; branch limit
    (= (actions-used start_branch1) 0) ; actions used
    (= (branch-limit start_branch2) 4) ; branch limit
    (= (actions-used start_branch2) 0) ; actions used
    (= (branch-limit start_branch3) 4) ; branch limit
    (= (actions-used start_branch3) 0) ; actions used
    (= (branch-limit loc_1_branch1) 4) ; branch limit
    (= (actions-used loc_1_branch1) 0) ; actions used
    (= (branch-limit loc_1_branch2) 4) ; branch limit
    (= (actions-used loc_1_branch2) 0) ; actions used
    (= (branch-limit loc_1_branch3) 4) ; branch limit
    (= (actions-used loc_1_branch3) 0) ; actions used
    (= (branch-limit loc_2_branch1) 4) ; branch limit
    (= (actions-used loc_2_branch1) 0) ; actions used
    (= (branch-limit loc_3_branch1) 4) ; branch limit
    (= (actions-used loc_3_branch1) 0) ; actions used
    (= (branch-limit loc_4_branch1) 4) ; branch limit
    (= (actions-used loc_4_branch1) 0) ; actions used
    (= (branch-limit loc_5_branch1) 4) ; branch limit
    (= (actions-used loc_5_branch1) 0) ; actions used
    (= (branch-limit loc_5_branch2) 4) ; branch limit
    (= (actions-used loc_5_branch2) 0) ; actions used
    (= (branch-limit loc_6_branch1) 4) ; branch limit
    (= (actions-used loc_6_branch1) 0) ; actions used
    (= (branch-limit loc_6_branch2) 4) ; branch limit
    (= (actions-used loc_6_branch2) 0) ; actions used
    (= (branch-limit loc_6_branch3) 4) ; branch limit
    (= (actions-used loc_6_branch3) 0) ; actions used
    (= (branch-limit loc_7_branch1) 4) ; branch limit
    (= (actions-used loc_7_branch1) 0) ; actions used
    (= (branch-limit loc_7_branch2) 4) ; branch limit
    (= (actions-used loc_7_branch2) 0) ; actions used
    (connected start loc_1) ; connection forward
    (connected loc_1 start) ; connection backward
    (connected start start_branch1) ; connection forward
    (connected start_branch1 start) ; connection backward
    (connected start start_branch2) ; connection forward
    (connected start_branch2 start) ; connection backward
    (connected start start_branch3) ; connection forward
    (connected start_branch3 start) ; connection backward
    (connected loc_1 loc_2) ; connection forward
    (connected loc_2 loc_1) ; connection backward
    (connected loc_1 loc_1_branch1) ; connection forward
    (connected loc_1_branch1 loc_1) ; connection backward
    (connected loc_1 loc_1_branch2) ; connection forward
    (connected loc_1_branch2 loc_1) ; connection backward
    (connected loc_1 loc_1_branch3) ; connection forward
    (connected loc_1_branch3 loc_1) ; connection backward
    (connected loc_2 loc_3) ; connection forward
    (connected loc_3 loc_2) ; connection backward
    (connected loc_2 loc_2_branch1) ; connection forward
    (connected loc_2_branch1 loc_2) ; connection backward
    (connected loc_3 loc_4) ; connection forward
    (connected loc_4 loc_3) ; connection backward
    (connected loc_3 loc_3_branch1) ; connection forward
    (connected loc_3_branch1 loc_3) ; connection backward
    (connected loc_4 loc_5) ; connection forward
    (connected loc_5 loc_4) ; connection backward
    (connected loc_4 loc_4_branch1) ; connection forward
    (connected loc_4_branch1 loc_4) ; connection backward
    (connected loc_5 loc_6) ; connection forward
    (connected loc_6 loc_5) ; connection backward
    (connected loc_5 loc_5_branch1) ; connection forward
    (connected loc_5_branch1 loc_5) ; connection backward
    (connected loc_5 loc_5_branch2) ; connection forward
    (connected loc_5_branch2 loc_5) ; connection backward
    (connected loc_6 loc_7) ; connection forward
    (connected loc_7 loc_6) ; connection backward
    (connected loc_6 loc_6_branch1) ; connection forward
    (connected loc_6_branch1 loc_6) ; connection backward
    (connected loc_6 loc_6_branch2) ; connection forward
    (connected loc_6_branch2 loc_6) ; connection backward
    (connected loc_6 loc_6_branch3) ; connection forward
    (connected loc_6_branch3 loc_6) ; connection backward
    (connected loc_7 crystal_caverns) ; connection forward
    (connected crystal_caverns loc_7) ; connection backward
    (connected loc_7 loc_7_branch1) ; connection forward
    (connected loc_7_branch1 loc_7) ; connection backward
    (connected loc_7 loc_7_branch2) ; connection forward
    (connected loc_7_branch2 loc_7) ; connection backward
    (guarded_by crystal_caverns golem) ; obstacle guarding
  ) ; end init

  (:goal ; goal conditions
    (and ; all goals
    (at hero crystal_caverns) ; goal condition
    (defeated golem) ; goal condition
    ) ; end and
  ) ; end goal
) ; end problem