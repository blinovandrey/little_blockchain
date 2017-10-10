import blockchain
import sys
import copy
import json

BLOCK_SIZE_LIMIT = 10
TNX_BUFFER_COUNT = 200
INIT_STATE = {'Alice': 50, 'Bob': 50, 'Micle': 100, 'Frank': 80}

def make_genesis_block(state):
    genesis_block_txns = [state]
    genesis_block_contents = {
        'block_number':0,
        'parent_hash': None,
        'txn_count':1,
        'txns': genesis_block_txns
    }
    genesis_hash = blockchain.hash_me(genesis_block_contents)
    genesis_block = {'hash': genesis_hash, 'contents': genesis_block_contents}

    return genesis_block

def fill_chain(state, txn_buffer):
    while len(txn_buffer) > 0:
        txn_list = []
        while (len(txn_buffer) > 0) and (len(txn_list) < BLOCK_SIZE_LIMIT):
            new_txn = txn_buffer.pop()
            valid_txn = blockchain.is_valid_txn(new_txn, state) # This will return False if txn is invalid
            
            if valid_txn:           # If we got a valid state, not 'False'
                txn_list.append(new_txn)
                state = blockchain.update_state(new_txn, state)
            else:
                print("ignored transaction! State: {state}, transaction: {tnx}".format(
                    state=json.dumps(state), tnx=json.dumps(new_txn)))
                sys.stdout.flush()
                continue
            
        ## Make a block
        my_block = blockchain.make_block(txn_list, chain)
        chain.append(my_block)  


state = INIT_STATE  # Define the initial state
chain = [make_genesis_block(state)]
txn_buffer = [blockchain.make_transaction(state.keys()) for _ in range(TNX_BUFFER_COUNT)]
fill_chain(state, txn_buffer)
print(blockchain.check_chain(chain))

# get block from other node
other_node_chain = copy.copy(chain)
other_node_txns  = [blockchain.make_transaction(state.keys()) for i in range(5)]
new_block = blockchain.make_block(other_node_txns, other_node_chain)

print("Blockchain on Node A is currently {num} blocks long".format(num=len(chain)))

try:
    print("New Block Received; checking validity...")
    state = blockchain.check_block_validity(new_block, chain[-1], state) # Update the state- this will throw an error if the block is invalid!
    chain.append(new_block)
except:
    print("Invalid block; ignoring and waiting for the next block...")

print("Blockchain on Node A is now {num} blocks long".format(num=len(chain)))
