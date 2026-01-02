from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    currency: str
    value: int

    def __add__(self,other:Money)->Money:
        if self.currency !=other.currency:
            raise ValueError(f'Cannot add {other.currency} to {self.currency}')
        return Money(self.currency,self.value+other.value)       
    def __mul__(self,other:int)->Money:
        return Money(self.currency,self.value*other)
    def __sub__(self,other:Money)->Money:
        if self.currency != other.currency:
            raise ValueError(f'Cannot sub {other.currency} to {self.currency}')
        return Money(self.currency,self.value-other.value)