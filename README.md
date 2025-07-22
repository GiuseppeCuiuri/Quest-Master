QuestMaster: progetto finale su Agentic AI

Istruzioni
QuestMaster is a two-phase system designed to help authors create interactive narrative experiences through classical planning techniques (PDDL) and generative AI (LLMs). It comprises a Story Generation Phase (Phase 1) and an Interactive Story Game Phase (Phase 2).
Phase 1: Story Generation
Objective
Assist authors interactively in creating a logically consistent narrative quest represented as a PDDL planning problem.
Input
A Lore Document containing the following elements: 
•	Quest Description: Description of the adventure, including the initial state, goal, and possible obstacles. It also includes contextual information and background of the story's world.
•	Branching Factor: Minimum and maximum number of actions available at each narrative state.
•	Depth Constraints: Minimum and maximum number of steps to reach the goal.
Workflow
1.	PDDL generation and validation
o	The system produces a PDDL file that models the proposed adventure, including the initial state, goal, actions, and other elements. Each line is accompanied by a comment that textually describes what that specific line of PDDL code does.
o	The system uses a classical planner (e.g., Fast Downward) to validate if the current story (PDDL) formulation allows at least one valid path from the initial state to a goal state.


2.	Interactive Refinement Loop (if no valid PDDL model)


o	If no valid solution exists: an automated LLM agent (Reflection Agent) refines the PDDL file by identifying logical inconsistencies or narrative gaps. It then suggests specific modifications and interacts with the author through a suitable chat interface, seeking approval or further input before finalizing the refinements.


3.	Phase 1 Output
o	A complete and validated PDDL domain and problem file.
o	A finalized lore file (if updated to consider the new version of the PDDL file).


Phase 2: Interactive Story Game
Objective
Create an interactive web-based narrative experience using the completed PDDL and lore files generated in Phase 1.
Workflow
1.	HTML Generation


o	Use an LLM agent to generate an HTML interactive web-based implementation of the adventure described in the Lore file and modeled by the computed PDDL file.
o	Optionally, generate state-specific images representing the narrative context and upcoming choices.
Project files to be delivered
•	Project Files: Zip file with implemented code
•	Example of a Quest output: Input Lore document, and the output files (PDDL and HTML).

