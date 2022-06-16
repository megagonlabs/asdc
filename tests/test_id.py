#!/usr/bin/env python3

import unittest

from asdc.schema.id import SID, DocID, UttrID


class TestID(unittest.TestCase):
    _prefix = "asdc.v1"
    _did = 1
    _doc_prefix = f"{_prefix}.001"
    _n = 5
    _uttr_prefix = f"{_doc_prefix}.{_n}"
    _snum = 7
    _sid = f"{_uttr_prefix}-{_snum}"

    def test_docid(self):
        d = DocID(id=self._doc_prefix)
        self.assertEqual(d.doc_num, 1)
        self.assertEqual(d.prefix, self._prefix)

        self.assertTrue(DocID(id="asdc.v1.2") < DocID(id="asdc.v1.104"))
        self.assertFalse(DocID(id="asdc.v1.104") < DocID(id="asdc.v1.2"))

    def test_uttrid(self):
        u = UttrID(id=self._uttr_prefix)
        self.assertEqual(u.docid, DocID(id=self._doc_prefix))
        self.assertEqual(u.num, self._n)

        self.assertTrue(UttrID(id="asdc.v1.001.2") < UttrID(id="asdc.v1.001.13"))

    def test_sid(self):
        sid = SID(id=self._sid)
        self.assertEqual(sid.id, self._sid)
        self.assertEqual(sid.docid.id, self._doc_prefix)
        self.assertEqual(sid.uttrid.id, self._uttr_prefix)
        self.assertEqual(sid.sentence_num, self._snum)

        self.assertTrue(SID(id="asdc.v1.001.2-9") < SID(id="asdc.v1.001.13-9"))
        self.assertTrue(SID(id="asdc.v1.001.2-9") < SID(id="asdc.v1.001.2-10"))
        self.assertTrue(SID(id="asdc.v1.001.12-9") < SID(id="asdc.v1.201.2-9"))


if __name__ == "__main__":
    unittest.main()
