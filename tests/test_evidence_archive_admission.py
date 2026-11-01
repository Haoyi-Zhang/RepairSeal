"""Exact retained-data admission must not admit arbitrary or changed archives."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_gate

class ArchiveAdmission(unittest.TestCase):
    def test_reviewed_archive_is_accepted(self):
        for rel in release_gate.REVIEWED_DATA_ARCHIVES:
            with self.subTest(path=rel):
                self.assertTrue(release_gate.reviewed_data_archive(release_gate.ROOT/rel))

    def test_changed_archive_at_reviewed_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for rel in release_gate.REVIEWED_DATA_ARCHIVES:
                with self.subTest(path=rel):
                    path=root/rel
                    path.parent.mkdir(parents=True,exist_ok=True)
                    path.write_bytes(b'not the reviewed observations')
                    with mock.patch.object(release_gate,'ROOT',root):
                        self.assertFalse(release_gate.reviewed_data_archive(path))

    def test_same_bytes_under_another_name_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'other.zip'
            path.write_bytes((release_gate.ROOT/'results/vector-rss/observations.zip').read_bytes())
            with mock.patch.object(release_gate,'ROOT',root):
                self.assertFalse(release_gate.reviewed_data_archive(path))

if __name__=='__main__':unittest.main()
