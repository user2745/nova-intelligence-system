import hashlib
import json 
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging


class ThoughtBlock:
    '''A class representing a block of thought in a thought chain.
    Each block contains a thought, its metadata, and a hash for integrity.
    '''
    def __init__(self, index: int, timestamp: str, thought_data: Dict, prev_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.thought_data = thought_data  # The actual thought record
        self.prev_hash = prev_hash
        self.hash = ""
        self.nonce = 0
        self.device_id = thought_data.get("device_id", "unknown")

    def compute_hash(self) -> str:
        '''Compute the hash of the thought block using SHA-256.'''
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.thought_data, sort_keys=True)}{self.prev_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()
    
    def mine_block(self, difficulty: int):
        '''Mine the block by finding a hash that starts with a certain number of zeros.'''
        self.hash = self.compute_hash()
        while not self.hash.startswith('0' * difficulty):
            self.nonce += 1
            self.hash = self.compute_hash()
        logging.info(f"Block {self.index} mined with hash: {self.hash} and nonce: {self.nonce}")

    def to_dict(self) -> Dict:
        """Serialize block for transmission"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "thought_data": self.thought_data,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
            "nonce": self.nonce,
            "device_id": self.device_id
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ThoughtBlock':
        """Deserialize block from received data"""
        block = cls(
            index=data['index'],
            timestamp=data['timestamp'],
            thought_data=data['thought_data'],
            prev_hash=data['prev_hash']
        )
        block.hash = data['hash']
        block.nonce = data['nonce']
        block.device_id = data.get('device_id', 'unknown')
        return block
    
    def is_valid(self, prev_block) -> bool:
        """Check if the block is valid by comparing hashes and previous hash."""
        if self.hash != self.compute_hash():
            return False
            
        # Check chain linkage
        if prev_block and self.prev_hash != prev_block.hash:
            return False
            
        # Check index sequence
        if prev_block and self.index != prev_block.index + 1:
            return False
            
        return True

class ChainOfThoughts:
    """Nova's blockchain-based consciousness chain"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.chain: List[ThoughtBlock] = []
        self.difficulty = 2  # Low difficulty for 50ms cycle
        self.create_genesis_block()
        
    def create_genesis_block(self) -> ThoughtBlock:
        """Create the first block in Nova's consciousness"""
        genesis_thought = {
            "device_id": self.device_id,
            "action": "initialize_consciousness",
            "working_memory": {"status": "nova_awakening"},
            "outcome": {"success": True, "message": "Nova consciousness initialized"},
            "emotional_state": {"mood": "curious", "stress": 0.0},
            "priority": 1.0
        }
        
        genesis_block = ThoughtBlock(
            index=0,
            timestamp=datetime.now().isoformat(),
            thought_data=genesis_thought,
            prev_hash="0"
        )
        
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        logging.info(f"🧠 Nova consciousness genesis block created: {genesis_block.hash[:8]}...")
        return genesis_block
    
    def add_thought(self, thought_record: Dict) -> bool:
        """Add a new thought to the chain (single device for now)"""
        try:
            prev_block = self.chain[-1] if self.chain else None
            prev_hash = prev_block.hash if prev_block else "0"
            
            new_block = ThoughtBlock(
                index=len(self.chain),
                timestamp=datetime.now().isoformat(),
                thought_data=thought_record,
                prev_hash=prev_hash
            )
            
            # Mine the block (with time budget for 50ms cycle)
            new_block.mine_block(self.difficulty)
            
            # Validate before adding
            if new_block.is_valid(prev_block):
                self.chain.append(new_block)
                logging.info(f"💭 Thought added to chain: {thought_record.get('device_id')} | Chain length: {len(self.chain)}")
                return True
            else:
                logging.error(f"❌ Invalid thought block rejected")
                return False
                
        except Exception as e:
            logging.error(f"💥 Error adding thought to chain: {str(e)}")
            return False
    
    def get_recent_thoughts(self, count: int = 10) -> List[ThoughtBlock]:
        """Get the most recent thoughts"""
        return self.chain[-count:] if len(self.chain) >= count else self.chain
    
    def get_thought_by_index(self, index: int) -> Optional[ThoughtBlock]:
        """Get specific thought by chain index"""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def query_thoughts_by_action(self, action: str, limit: int = 10) -> List[ThoughtBlock]:
        """Find thoughts by action type"""
        matching_thoughts = []
        for block in reversed(self.chain):
            if block.thought_data.get("action") == action:
                matching_thoughts.append(block)
                if len(matching_thoughts) >= limit:
                    break
        return matching_thoughts
    
    def get_chain_length(self) -> int:
        """Get current chain length"""
        return len(self.chain)
    
    def validate_chain(self) -> bool:
        """Validate entire chain integrity"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i-1]
            
            if not current_block.is_valid(prev_block):
                logging.error(f"❌ Chain validation failed at block {i}")
                return False
                
        logging.info(f"✅ Chain validation passed ({len(self.chain)} blocks)")
        return True
    
    def save_chain(self, filepath: str):
        """Save chain to disk"""
        try:
            chain_data = [block.to_dict() for block in self.chain]
            with open(filepath, 'w') as f:
                json.dump(chain_data, f, indent=2)
            logging.info(f"💾 Chain saved to {filepath}")
        except Exception as e:
            logging.error(f"💥 Error saving chain: {str(e)}")
    
    def load_chain(self, filepath: str) -> bool:
        """Load chain from disk"""
        try:
            with open(filepath, 'r') as f:
                chain_data = json.load(f)
            
            self.chain = [ThoughtBlock.from_dict(block_data) for block_data in chain_data]
            
            if self.validate_chain():
                logging.info(f"📖 Chain loaded from {filepath} ({len(self.chain)} blocks)")
                return True
            else:
                logging.error(f"❌ Loaded chain failed validation")
                self.chain = []
                self.create_genesis_block()
                return False
                
        except FileNotFoundError:
            logging.info(f"📝 No existing chain found, starting fresh")
            return False
        except Exception as e:
            logging.error(f"💥 Error loading chain: {str(e)}")
            return False