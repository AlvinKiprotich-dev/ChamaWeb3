import json
import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from web3 import Web3
from django.conf import settings
from eth_account import Account

logger = logging.getLogger(__name__)


class AvalancheWeb3Helper:
    """Helper class for interacting with Avalanche blockchain"""
    
    def __init__(self):
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(settings.AVALANCHE_RPC_URL))
        
        # Add middleware for Avalanche (which is POA-based)
        # Note: Avalanche C-Chain is EVM compatible, so we might not need special middleware
        
        # Set default account if private key is provided
        if settings.ADMIN_PRIVATE_KEY:
            account = Account.from_key(settings.ADMIN_PRIVATE_KEY)
            self.w3.eth.default_account = account.address
            self.default_account = account
        else:
            self.default_account = None
    
    def is_connected(self) -> bool:
        """Check if connected to Avalanche network"""
        try:
            return self.w3.is_connected()
        except Exception as e:
            logger.error(f"Web3 connection error: {e}")
            return False
    
    def get_balance(self, address: str) -> Decimal:
        """Get AVAX balance for an address"""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_avax = self.w3.from_wei(balance_wei, 'ether')
            return Decimal(str(balance_avax))
        except Exception as e:
            logger.error(f"Error getting balance for {address}: {e}")
            return Decimal('0')
    
    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction receipt"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt)
        except Exception as e:
            logger.error(f"Error getting transaction receipt for {tx_hash}: {e}")
            return None
    
    def verify_transaction(self, tx_hash: str, expected_amount: Decimal, 
                          expected_to_address: str) -> Dict[str, Any]:
        """Verify a transaction matches expected parameters"""
        try:
            # Get transaction details
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            # Convert amount to wei for comparison
            expected_amount_wei = self.w3.to_wei(expected_amount, 'ether')
            
            verification_result = {
                'is_valid': False,
                'tx_hash': tx_hash,
                'from_address': tx['from'],
                'to_address': tx['to'],
                'amount': self.w3.from_wei(tx['value'], 'ether'),
                'gas_used': receipt['gasUsed'],
                'block_number': receipt['blockNumber'],
                'status': receipt['status'],
                'errors': []
            }
            
            # Verify transaction succeeded
            if receipt['status'] != 1:
                verification_result['errors'].append('Transaction failed')
                return verification_result
            
            # Verify recipient address
            if tx['to'].lower() != expected_to_address.lower():
                verification_result['errors'].append('Recipient address mismatch')
            
            # Verify amount (allow small gas differences)
            if abs(tx['value'] - expected_amount_wei) > self.w3.to_wei(0.001, 'ether'):
                verification_result['errors'].append('Amount mismatch')
            
            # If no errors, transaction is valid
            if not verification_result['errors']:
                verification_result['is_valid'] = True
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Error verifying transaction {tx_hash}: {e}")
            return {
                'is_valid': False,
                'tx_hash': tx_hash,
                'errors': [f'Verification error: {str(e)}']
            }
    
    def estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """Estimate gas for a transaction"""
        try:
            return self.w3.eth.estimate_gas(transaction)
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            return 21000  # Default gas limit
    
    def get_gas_price(self) -> int:
        """Get current gas price"""
        try:
            return self.w3.eth.gas_price
        except Exception as e:
            logger.error(f"Error getting gas price: {e}")
            return self.w3.to_wei(25, 'gwei')  # Default gas price
    
    def send_transaction(self, to_address: str, amount: Decimal, 
                        private_key: Optional[str] = None) -> Optional[str]:
        """Send AVAX transaction"""
        try:
            if not private_key and not self.default_account:
                logger.error("No private key available for sending transaction")
                return None
            
            account = Account.from_key(private_key) if private_key else self.default_account
            
            # Build transaction
            transaction = {
                'to': to_address,
                'value': self.w3.to_wei(amount, 'ether'),
                'gas': 21000,
                'gasPrice': self.get_gas_price(),
                'nonce': self.w3.eth.get_transaction_count(account.address),
            }
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key or self.default_account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            return None
    
    def wait_for_transaction_receipt(self, tx_hash: str, timeout: int = 120) -> Optional[Dict[str, Any]]:
        """Wait for transaction to be mined"""
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return dict(receipt)
        except Exception as e:
            logger.error(f"Error waiting for transaction receipt {tx_hash}: {e}")
            return None


# Initialize global Web3 helper instance
web3_helper = AvalancheWeb3Helper()


def verify_contribution_transaction(tx_hash: str, amount: Decimal, 
                                  group_wallet_address: str) -> Dict[str, Any]:
    """Verify a contribution transaction on the blockchain"""
    return web3_helper.verify_transaction(tx_hash, amount, group_wallet_address)


def get_transaction_details(tx_hash: str) -> Optional[Dict[str, Any]]:
    """Get transaction details from blockchain"""
    return web3_helper.get_transaction_receipt(tx_hash)


def check_wallet_balance(address: str) -> Decimal:
    """Check wallet balance on Avalanche"""
    return web3_helper.get_balance(address)


def send_payout_transaction(to_address: str, amount: Decimal) -> Optional[str]:
    """Send payout transaction"""
    return web3_helper.send_transaction(to_address, amount)
