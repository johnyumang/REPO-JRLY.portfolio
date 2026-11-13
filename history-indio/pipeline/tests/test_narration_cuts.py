"""narration_cuts.source_index: which original sentence each timings line is. Run: python -m unittest pipeline/tests/test_narration_cuts.py"""
import json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import narration_cuts as nc

S = [{'text': 'pangungusap %d.' % i} for i in range(10)]
T = [{'text': s['text'], 'start': float(i), 'end': i + 0.8} for i, s in enumerate(S)]


def ep(cuts=None, tim=T):
    d = tempfile.mkdtemp(); json.dump(S, open(d + '/sentences.json', 'w'))
    if cuts is not None: json.dump(cuts, open(d + '/narration_cuts.json', 'w'))
    return d, tim


class Cuts(unittest.TestCase):
    def test_no_cut_file(self):
        d, t = ep(); src, note = nc.source_index(d, t); self.assertEqual(src, list(range(10))); self.assertIsNone(note)

    def test_applied(self):
        d, _ = ep({'cut': [{'index': 3, 'text': S[3]['text']}, {'index': 7, 'text': S[7]['text']}]})
        t = [x for i, x in enumerate(T) if i not in (3, 7)]; src, note = nc.source_index(d, t)
        self.assertEqual(src, [0, 1, 2, 4, 5, 6, 8, 9]); self.assertIn('applied', note); self.assertNotIn('NOT', note)

    def test_not_applied_yet(self):
        d, t = ep({'cut': [{'index': 3, 'text': S[3]['text']}]}); src, note = nc.source_index(d, t)
        self.assertEqual(src, list(range(10))); self.assertIn('NOT applied', note)

    def test_wrong_count_stops(self):
        d, _ = ep({'cut': [{'index': 3, 'text': S[3]['text']}]})
        with self.assertRaises(SystemExit): nc.source_index(d, T[:7])

    def test_wrong_sentence_removed_stops(self):
        d, _ = ep({'cut': [{'index': 3, 'text': S[3]['text']}]})
        with self.assertRaises(SystemExit): nc.source_index(d, [x for i, x in enumerate(T) if i != 5])

    def test_revoice_replaces_in_place(self):
        c = {'cut': [{'index': 6, 'text': S[6]['text']}], 'revoice': [{'after_index': 5, 'new_text': 'bagong linya.'}]}
        d, _ = ep(c); t = [dict(x) for x in T]; t[6]['text'] = 'bagong linya.'; src, note = nc.source_index(d, t)
        self.assertEqual(src, list(range(10))); self.assertIn('replaced', note)
        src, note = nc.source_index(d, T); self.assertEqual(src, list(range(10)))          # before the new line is recorded: same map
        with self.assertRaises(SystemExit): nc.source_index(d, [x for i, x in enumerate(T) if i != 6])   # cut without the new line: refused

    def test_cut_and_revoice_together(self):
        c = {'cut': [{'index': 2, 'text': S[2]['text']}, {'index': 6, 'text': S[6]['text']}], 'revoice': [{'after_index': 5, 'new_text': 'bagong linya.'}]}
        d, _ = ep(c); t = [dict(x) for i, x in enumerate(T) if i != 2]; t[5]['text'] = 'bagong linya.'; src, note = nc.source_index(d, t)
        self.assertEqual(src, [0, 1, 3, 4, 5, 6, 7, 8, 9])


if __name__ == '__main__': unittest.main()
