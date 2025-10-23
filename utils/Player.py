from collections import defaultdict
import numpy as np

class Player:
    '''The RPG player, used only for statistics
    
    # Attributes
    
    name:`str`
        The name of the player, commonly discord's display name
    
    dices:`defaultdict[int,list[int]]`
        All dice rolled by the player
    
    # Methods
    
    ## add_or_update_dices
        Update the dices attribute
        ### Params
            dice: `str`
                The dice type which the player rolled, it's used as key
            
            values:`list[int]`
                The values that the player acquired
        
        ### Return
            The self Player object
    
    ## n_critics
        Return number of critics rolled by the player
        ### Return
            The number of critics
            
    ## n_critical_failures
        Return the number of critical failures
        ### Return
            The number of critical failures
    '''
    
    
    def __init__(self,name:str):
        self.name = name
        self.dices:defaultdict[int,np.typing.ArrayLike] = defaultdict(list)
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Player('{self.name}')"
    
    def add_or_update_dices(self,dice:int,values:list[int]):
        '''Update the dices attribute, returns the object
        # Params
            dice: `int`
                The dice type which the player rolled, it's used as key
            
            values:`list[int]`
                The values that the player acquired
        '''
        
        self.dices[dice] = np.concatenate((self.dices[dice],np.array(values)))
        return self
    
    def n_critics(self):
        '''
        Return number of critics rolled by the player
        # Return
            The number of critics'''
        critics = 0
        for key, value in self.dices.items():
            critics += np.count_nonzero(value == key)
        return critics
    
    def n_critical_failures(self):
        '''Return the number of critical failures
        # Return
            The number of critical failures
        '''
        failures = 0
        for value in self.dices.values():
            failures += np.count_nonzero(value == 1)
        return failures
    
    def total_dices_rolled(self):
        dices = 0
        for values in self.dices.values():
            dices += len(values)
        return dices