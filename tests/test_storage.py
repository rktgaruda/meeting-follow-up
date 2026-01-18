import os
import sqlite3
import pytest
from followup_agent.storage import Storage

@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    return str(db_path)

def test_mark_complete(temp_db):
    storage = Storage(temp_db)
    meeting_id = "test_123"
    
    assert not storage.is_completed(meeting_id)
    storage.mark_complete(meeting_id)
    assert storage.is_completed(meeting_id)

def test_get_completed_ids(temp_db):
    storage = Storage(temp_db)
    ids = {"a", "b", "c"}
    for i in ids:
        storage.mark_complete(i)
    
    assert storage.get_completed_ids() == ids
