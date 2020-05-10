
import lexer

class AssignRegisterToken:
    def __init__(self, target_register, source_register, text=None):
        self.type = "ASSIGN_REGISTER"
        self.target_register = target_register
        self.source_register = source_register
        self.text = text

    def __str__(self):
        return "type={}: target_register={}, source_register={}".format(self.type, self.target_register, self.source_register)
    
    def __repr__(self):
        return self.__str__()

class AssignConstToken:
    def __init__(self, target_register, constant, text=None):
        self.type = "ASSIGN_CONSTANT"
        self.target_register = target_register
        self.constant = constant
        self.text = text
        
    def __str__(self):
        return "type={}: target_register={}, constant={}".format(self.type, self.target_register, self.constant)
    
    def __repr__(self):
        return self.__str__()
        
class AssignOpToken:
    def __init__(self, target_register, op, args, text=None):
        self.type = "ASSIGN_OP"
        self.target_register = target_register
        self.op = op
        self.args = args
        self.text = text
        
    def __str__(self):
        return "type={}: target_register={} op={} args={}".format(self.type, self.target_register, self.op, self.args)
    
    def __repr__(self):
        return self.__str__()

        
class AssignLabelToken:
    def __init__(self, target_register, label, text=None):
        self.type = "ASSIGN_LABEL"
        self.target_register = target_register
        self.label = label
        self.text = text

    def __str__(self):
        return "type={}: target_register={} label={}".format(self.type, self.target_register, self.label)
    
    def __repr__(self):
        return self.__str__()

class PerformToken:
    def __init__(self, op, args, text=None):
        self.type = "PERFORM"
        self.op = op
        self.args = args
        self.text = text
        
    def __str__(self):
        return "type={}: op={} args={}".format(self.type, self.op, self.args)
    
    def __repr__(self):
        return self.__str__()
    
class TestToken:
    def __init__(self, op, args, text=None):
        self.type = "TEST"
        self.op = op
        self.args = args
        self.text = text

    def __str__(self):
        return "type={}: op={} args={}".format(self.type, self.op, self.args)
    
    def __repr__(self):
        return self.__str__()

class BranchToken:
    def __init__(self, label, text=None):
        self.type = "BRANCH"
        self.label = label
        self.text = text
    
    def __str__(self):
        return "type={}: label={}".format(self.type, self.label)
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return all([self.type == other.type, self.label == other.label])
        
        
class GoToLabelToken:
    def __init__(self, label, text=None):
        self.type = "GOTO_LABEL"
        self.label = label
        self.text = text
        
    def __str__(self):
        return "type={}: label={}".format(self.type, self.label)
    
    def __repr__(self):
        return self.__str__()

class GoToRegisterToken:
    def __init__(self, register, text=None):
        self.type = "GOTO_REGISTER"
        self.register = register
        self.text = text

class PrimitiveExpToken:
    def __init__(self, type, value, text=None):
        self.type = type
        self.value = value
        self.text = text

    def __str__(self):
        return "type={}: value={}".format(self.type, self.value)
    
    def __repr__(self):
        return self.__str__()
    
class SaveToken:
    def __init__(self, register, text=None):
        self.type = "SAVE"
        self.register = register
        self.text = text

class LabelToken:
    def __init__(self, label, text=None):
        self.type = "LABEL"
        self.label = label
        self.text = text
        
    def __str__(self):
        return "type={}: label={}".format(self.type, self.label)
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return all([self.type == other.type, self.label == other.label])

class RestoreToken:
    def __init__(self, register, text=None):
        self.type = "RESTORE"
        self.register = register
        self.text = text

class ParseError(Exception): pass

