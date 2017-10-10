import hashlib
import json
import sys
import random

def hash_me(msg=""):
    # For convenience, this is a helper function that wraps our hashing algorithm
    if type(msg) != str:
        msg = json.dumps(msg, sort_keys=True)  # If we don't sort keys, we can't guarantee repeatability!
        
    return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()

def make_transaction(users, maxValue=10):
    # This will create valid transactions in the range of (1,maxValue)
    # sign = int(random.getrandbits(1))*2 - 1   # This will randomly choose -1 or 1
    amount = random.randint(1, maxValue)
    result = {}
    sender_index = random.randint(0, len(users) - 1)
    sender = users.pop(sender_index)
    result[sender] = -1 * amount
    receiver_index = random.randint(0, len(users) - 1)
    receiver = users.pop(receiver_index)
    result[receiver] = amount
    result.update({ user: 0 for user in users })

    return result

def update_state(txn, state):
    # Inputs: txn, state: dictionaries keyed with account names, holding numeric values for transfer amount (txn) or account balance (state)
    # Returns: Updated state, with additional users added to state if necessary
    # NOTE: This does not validate the transaction- just updates the state!
    
    # If the transaction is valid, then update the state
    state = state.copy() # As dictionaries are mutable, let's avoid any confusion by creating a working copy of the data.
    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state

def is_valid_txn(txn, state):
    # Assume that the transaction is a dictionary keyed by account names

    # Check that the sum of the deposits and withdrawals is 0
    if sum(txn.values()) is not 0:
        return False
    
    # Check that the transaction does not cause an overdraft
    for key in txn.keys():
        if key in state.keys(): 
            acc_balance = state[key]
        else:
            acc_balance = 0
        if (acc_balance + txn[key]) < 0:
            return False
    
    return True

def make_block(txns, chain):
    parent_block = chain[-1]
    parent_hash  = parent_block['hash']
    block_number = parent_block['contents']['block_number'] + 1
    txn_count = len(txns)
    block_contents = {
    	'block_number': block_number,
    	'parent_hash': parent_hash,
    	'txn_count': len(txns),
    	'txns': txns
    }
    block_hash = hash_me(block_contents)
    block = {'hash': block_hash, 'contents': block_contents}
    
    return block

def check_block_hash(block):
    # Raise an exception if the hash does not match the block contents
    expected_hash = hash_me(block['contents'])
    if block['hash'] != expected_hash:
        raise Exception('Hash does not match contents of block {num}'.format(
        	num=block['contents']['blockNumber']))
    return

def check_block_validity(block, parent, state):    
    # We want to check the following conditions:
    # - Each of the transactions are valid updates to the system state
    # - Block hash is valid for the block contents
    # - Block number increments the parent block number by 1
    # - Accurately references the parent block's hash
    parent_number = parent['contents']['block_number']
    parent_hash   = parent['hash']
    block_number  = block['contents']['block_number']
    
    # Check transaction validity; throw an error if an invalid transaction was found.
    for txn in block['contents']['txns']:
        if is_valid_txn(txn, state):
            state = update_state(txn, state)
        else:
            raise Exception('Invalid transaction in block {num}: {txn}'.format(
            	num=block_number,txn=txn))

    check_block_hash(block) # Check hash integrity; raises error if inaccurate

    if block_number != (parent_number+1):
        raise Exception('Hash does not match contents of block {num}'.format(block_number))

    if block['contents']['parent_hash'] != parent_hash:
        raise Exception('Parent hash not accurate at block {num}'.format(block_number))
    
    return state

def check_chain(chain):
    # Work through the chain from the genesis block (which gets special treatment), 
    #  checking that all transactions are internally valid,
    #    that the transactions do not cause an overdraft,
    #    and that the blocks are linked by their hashes.
    # This returns the state as a dictionary of accounts and balances,
    #   or returns False if an error was detected

    
    ## Data input processing: Make sure that our chain is a list of dicts
    if type(chain) == str:
        try:
            chain = json.loads(chain)
            assert(type(chain) == list)
        except:  # This is a catch-all, admittedly crude
            return False
    elif type(chain) != list:
        return False
    
    state = {}
    ## Prime the pump by checking the genesis block
    # We want to check the following conditions:
    # - Each of the transactions are valid updates to the system state
    # - Block hash is valid for the block contents

    for txn in chain[0]['contents']['txns']:
        state = update_state(txn, state)
    check_block_hash(chain[0])
    parent = chain[0]
    
    ## Checking subsequent blocks: These additionally need to check
    #    - the reference to the parent block's hash
    #    - the validity of the block number
    for block in chain[1:]:
        state = check_block_validity(block, parent, state)
        parent = block
        
    return state
