"""Typed expression transfer, explicit Boolean conversion and fail-closed bounds."""
from pathlib import Path
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from macro_bridge import translate,Unsupported
from checker import Session


class MacroBridgeTests(unittest.TestCase):
    def test_actual_selected_definitions(self):
        provenance=json.loads((ROOT/'public-data/ceil-div-source.json').read_text(encoding='utf-8'))
        old=translate(provenance['before']['line'],['m','n'])
        new=translate(provenance['after']['line'],['m','n'])
        request=dict(id='macro-check',word_bits=32,inputs={'m':[0,1,2,31,32,4294967294,4294967295],
                     'n':[1,2,3,7,32,4294967295]},original=old['source'],candidate=new['source'],
                     reference=new['source'],repair_guard='m > (4294967295u - (n - 1u))')
        session=Session(request)
        for m in request['inputs']['m']:
            for n in request['inputs']['n']:
                for role,expected in [('original',((m+n-1)%(2**32))//n),('candidate',(m+n-1)//n)]:
                    defined,value,_trace=session.run(role,{'m':m,'n':n})
                    self.assertTrue(defined);self.assertEqual(value,expected)

    def test_conversion_occurs_at_boolean_to_word_boundary(self):
        result=translate('#define F(A,B) ((A) + ((B) != 0))',['x','y'])
        self.assertIn('if (',result['source'])
        self.assertEqual(result['source'].count('if ('),1)
        nested=translate('#define F(A,B) ((A) + (((B) != 0) == 1))',['x','y'])
        self.assertEqual(nested['source'].count('if ('),2)

    def test_rejects_missing_type_or_unmodeled_execution(self):
        for body in ['M++ + N','++M + N','M = N','f(M) + N','M ? N : 0',
                     'M && N','M || N','M, N','(int) M + N','M + global',
                     '1 + 1','(M != 0) + 1','M + 01','M + 2147483648',
                     'M + 4294967296u','M + 0x10','M + 1L','M + 1.0','M + 1 /* x */']:
            with self.subTest(body=body),self.assertRaises(Unsupported):
                translate('#define F(M,N) '+body,['m','n'])

    def test_rejects_surface_ambiguity_and_parameter_changes(self):
        for definition,inputs in [('#define F(M,M) (M+1)',['m','n']),
                                  ('#define F(M,N) (M+N)',['m']),
                                  ('#define F(M,N) (M+N)',['m','m']),
                                  ('#define F(M,N) (M+N)',['m',[]]),
                                  ('#define F(M,N) (M+N)',['unsigned','n']),
                                  ('#define F(M,N) (M+N)',['rs_generated0','n']),
                                  ('#define F(M,N) (M+N)\n#define G 1',['m','n']),
                                  ('#define F(M,N) ('*40+'M'+')'*40,['m','n'])]:
            with self.subTest(definition=definition[:60]),self.assertRaises(Unsupported):
                translate(definition,inputs)
        with self.assertRaises(Unsupported):
            translate('#define F(M,N) '+'+'.join(['M']*70),['m','n'])

    def test_exact_source_is_not_a_macro_callsite_analysis(self):
        result=translate('#define F(A,B) ((A) / (B))',['x','y'])
        self.assertIn('caller applicability',result['premises'])
        self.assertIn('normalization',result['trace'])
        self.assertEqual(result['parameters'],['A','B'])


if __name__=='__main__':unittest.main()
