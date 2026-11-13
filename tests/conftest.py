import pytest

from src.chatbot.semantic_cache import global_semantic_cache
from src.config import settings
from src.data.loader import DataLoader
from src.search.cache import global_cache


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensures database is initialized and clean before running tests."""
    loader = DataLoader()
    loader.initialize_database(force_reload=False)
    # Enable virtual LLM mode during tests to avoid exhausting OpenRouter rate limits
    settings.virtual_llm_mode = True
    yield
    global_cache.clear()
    global_semantic_cache.clear()
