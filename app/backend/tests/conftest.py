from pytest import MonkeyPatch
import pytest

from settings.gladstone_settings import GladstoneSettings

monkey_patch = MonkeyPatch()
monkey_patch.setenv("OPENAI_API_KEY", "FAKE_API_KEY")
monkey_patch.setenv("SYSTEM_PROMPT", "demo system prompt")


@pytest.fixture()
def mock_settings():
    return GladstoneSettings("Mock System prompt")
