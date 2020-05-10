
import lisp_parser
import unittest


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.parser = lisp_parser.Parser()
        
    def test_assign_register(self):
        gcd_command = "(bla (assign t (reg a)))"
        self.parser.parse(gcd_command)
        instr = self.parser.instructions[1]
        self.assertEqual(2, len(self.parser.instructions))
        self.assertEqual("ASSIGN_REGISTER", instr.type)
        self.assertEqual("t", instr.target_register)
        self.assertEqual("a", instr.source_register)
      
    def test_assign_label(self):
        command = "(bla (assign t (label ha)))"
        self.parser.parse(command)
        instr = self.parser.instructions[1]
        self.assertEqual(2, len(self.parser.instructions))
        self.assertEqual("ASSIGN_LABEL", instr.type)
        self.assertEqual("t", instr.target_register)
        self.assertEqual("ha", instr.label)

    def test_assign_const(self):
        command = "(bla (assign t (const ha)))"
        self.parser.parse(command)
        instr = self.parser.instructions[1]
        self.assertEqual(2, len(self.parser.instructions))
        self.assertEqual("ASSIGN_CONSTANT", instr.type)
        self.assertEqual("t", instr.target_register)
        self.assertEqual("ha", instr.constant)
        
    def test_test(self):
        command = "(bla (test (op =) (reg b) (const 0)))"
        self.parser.parse(command)
        instr = self.parser.instructions[1]
        self.assertEqual(2, len(self.parser.instructions))
        self.assertEqual("TEST", instr.type)
        self.assertEqual("=", instr.op)
        self.assertEqual(2, len(instr.args))
        self.assertEqual("reg", instr.args[0].type)
        self.assertEqual("b",instr.args[0].value)
        self.assertEqual("const", instr.args[1].type)
        self.assertEqual(0,instr.args[1].value)
        
    def test_assign_op(self):
        gcd_command = "(bla (assign t (op rem) (reg a) (reg b)))"
        self.parser.parse(gcd_command)
        instr = self.parser.instructions[0]
        
    def test_branch(self):
        gcd_command = "(bla (branch (label haha)))"
        self.parser.parse(gcd_command)
        self.assertEqual(self.parser.instructions, [lisp_parser.LabelToken("bla"), lisp_parser.BranchToken("haha")])


if __name__ == '__main__': 
    unittest.main() 