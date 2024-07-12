import logging
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import Any, Optional, Sequence, Union

from app.enums.hyperoptstate import HyperoptState
from app.optimize.hyperopt_tools import HyperoptStateContainer

with suppress(ImportError):
    from skopt.space import Categorical, Integer, Real
    
    from app.optimize.space import SKDecimal
    
from app.exceptions import OperationalException

logger = logging.getLogger(__name__)

class BaseParameter(ABC):
    """
    Defines a parameter that can be optimized by hyperopt.
    """

    category: Optional[str]
    default: Any
    value: Any
    in_space: bool = False
    name: str

    def __init__(
        self,
        *,
        default: Any,
        space: Optional[str] = None,
        optimize: bool = True,
        load: bool = True,
        **kwargs,
    ):
        """
        Initialize hyperopt-optimizable parameter.
        :param space: A parameter category. Can be 'buy' or 'sell'. This parameter is optional if
         parameter field
         name is prefixed with 'buy_' or 'sell_'.
        :param optimize: Include parameter in hyperopt optimizations.
        :param load: Load parameter value from {space}_params.
        :param kwargs: Extra parameters to skopt.space.(Integer|Real|Categorical).
        """
        if "name" in kwargs:
            raise OperationalException(
                "Name is determined by parameter field name and can not be specified manually."
            )
        self.category = space
        self._space_params = kwargs
        self.value = default
        self.optimize = optimize
        self.load = load

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"

    @abstractmethod
    def get_space(self, name: str) -> Union["Integer", "Real", "SKDecimal", "Categorical"]:
        """
        Get-space - will be used by Hyperopt to get the hyperopt Space
        """

    def can_optimize(self):
        return (
            self.in_space
            and self.optimize
            and HyperoptStateContainer.state != HyperoptState.OPTIMIZE
        )
        
class NumericParameter(BaseParameter):
    """Internal parameter used for Numeric purposes"""

    float_or_int = Union[int, float]
    default: float_or_int
    value: float_or_int

    def __init__(
        self,
        low: Union[float_or_int, Sequence[float_or_int]],
        high: Optional[float_or_int] = None,
        *,
        default: float_or_int,
        space: Optional[str] = None,
        optimize: bool = True,
        load: bool = True,
        **kwargs,
    ):
        