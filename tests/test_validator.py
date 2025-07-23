from quest_master.validators.pddl_validator import PDDLValidator


def test_validator_local(monkeypatch):
    validator = PDDLValidator(fd_path="/tmp")
    def fake_run(cmd, capture_output=True, text=True, timeout=30):
        class R:
            returncode = 0
            stdout = "Solution found!"
            stderr = ""
        return R()
    monkeypatch.setattr("subprocess.run", fake_run)
    ok, err = validator.validate("domain", "problem")
    assert ok is True
    assert err is None
