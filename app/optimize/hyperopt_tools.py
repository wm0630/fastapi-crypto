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