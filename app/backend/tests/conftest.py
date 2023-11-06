from pytest import MonkeyPatch

monkey_patch = MonkeyPatch()
monkey_patch.setenv("OPENAI_API_KEY", "FAKE_API_KEY")
monkey_patch.setenv("SYSTEM_PROMPT", "demo system prompt")
