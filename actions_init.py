# actions/actions_init.py (updated)
from .actions_basic import get_basic_actions
from .actions_conditions import get_condition_actions
from .actions_ocr import get_ocr_actions
from .actions_trading import get_trading_actions
from .actions_selenium import get_selenium_actions
from .actions_flow import get_flow_actions
from actions.actions_init import register_all_actions

def register_all_actions(nexus):
    return {
        **get_basic_actions(nexus),
        **get_condition_actions(nexus),
        **get_ocr_actions(nexus),
        **get_trading_actions(nexus),
        **get_selenium_actions(nexus),
        **get_flow_actions(nexus),
    }
