"""PII masking and tokenization handler."""
from cryptography.fernet import Fernet
from typing import Dict, Any
import re
import hashlib
import base64
import os
from app.config import settings


class PIIHandler:
    """Zero-retention PII masking and tokenization."""
    
    def __init__(self):
        """Initialize PII handler with encryption key."""
        key_str = settings.encryption_key
        key_bytes = key_str.encode()
        
        # Fernet requires a base64-encoded 32-byte key
        # Generate a proper Fernet key from the encryption_key string
        key_hash = hashlib.sha256(key_bytes).digest()
        # Fernet keys are base64-encoded, so we encode the hash
        fernet_key = base64.urlsafe_b64encode(key_hash)
        
        try:
            self.cipher = Fernet(fernet_key)
        except Exception:
            # Fallback: generate a new key and log warning
            self.cipher = Fernet(Fernet.generate_key())
        
        self.token_map: Dict[str, str] = {}
    
    def mask_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Replace PII with tokens before sending to LLM."""
        masked_data = data.copy()
        
        # Mask names
        if 'member_name' in masked_data:
            token = self._create_token(masked_data['member_name'])
            self.token_map[token] = masked_data['member_name']
            masked_data['member_name'] = token
        
        # Mask DOB
        if 'date_of_birth' in masked_data:
            token = self._create_token(masked_data['date_of_birth'])
            self.token_map[token] = masked_data['date_of_birth']
            masked_data['date_of_birth'] = token
        
        # Mask SSN
        if 'ssn' in masked_data:
            token = self._create_token(masked_data['ssn'])
            self.token_map[token] = masked_data['ssn']
            masked_data['ssn'] = token
        
        # Mask SSN patterns in free text
        if 'notes' in masked_data:
            masked_data['notes'] = self._mask_ssn_patterns(masked_data['notes'])
        
        return masked_data
    
    def unmask_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Replace tokens with actual PII after LLM processing."""
        unmasked_data = data.copy()
        
        for key, value in unmasked_data.items():
            if isinstance(value, str) and value in self.token_map:
                unmasked_data[key] = self.token_map[value]
            elif isinstance(value, dict):
                unmasked_data[key] = self.unmask_pii(value)
            elif isinstance(value, list):
                unmasked_data[key] = [
                    self.unmask_pii(item) if isinstance(item, dict) else item
                    for item in value
                ]
        
        return unmasked_data
    
    def _create_token(self, value: str) -> str:
        """Create a deterministic token for a PII value."""
        hash_obj = hashlib.sha256(value.encode())
        return f"TOKEN_{hash_obj.hexdigest()[:16].upper()}"
    
    def _mask_ssn_patterns(self, text: str) -> str:
        """Find and mask SSN patterns like XXX-XX-XXXX."""
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        
        def replace_ssn(match):
            ssn = match.group(0)
            token = self._create_token(ssn)
            self.token_map[token] = ssn
            return token
        
        return re.sub(ssn_pattern, replace_ssn, text)
    
    def clear_tokens(self):
        """Clear token map after processing (zero retention)."""
        self.token_map.clear()

