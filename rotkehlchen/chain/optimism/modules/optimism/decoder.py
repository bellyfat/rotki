from typing import TYPE_CHECKING, Any, Optional

from rotkehlchen.accounting.structures.balance import Balance
from rotkehlchen.accounting.structures.base import HistoryBaseEntry
from rotkehlchen.accounting.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.chain.evm.decoding.interfaces import DecoderInterface
from rotkehlchen.chain.evm.decoding.structures import ActionItem
from rotkehlchen.chain.evm.structures import EvmTxReceiptLog
from rotkehlchen.chain.evm.types import string_to_evm_address
from rotkehlchen.chain.optimism.constants import CPT_OPTIMISM
from rotkehlchen.constants.assets import A_ETH
from rotkehlchen.types import ChecksumEvmAddress, EvmTransaction, Location
from rotkehlchen.utils.misc import hex_or_bytes_to_address, ts_sec_to_ms

if TYPE_CHECKING:
    from rotkehlchen.chain.evm.decoding.base import BaseDecoderTools
    from rotkehlchen.chain.optimism.node_inquirer import OptimismInquirer
    from rotkehlchen.user_messages import MessagesAggregator

OPTIMISM_TOKEN = string_to_evm_address('0x4200000000000000000000000000000000000042')

DELEGATE_CHANGED = b'14\xe8\xa2\xe6\xd9~\x92\x9a~T\x01\x1e\xa5H]}\x19m\xd5\xf0\xbaMN\xf9X\x03\xe8\xe3\xfc%\x7f'  # noqa: E501


class OptimismDecoder(DecoderInterface):

    def __init__(    # pylint: disable=super-init-not-called
            self,
            optimism_inquirer: 'OptimismInquirer',  # pylint: disable=unused-argument
            base_tools: 'BaseDecoderTools',
            msg_aggregator: 'MessagesAggregator',
    ) -> None:
        self.base = base_tools

    def _decode_delegate_changed(  # pylint: disable=no-self-use
            self,
            tx_log: EvmTxReceiptLog,
            transaction: EvmTransaction,
            decoded_events: list[HistoryBaseEntry],  # pylint: disable=unused-argument
            all_logs: list[EvmTxReceiptLog],  # pylint: disable=unused-argument
            action_items: list[ActionItem],  # pylint: disable=unused-argument
    ) -> tuple[Optional[HistoryBaseEntry], list[ActionItem]]:
        if tx_log.topics[0] != DELEGATE_CHANGED:
            return None, []

        delegator = hex_or_bytes_to_address(tx_log.topics[1])
        if not self.base.is_tracked(delegator):
            return None, []

        from_delegate = hex_or_bytes_to_address(tx_log.topics[2])
        to_delegate = hex_or_bytes_to_address(tx_log.topics[3])
        event = HistoryBaseEntry(
            event_identifier=transaction.tx_hash,
            sequence_index=self.base.get_sequence_index(tx_log),
            timestamp=ts_sec_to_ms(transaction.timestamp),
            location=Location.BLOCKCHAIN,
            location_label=transaction.from_address,
            asset=A_ETH,
            balance=Balance(),
            notes=f'Change OP Delegate from {from_delegate} to {to_delegate}',
            event_type=HistoryEventType.INFORMATIONAL,
            event_subtype=HistoryEventSubType.GOVERNANCE,
            counterparty=CPT_OPTIMISM,
        )
        return event, []

    # -- DecoderInterface methods

    def addresses_to_decoders(self) -> dict[ChecksumEvmAddress, tuple[Any, ...]]:
        return {
            OPTIMISM_TOKEN: (self._decode_delegate_changed,),
        }

    def counterparties(self) -> list[str]:
        return [CPT_OPTIMISM]
