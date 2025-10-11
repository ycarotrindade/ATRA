from dataclasses import dataclass
from typing import Literal

@dataclass
class RandomAlgOptions:
    times: int
    quantity: int
    maximum: int
    
    @staticmethod
    def catch_essential_params(arguments:dict[str,int]) -> "RandomAlgOptions":
        return RandomAlgOptions(
        times = arguments['times'] or 1,
        quantity = arguments['quantity'] or 1,
        maximum = arguments['maximum'] or 20
        )