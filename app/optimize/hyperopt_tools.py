import logging
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import numpy as np
import rapidjson
from pandas import isna, json_normalize

from app.constants import FTHYPT_FILEVERSION, Config
from app.enums import HyperoptState
from app.exceptions import OperationalException
from app.misc import deep_merge_dicts, round_dict, safe_value_fallback2
from app.optimize.hyperopt_epoch_filters import hyperopt_filter_epochs

logger = logging.getLogger(__name__)

NON_OPT_PARAM_FILE_FORMAT = " # value loaded from strategy"

HYPER_PARAMS_FILE_FORMAT = rapidjson.NM_NATIVE | rapidjson.NM_NAN

def hyperopt_serializer(x):
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    
    return str(x)

class HyperoptStateContainer:
    """Singleton class to track state of hyperopt"""
    
    state: HyperoptState = HyperoptState.OPTIMIZE
    
    @classmethod
    def set_state(cls, value: HyperoptState):
        cls.state = value
        
class HyperoptTools:
    @staticmethod
    def get_strategy_filename(config: Config, strategy_name: str) -> Optional[Path]:
        """
        Get Strategy-location (filename) from strategy_name
        """
        from app.resolvers.strategy_resolver import StrategyResolver
        
        strategy_objs = StrategyResolver.search_all_objects(
            config, False, config.get("recursive_strategy_search", False)
        )
        strategies = [s for s in strategy_objs if s["name"] == strategy_name]
        if strategies:
            strategy = strategies[0]
            
            return Path(strategy["location"])
        return None
    
    @staticmethod
    def export_params(params, strategy_name: str, filename: Path):
        """
        Generate files
        """
        final_params = deepcopy(params["params_not_optimized"])
        final_params = deep_merge_dicts(params["params_details"], final_params)
        final_params = {
            "strategy_name": strategy_name,
            "params": final_params,
            "ft_stratparam_v": 1,
            "export_time": datetime.now(timezone.utc),
        }
        logger.info(f"Dumping parameters to {filename}")
        with filename.open("w") as f:
            rapidjson.dump(
                final_params,
                f,
                indent=2,
                default=hyperopt_serializer,
                number_mode=HYPER_PARAMS_FILE_FORMAT,
            )
    
    @staticmethod
    def load_params(filename: Path) -> Dict:
        """
        Load parameters from file
        """
        with filename.open("r") as f:
            params = rapidjson.load(f, number_mode=HYPER_PARAMS_FILE_FORMAT)
            
        return params
    
    @staticmethod
    def try_export_params(config: Config, strategy_name: str, params: Dict):
        if params.get(FTHYPT_FILEVERSION, 1) >= 2 and not config.get("disableparamexport", False):
            # Export parameters ...
            fn = HyperoptTools.get_strategy_filename(config, strategy_name)
            if fn:
                HyperoptTools.export_params(params, strategy_name, fn.with_suffix(".json"))
            else:
                logger.warning("Strategy not found, not exporting parameter file.")
                
    @staticmethod
    def has_space(config: Config, space: str) -> bool:
        """
        Tell if the space value is contained in the configuration
        """
        # 'trailing' and 'protection' spaces are not included in the 'default' set of spaces
        if space in ("trailing", "protection", "trades"):
            return any(s in config["spaces"] for s in [space, "all"])
        else:
            return any(s in config["spaces"] for s in [space, "all", "default"])
        
    @staticmethod
    def _read_results(results_file: Path, batch_size: int = 10) -> Iterator[List[Any]]:
        """
        Stream hyperopt results from file
        """
        
        import rapidjson
        
        logger.info(f"Reading epochs from '{results_file}'")
        with results_file.open("r") as f:
            data = []
            for line in f:
                data += [rapidjson.loads(line)]
                if len(data) >= batch_size:
                    yield data
                    data = []
        yield data