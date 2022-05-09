from typing import TYPE_CHECKING, Dict

from rotkehlchen.accounting.structures.base import (
    HistoryEventSubType,
    HistoryEventType,
    get_tx_event_type_identifier,
)
from rotkehlchen.chain.ethereum.accounting.interfaces import ModuleAccountantInterface
from rotkehlchen.chain.ethereum.accounting.structures import TxEventSettings

from .constants import CPT_LIQUITY

if TYPE_CHECKING:
    from rotkehlchen.accounting.pot import AccountingPot


class LiquityAccountant(ModuleAccountantInterface):

    def event_settings(self, pot: 'AccountingPot') -> Dict[str, TxEventSettings]:  # pylint: disable=unused-argument  # noqa: E501
        """Being defined at function call time is fine since this function is called only once"""
        return {
            get_tx_event_type_identifier(HistoryEventType.DEPOSIT, HistoryEventSubType.DEPOSIT_ASSET, CPT_LIQUITY): TxEventSettings(  # noqa: E501
                taxable=False,
                count_entire_amount_spend=False,
                count_cost_basis_pnl=False,
                method='spend',
                take=1,
                multitake_treatment=None,
            ),
            get_tx_event_type_identifier(HistoryEventType.SPEND, HistoryEventSubType.PAYBACK_DEBT, CPT_LIQUITY): TxEventSettings(  # noqa: E501
                taxable=False,
                count_entire_amount_spend=False,
                count_cost_basis_pnl=False,
                method='spend',
                take=1,
                multitake_treatment=None,
            ),
            get_tx_event_type_identifier(HistoryEventType.WITHDRAWAL, HistoryEventSubType.GENERATE_DEBT, CPT_LIQUITY): TxEventSettings(  # noqa: E501
                taxable=False,
                count_entire_amount_spend=False,
                count_cost_basis_pnl=False,
                method='acquisition',
                take=1,
                multitake_treatment=None,
            ),
            get_tx_event_type_identifier(HistoryEventType.WITHDRAWAL, HistoryEventSubType.REMOVE_ASSET, CPT_LIQUITY): TxEventSettings(  # noqa: E501
                taxable=False,
                count_entire_amount_spend=False,
                count_cost_basis_pnl=False,
                method='acquisition',
                take=1,
                multitake_treatment=None,
            ),
        }