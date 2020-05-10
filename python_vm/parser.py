
import lexer

class AssignRegisterToken:
    def __init__(self, target_register, source_register):
        self.type = "ASSIGN_REGISTER"
        self.target_register = target_register
        self.source_register = source_register
    
class AssignConstToken:
    def __init__(self, target_register, constant):
        self.type = "ASSIGN_CONSTANT"
        self.target_register = target_register
        self.constant = constant
        
    def __str__(self):
        return "type={}: target_register={}, constant={}".format(self.type, self.target_register, self.constant)
    
    def __repr__(self):
        return self.__str__()
        
class AssignOpToken:
    def __init__(self, target_register, op, args):
        self.type = "ASSIGN_OP"
        self.target_register = target_register
        self.op = op
        self.args = args
        
class AssignLabelToken:
    def __init__(self, target_register, label):
        self.type = "ASSIGN_LABEL"
        self.target_register = target_register
        self.label = label

class PerformToken:
    def __init__(self, op, args):
        self.type = "PERFORM"
        self.op = op
        self.args = args
        
class TestToken:
    def __init__(self, op, args):
        self.type = "TEST"
        self.op
        self.args = args
        
class BranchToken:
    def __init__(self, label):
        self.type = "BRANCH"
        self.label = label
    
    def __str__(self):
        return "type=%s: label=%s".format(self.type, self.label)
        
class GoToLabelToken:
    def __init__(self, label):
        self.type = "GOTO_LABEL"
        self.label = label
        
class GoToRegisterToken:
    def __init__(self, register):
        self.type = "GOTO_REGISTER"
        self.register = register

class SaveToken:
    def __init__(self, register):
        self.type = "SAVE"
        self.register = register
        
class RestoreToken:
    def __init__(self, register):
        self.type = "RESTORE"
        self.register = register

class ParseError(Exception): pass

class Parser:    
    def __init__(self):
        lex_rules = [
            ('assign',             'ASSIGN'),
            ('const',              'CONST'),
            ('test',              'TEST'),
            ('goto',            'GOTO'),
            ('perform',          'PERFORM'),
            ('branch',           'BRANCH'),
            ('save',             'SAVE'),
            ('restore',          'RESTORE'),
            ('register',          'REGISTER'),
            ('label',            'LABEL'),
            ('\d+',             'NUMBER'),
            ('[a-zA-Z_0-9]\w*',    'IDENTIFIER'),
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
        self.label_pointers = []
        
    def parse(self, text):
        self.lexer.input(text)
        self._get_next_token()
        self._top_level_controller()
        
    def _error(self, msg):
        raise ParseError(msg)

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
        self.label_pointers.append([label, self.instructions[l:]])
        
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
            return AssignRegisterToken(source_register, target_register)
        elif self.cur_token.type == "CONST":
            const = self._assign_const()
            return AssignConstToken(target_register, const)
        elif self.cur_token.type == "OP":
            op, args = self._assign_op()
            return AssignOpToken(target_register, op, args)
        else:
            raise ParseError("Error unknown token {} with value {}".format(self.cur_token.type, self.cur_token.val))
        
        
    # (assign ⟨register-name⟩ (label ⟨label-name⟩))
    def _assign_reg(self):
        self._match("REGISTER")
        register_name = self._match("IDENTIFIER")
        self._match(")")
        return register_name
    
    def _assign_const(self):
        self._match("CONST")
        register_name = self._match("IDENTIFIER")
        self._match(")")
        return register_name
    
    def _assign_op(self):
        self._match("OP")
        op = self._match("IDENTIFIER")
        self._match(")")
        args = []
        while self.cur_token.val != ")":
            arg = self._match("IDENTIFIER")
            args.append(arg)
        return op, args
    
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
        op = self._match("IDENTIFIER")
        self._match(")")
        args = []
        while self.cur_token.val != ")":
            arg = self._match("IDENTIFIER")
            args.append(arg)
        return TestToken(op, args)
    
    # (branch (label ⟨label-name⟩))
    def _branch(self):
        self._match("BRANCH")
        self._match("(")
        self._match("LABEL")
        label = self._match("IDENTIFIER")
        self.match(")")
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
        self.match(")")
        return label
    
    def _goto_register(self):
        self._match("REGISTER")
        register = self._match("IDENTIFIER")
        self.match(")")
        return register
    
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
