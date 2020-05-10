
import parser
import lexer


def update_instructions(insts_tokens, machine):
    pc = machine.lookup_register("pc")
    flag = machine.lookup_register("flag")
    stack = machine.stack
    ops = machine.ops
    instructions = []
    count = 0
    for i in range(len(insts_tokens) - 1, -1, -1):
        token = insts_tokens[i]
        if token.type == "LABEL":
            machine.label_pointers[token.label] = instructions[::-1]
        else:
            instr = make_execution_procedure(token, machine.label_pointers, machine, pc, flag, stack, ops)
            instructions.append(instr)
            count += 1
    machine.install_instruction_sequence(instructions)

        
class ExecutionError(Exception): pass

        
def make_execution_procedure(inst, labels, machine, pc, flag, stack, ops):
    t = inst.type
    if t == "ASSIGN_REGISTER":
        return make_assign_register_instruction(inst, machine, labels, ops, pc)
    elif t == "ASSIGN_CONSTANT":
        return make_assign_constant_instruction(inst, machine, labels, ops, pc)
    elif t == "ASSIGN_LABEL":
        return make_assign_label_instruction(inst, machine, labels, ops, pc)
    elif t == "ASSIGN_OP":
        return make_assign_op_instruction(inst, machine, labels, ops, pc)
    elif t == "PERFORM":
        return make_perform_instruction(inst, machine, labels, ops ,pc)        
    elif t == "TEST":
        return make_test_instruction(inst, machine, labels, ops, flag, pc)
    elif t == "BRANCH":
        return make_branch_instruction(inst, machine, labels, flag, pc)
    elif t == "GOTO_LABEL":     
        return make_goto_label_instruction(inst, machine, labels, pc)
    elif t == "GOTO_REGISTER":
        return make_goto_register_instruction(inst, machine, labels, pc)
    elif t == "SAVE":
        return make_save_instruction(inst, machine, stack, pc)
    elif t == "RESTORE":
        return make_restore_instruction(inst, machine, stack, pc)
    raise ExecutionError("unknown instuction type {}".format(t)) 
        


def make_assign_register_instruction(inst, machine, labels, ops, pc):
    source_register = machine.lookup_register(inst.source_register)
    target_register = machine.lookup_register(inst.target_register)
    def execution():
        target_register.set_contents(source_register.get_contents())
        advance_pc(pc)
    return execution

def make_assign_constant_instruction(inst, machine, labels, ops, pc):
    target_register = machine.lookup_register(inst.target_register)
    constant = inst.constant
    def execution():
        target_register.set_contents(constant)
        advance_pc(pc)
    return execution

def make_assign_label_instruction(inst, machine, labels, ops, pc):
    target_register = machine.lookup_register(inst.target_register)
    label = inst.label
    def execution():
        target_register.set_contents(labels[label])
        advance_pc(pc)
    return execution

def make_assign_op_instruction(inst, machine, labels, ops, pc):
    target_register = machine.lookup_register(inst.target_register)
    condition_proc = make_operation_exp(inst, machine, labels, ops)
    def execution():
        op_result = condition_proc()
        target_register.set_contents(op_result)
        advance_pc(pc)
    return execution 
    
def make_perform_instruction(inst, machine, labels, ops ,pc):
    action = make_operation_exp(inst, machine, labels, ops)
    def execution():
        action()
        advance_pc(pc)
    return execution
  
def make_test_instruction(inst, machine, labels, ops, flag, pc):
    condition_proc = make_operation_exp(inst, machine, labels, ops)
    def execution():
        af = condition_proc()
        flag.set_contents(condition_proc())
        advance_pc(pc)
    return execution

def make_branch_instruction(inst, machine, labels, flag, pc):
    branch_dest = inst.label
    insts = labels[branch_dest]
    def execution():
        f = flag.get_contents()
        if f:
            pc.set_contents(insts)
            advance_pc(pc)
        else:
            advance_pc(pc)
    return execution

def make_goto_label_instruction(inst, machine, labels, pc):
    label = inst.label
    def execution():
        pc.set_contents(labels[label])
    return execution
    
def make_goto_register_instruction(inst, machine, labels, pc):
     register_name = inst.register
     register = machine.lookup_register(register_name)
     def execution():
         pc.set_contents(register.get_contents())
     return execution
    
def make_save_instruction(inst, machine, stack, pc):
    register = inst.register
    def execution():
        stack.Push(register.get_contents())
        advance_pc(pc)
    return execution

def make_restore_instruction(inst, machine, stack, pc):
    register = inst.register
    def execution():
        register.set_contents(stack.Pop())
        advance_pc(pc)
    return execution
        
def make_operation_exp(inst, machine, labels, ops):
    op = ops[inst.op]
    aprocs = []
    for arg in inst.args:
        aprocs.append(make_primitive_exp(arg, machine, labels))
    def execution():
        op_args = []
        for a in aprocs:
            op_args.append(a())
        return op(*op_args)
    return execution
    

def make_primitive_exp(exp, machine, labels):
    t = exp.type
    if t == "const":
        return lambda: exp.value
    elif t == "LABEL":
        return lambda: labels[exp.value]
    elif t == "reg":
        register = machine.lookup_register(exp.value)
        return lambda: register.get_contents()
    raise ExecutionError("unknown type {}".format(t))

def advance_pc(pc):
    pc.set_contents(pc.get_contents()[1:])
    