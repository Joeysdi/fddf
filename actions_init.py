# actions/__init__.py
from .basic import get_basic_actions
from .conditions import get_condition_actions
from .ocr import get_ocr_actions
from .selenium import get_selenium_actions
from .trading import get_trading_actions
from .flow import get_flow_actions

def register_all_actions(nexus):
    """
    Returns a dictionary of all action functions: name → callable
    Used by ui.py to populate the "Add Action" menu
    """
    return {
        **get_basic_actions(nexus),
        **get_condition_actions(nexus),
        **get_ocr_actions(nexus),
        **get_selenium_actions(nexus),
        **get_trading_actions(nexus),
        **get_flow_actions(nexus),
    }