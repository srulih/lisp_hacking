
import lisp_parser
import instructions as inst

class Register:
    def __init__(self, name):
        self.name = name
        self.contents = None
        
    def get_contents(self):
        return self.contents
    
    def set_contents(self, value):
        self.contents = value
        
        
class Stack:
    def __init__(self):
        self.stack = []
        
    def push(self, value):
        self.stack.append(value)
        
    def pop(self):
        if len(self.stack) == 0:
            return None
        return self.stack.pop()
    
    def initialise(self):
        self.stack = []
        

class Instruction:
    def __init__(self, text, func):
        self.text = text
        self.func = func


class Machine:
    def __init__(self):
        self.pc = Register("pc")
        self.flag = Register("flag")
        self.stack = Stack()
        self.registers = [self.pc, self.flag]
        self.instruction_sequence = []
        self.ops = {}
        self.label_pointers = {}
        
    def install_instruction_sequence(self, seq):
        self.instruction_sequence = seq
    
    def allocate_register(self, name):
        for r in self.registers:
            if r.name == name:
                raise "Multiply defined registers {}".format(name)
        
        self.registers.append(Register(name))
    
    def lookup_register(self, name):
        for r in self.registers:
            if r.name == name:
                return r
        raise "Unknown register {}".format(name)
        
    def set_register_value(self, name, value):
        reg = self.lookup_register(name)
        reg.set_contents(value)
        
    def get_register_value(self, name):
        reg = self.lookup_register(name)
        return reg.get_contents()

    def install_operations(self, ops):
        self.ops.update(ops)
        
    def execute(self):
        instructions = self.pc.get_contents()
        while len(instructions) != 0:
            instructions[0]()
            instructions = self.pc.get_contents()

    def start(self):
        self.pc.set_contents(self.instruction_sequence)
        self.execute()
        
    def get_stack(self):
        return self.stack
    
    def get_ops(self):
        return self.ops


def make_machine(registers, ops):
    machine = Machine()
    for register in registers:
        machine.allocate_register(register)
    machine.install_operations(ops)
    return machine
        
def assemble_machine(machine, text):
    p = lisp_parser.Parser()
    
    p.parse(text)
    inst.update_instructions(p.instructions, machine)
