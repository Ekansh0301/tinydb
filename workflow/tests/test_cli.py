from autose import cli


def test_only_the_workflows_own_token_is_trusted_for_dispatch():
    assert cli.trusted_dispatch("workflow_dispatch", "github-actions[bot]")
    assert not cli.trusted_dispatch("issues", "github-actions[bot]")
    assert not cli.trusted_dispatch("issue_comment", "github-actions[bot]")
    assert not cli.trusted_dispatch("workflow_dispatch", "some-user")
