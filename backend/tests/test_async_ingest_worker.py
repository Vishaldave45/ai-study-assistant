import unittest
import fitz
import asyncio
from app.engine.worker import AsyncIngestWorker, IngestProgress


class TestAsyncIngestWorker(unittest.TestCase):

    def test_process_document_async_progress_tracking(self):
        """Verify async document ingestion worker parses PDF bytes and reports progress stages."""
        # Create 2-page in-memory PDF
        doc = fitz.open()
        p1 = doc.new_page(width=595, height=842)
        p1.insert_text((50, 50), "Async Worker Test Page 1")

        p2 = doc.new_page(width=595, height=842)
        p2.insert_text((50, 50), "Async Worker Test Page 2")

        pdf_bytes = doc.tobytes()
        doc.close()

        progress_updates: list[IngestProgress] = []

        def handle_progress(p: IngestProgress):
            progress_updates.append(p)

        chunks = asyncio.run(
            AsyncIngestWorker.process_document_async(
                file_bytes=pdf_bytes,
                filename="test.pdf",
                progress_callback=handle_progress,
            )
        )

        self.assertGreater(len(chunks), 0)
        self.assertEqual(len(progress_updates), 4)

        # Verify progress percentage sequence
        percentages = [p.percentage for p in progress_updates]
        self.assertEqual(percentages, [10, 50, 80, 100])
        self.assertEqual(progress_updates[-1].stage, "Ready")


if __name__ == "__main__":
    unittest.main()
