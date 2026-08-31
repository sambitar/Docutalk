from app.services.ingest import chunk_text


def test_chunk_text_overlap():
    text = "a" * 1000
    chunks = chunk_text(text, chunk_size=800, overlap=120)
    assert len(chunks) >= 2
    assert all(len(c) <= 800 for c in chunks)


def test_chunk_text_empty():
    assert chunk_text("   ", 800, 120) == []
