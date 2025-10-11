import random
from .services import random_org_api
from .types import RandomAlgOptions
from typing import Any
from abc import ABC
from enum import Enum


class GenericAlg(ABC):
    
    def __repr__(self,):
        pass
    
    def __call__(self, options:RandomAlgOptions):
        pass
    
class PythonAlg(GenericAlg):
    
    def __repr__(self):
        return 'PythonAlg("Python")'
    
    def __str__(self):
        return "PYTHON"
    
    def __call__(self, options:RandomAlgOptions):
        values:list[Any] = []
        for _ in range(options.times):
            values.append([random.randint(1,options.maximum) for _ in range(options.quantity)])
        return values      

class RandomOrgAlg(GenericAlg):
    
    def __repr__(self):
        return 'RandomOrgAlg("RANDOM.ORG")'
    
    def __str__(self):
        return "RANDOM.ORG"
    
    def __call__(self, options:RandomAlgOptions):
        return random_org_api.request_random_integers(quantity=options.quantity,times=options.times,maximum=options.maximum)

class Algorithms(Enum):
    PYTHON = "PYTHON"
    RANDOMORG = "RANDOM.ORG"

def get_alg_instance(alg:Algorithms | str):
    option = ''
    if isinstance(alg, Algorithms):
        option = alg.value
    else:
        option = alg
    match option:
        case "PYTHON":
            return PythonAlg()
        
        case "RANDOM.ORG":
            return RandomOrgAlg()
        
        case _:
            return PythonAlg()