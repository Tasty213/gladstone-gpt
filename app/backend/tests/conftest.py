from pytest import MonkeyPatch
import pytest

from app.backend.settings.chat_bot_settings import ChatbotSettings

monkey_patch = MonkeyPatch()
monkey_patch.setenv("OPENAI_API_KEY", "FAKE_API_KEY")


@pytest.fixture()
def mock_settings():
    return ChatbotSettings("Mock System prompt", "not-a-region", "not-a-database", 1)
