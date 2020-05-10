import unittest
import python_vm

class TestGCDInstructions(unittest.TestCase):

    def test_gcd(self):
        machine = python_vm.make_machine(["a", "t", "b"], {"=": lambda x, y: x == y, "rem": lambda x, y: x%y})
        python_vm.assemble_machine(machine, '''(bla (test (op =) (reg b) (const 0))
            (branch (label gcd-done))
            (assign t (op rem) (reg a) (reg b))
            (assign a (reg b))
            (assign b (reg t))
            (goto (label bla))
            gcd-done)''')
        machine.set_register_value("a", 21)
        machine.set_register_value("b", 343)
        machine.start()
        self.assertEqual(machine.get_register_value("a"), 7)