class Parser:    
    def __init__(self):
        lex_rules = [
            ('assign',             'ASSIGN'),
            ('const',              'CONST'),
            ('test',              'TEST'),
            ('goto',            'GOTO'),
            ('op',             'OP'),
            ('perform',          'PERFORM'),
            ('branch',           'BRANCH'),
            ('save',             'SAVE'),
            ('restore',          'RESTORE'),
            ('reg',          'REGISTER'),
            ('label',            'LABEL'),
            ('\d+',             'NUMBER'),
            ('[a-zA-Z_](\w|-|_)*',    'IDENTIFIER'),
            ('\*\*',            '**'),
            ('!=',              '!='),
            ('==',              '=='),
            ('>=',              '>='),
            ('<=',              '<='),
            ('>>',              '>>'),
            ('<<',              '<<'),
            ('&',               '&'),
            ('\^',              '^'),
            ('\|',              '|'),
            ('<',               '<'),
            ('>',               '>'),
            ('\+',              '+'),
            ('\-',              '-'),
            ('\*',              '*'),
            ('\/',              '/'),
            ('\(',              '('),
            ('\)',              ')'),
            ('=',               '='),
        ]

        self.lexer = lexer.Lexer(lex_rules, skip_whitespace=True)
        self.cur_token = None
        self.var_table = {}
        self.instructions = []
        self.label_pointers = {}
        
    def parse(self, text=None):
        self.lexer.input(text)
        self._get_next_token()
        self._top_level_controller()
        
    def _error(self, msg):
        raise ParseError(msg)
        
    def _match_from_list(self, type_list):
        """ The 'match' primitive of RD parsers.
            * Verifies that the current token is of the given type
            * Returns the value of the current token
            * Reads in the next token
        """

        if self.cur_token.type in type_list:
            val = self.cur_token.val
            self._get_next_token()
            return val
        else:
            self._error('Unmatched %s (found %s)' % (
                    type_list, self.cur_token.type))


    def _match(self, type):
        """ The 'match' primitive of RD parsers.
            * Verifies that the current token is of the given type
            * Returns the value of the current token
            * Reads in the next token
        """
        
        if self.cur_token.type == type:
            val = self.cur_token.val
            self._get_next_token()
            return val
        else:
            self._error('Unmatched %s (found %s)' % (
                type, self.cur_token.type))

    
    def _get_next_token(self):
        try:
            self.cur_token = self.lexer.token()

            if self.cur_token is None:
                self.cur_token = lexer.Token(None, None, None)
        except lexer.LexerError as e:
            self._error('Lexer error at position %d' % e.pos)
            
    
    def _top_level_controller(self):
        self._match("(")
        self._controller()
        while self.cur_token.type != ")":
            self._controller()
        self._match(")")

                
    def _controller(self):
        label = self._match("IDENTIFIER")
        self.instructions.append(LabelToken(label))
        if self.cur_token.type == ")":
            l = len(self.instructions)
            self.label_pointers[label] = [self.instructions[l:], l]
            return
        self._match("(")
        l = len(self.instructions)
        instr = self._instruction()
        self.instructions.append(instr)
        self._match(")")
        while self.cur_token.type != "IDENTIFIER" and self.cur_token.type != ")":
            self._match("(")
            instr = self._instruction()
            self.instructions.append(instr)
            self._match(")")
        self.label_pointers[label] = [self.instructions[l:], l]
        
    def _instruction(self):
        t = self.cur_token.type
        if t == "ASSIGN":
            return self._assign()
        elif t == "TEST":
            return self._test()
        elif t == "PERFORM":
            return self._perform()
        elif t == "BRANCH":
            return self._branch()
        elif t == "GOTO":
            return self._goto()
        elif t == "SAVE":
            return self._save()
        elif t == "RESTORE":
            return self._restore()
        else:
            raise ParseError("Error unknown token {} with value {}".format(self.cur_token.type, self.cur_token.val))
            
    def _assign(self):
        self._match("ASSIGN")
        target_register = self._match("IDENTIFIER")
        self._match("(")
        if self.cur_token.type == "REGISTER":
            source_register = self._assign_reg()
            return AssignRegisterToken(target_register, source_register)
        elif self.cur_token.type == "CONST":
            const = self._assign_const()
            return AssignConstToken(target_register, const)
        elif self.cur_token.type == "OP":
            op, args = self._assign_op()
            return AssignOpToken(target_register, op, args)
        elif self.cur_token.type == "LABEL":
            label_name = self._assign_label()
            return AssignLabelToken(target_register, label_name)
        else:
            raise ParseError("Error unknown token {} with value {}".format(self.cur_token.type, self.cur_token.val))
        
    #(assign ⟨register-name⟩ (reg ⟨register-name⟩))
    def _assign_reg(self):
        self._match("REGISTER")
        register_name = self._match("IDENTIFIER")
        self._match(")")
        return register_name

    #(assign ⟨register-name⟩ (const ⟨constant-value⟩))    
    def _assign_const(self):
        self._match("CONST")
        const_value = self._const()
        self._match(")")
        return const_value
    
    def _assign_op(self):
        self._match("OP")
        op = self._match("IDENTIFIER")
        self._match(")")
        args = []
        while self.cur_token.val != ")":
            self._match("(")
            type, val = self._primitive_exp()
            args.append(PrimitiveExpToken(type, val))
        return op, args
    
    # (assign ⟨register-name⟩ (label ⟨label-name⟩))
    def _assign_label(self):
        self._match("LABEL")
        label_name = self._match("IDENTIFIER")
        self._match(")")
        return label_name
        
    # (perform (op ⟨operation-name⟩) ⟨input1⟩ . . . ⟨inputn⟩)
    def _perform(self):
        self._match("PERFORM")
        self._match("(")
        self._match("OP")
        op = self._match("IDENTIFIER")
        self._match(")")
        args = []
        while self.cur_token.val != ")":
            arg = self._match("IDENTIFIER")
            args.append(arg)
        return PerformToken(op, args)
        
    # (test (op ⟨operation-name⟩) ⟨input1⟩ . . . ⟨inputn⟩)
    def _test(self):
        self._match("TEST")
        self._match("(")
        self._match("OP")
        op = self._match_from_list(["IDENTIFIER", "="])
        self._match(")")
        args = []
        while self.cur_token.val != ")":
            self._match("(")
            type, val = self._primitive_exp()
            args.append(PrimitiveExpToken(type, val))
        return TestToken(op, args)
    
    # (branch (label ⟨label-name⟩))
    def _branch(self):
        self._match("BRANCH")
        self._match("(")
        self._match("LABEL")
        label = self._match("IDENTIFIER")
        self._match(")")
        return BranchToken(label)
        
    def _goto(self):
        self._match("GOTO")
        self._match("(")
        if self.cur_token.type == "LABEL":
            label = self._goto_label()
            return GoToLabelToken(label)
        elif self.cur_token.type == "REGISTER":
            register = self._goto_register()
            return GoToRegisterToken(register)
        else:
            raise ParseError("Error unknown token {} with value {}".format(self.cur_token.type, self.cur_token.val))
        
    def _goto_label(self):
        self._match("LABEL")
        label = self._match("IDENTIFIER")
        self._match(")")
        return label
    
    def _goto_register(self):
        self._match("REGISTER")
        register = self._match("IDENTIFIER")
        self.match(")")
        return register
    
    def _primitive_exp(self):
        if self.cur_token.type == "CONST":
            type = self._match("CONST")
            val = self._const()
        elif self.cur_token.type == "REGISTER":
            type = self._match("REGISTER")
            val = self._match("IDENTIFIER")
        elif self.cur_token.type == "LABEL":
            type= self._match("LABEL")
            val = self._match("IDENTIFIER")
        else:
            raise ParseError("Error unknown token {} with value {}".format(self.cur_token.type, self.cur_token.val))
        self._match(")")
        return type, val
        
    def _const(self):
        if self.cur_token.type == "NUMBER":
            val = self._match("NUMBER")
            return int(val)
        elif self.cur_token.type == "IDENTIFIER":
            val = self._match("IDENTIFIER")
            return val
        
    # (save ⟨register-name⟩)
    def _save(self):
        self._match("SAVE")
        register = self._match("IDENTIFIER")
        return SaveToken(register)
    
    # (restore ⟨register-name⟩)    
    def _restore(self):
        self._match("RESTORE")
        register = self._match("IDENTIFIER")
        return RestoreToken(register)
