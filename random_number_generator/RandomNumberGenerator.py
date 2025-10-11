from . import algs
from .types import RandomAlgOptions
from typing import Callable, Any
import re
import traceback

class RandomNumberGenerator:
    
    def __init__(self):
        self.REGEX_DICE_SYNTAX = re.compile(r'(?P<times>\d+)?#?(?P<quantity>\d+)d(?P<maximum>\d+)?(?P<phrase>[a-zA-Z\s]+)?')
        self.AVAILABLE_ALGS = algs.Algorithms
        self.current_alg = algs.get_alg_instance(self.AVAILABLE_ALGS.PYTHON)
    
    def _split_args(self, text:str) -> list[dict[str,int]]:
        text = text.strip()
        operations = text.split("+")
        operations = list(map(lambda x:x.strip(), operations))
        valid_args = []
        first = True
        times = None
        for operation in operations:
            try:
                int(operation)
            except:
                matches = re.match(self.REGEX_DICE_SYNTAX, operation)
            else:
                if not first:
                    valid_args.append(int(operation))
                    continue
                else:
                    raise RuntimeError("Not possible to generate a value, incorrect syntax")
            
            if matches is not None:
                args: dict[str,str | int | None]
                args = matches.groupdict()
            else:
                raise Exception('Not possible to generate a value, incorrect syntax')
            
            if not first and args['times'] is not None:
                raise RuntimeError("Not possible to generate a value, incorrect syntax")
            
            if first:
                args['times'] = int(args['times']) if args['times'] is not None else None
            else:
                args['times'] = valid_args[0]['times']
            
            args['quantity'] = int(args['quantity']) if args['quantity'] is not None else None
            args['maximum'] = int(args['maximum']) if args['maximum'] is not None else None
            args['phrase'] = args['phrase'].strip() if args['phrase'] is not None else None
            
            valid_args.append(args)
            first = False
            
        return valid_args
    
    def set_alg(self, alg:algs.Algorithms | str):
        try:
            self.current_alg = algs.get_alg_instance(alg)
        except:
            raise Exception('Not possible to change alg.')
    
    def generate_random_numbers(self,syntax:str):
        try:
            arguments = self._split_args(syntax)
            values = []
            for argument in arguments:
                if isinstance(argument, int):
                    values.append([[argument]] * arguments[0]['times'])
                else:
                    options = RandomAlgOptions.catch_essential_params(argument)
                    values.append(self.current_alg(options))
                
            return values, arguments
        except Exception as e:
            if str(e) == 'Not possible to generate a value, incorrect syntax':
                raise Exception('Not possible to generate a value, incorrect syntax')
            else:
                raise RuntimeError('Not possible to generate values' + traceback.format_exc())