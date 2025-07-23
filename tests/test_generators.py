from quest_master.generators.pddl_domain import PDDLDomainGenerator
from quest_master.generators.pddl_problem import PDDLProblemGenerator
from quest_master.models.quest_data import EnhancedQuestData


def sample_data():
    return EnhancedQuestData(
        locations=["start", "dest"],
        items=["sword"],
        obstacles={"dest": "dragon"},
        connections=[("start", "dest")],
        initial_location="start",
        goal_conditions=["at hero dest", "defeated dragon"],
    )


def test_generators_comments_and_item_location():
    data = sample_data()
    domain = PDDLDomainGenerator().generate(data)
    problem = PDDLProblemGenerator(data).generate()
    # every line should contain a comment marker ';'
    for line in domain.splitlines():
        if line.strip():
            assert ';' in line
    for line in problem.splitlines():
        if line.strip():
            assert ';' in line
    # item should start at start location
    assert "(at sword start)" in problem
