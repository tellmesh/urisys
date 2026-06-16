import os

from urirdpedge.env import load_env_policy, resolve_env_var


def test_load_env_policy_includes_llm_vars():
    policy = load_env_policy()
    if not policy:
        return
    assert "OPENROUTER_API_KEY" in policy.get("secret_vars", [])
    assert "LLM_MODEL" in policy.get("public_vars", [])


def test_resolve_env_var_falls_back_to_process_env():
    os.environ["LLM_MODEL"] = "test-model-from-env"
    context = {"env_config": load_env_policy()} if load_env_policy() else {}
    assert resolve_env_var("LLM_MODEL", context) == "test-model-from-env"


def test_resolve_env_var_secret_via_env_policy(monkeypatch):
    policy = load_env_policy()
    if not policy:
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-fallback")
        assert resolve_env_var("OPENROUTER_API_KEY", {}, secret=True) == "sk-test-fallback"
        return
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-secret")
    context = {"env_config": policy, "allow_secret_read": True}
    assert resolve_env_var("OPENROUTER_API_KEY", context, secret=True) == "sk-test-secret"
