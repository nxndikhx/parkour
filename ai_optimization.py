import random

# 🎯 Default sample graph (optional if you're generating dynamically)
graph = {
    "Entry": {"SLOT1": 2, "SLOT2": 3, "SLOT3": 4},
    "SLOT1": {"Exit": 1},
    "SLOT2": {"Exit": 1},
    "SLOT3": {"Exit": 1},
    "Exit": {}
}

# 🧠 Quantum DQN simulation
def quantum_dqn_allocate(slots, vehicle_type):
    weights = {'car': 1.0, 'bike': 0.6, 'ev': 1.2}
    scored = [(slot, random.random() * weights.get(vehicle_type.lower(), 1)) for slot in slots]
    best_slot = sorted(scored, key=lambda x: -x[1])[0][0]
    return best_slot

# 🧬 QAOA simulation
def qaoa_optimize(slots):
    # Example: return top 50% best slots based on alphabetical order
    return sorted(slots)[:len(slots) // 2]

# 🧬 Genetic Algorithm simulation
def genetic_slot_assignment(slots, vehicle_type):
    # Random choice simulation for now
    return random.choice(slots)

# 🚨 CNN-like unauthorized parking detection
def detect_unauthorized_parking(assigned_slots, actual_cctv_data):
    unauthorized = []
    for slot in actual_cctv_data:
        if slot['vehicle'] not in assigned_slots:
            unauthorized.append(slot['vehicle'])
    return unauthorized

# 🧭 Auto-generate weighted graph from slot list
def generate_parking_graph(slot_list, entry_node="Entry", exit_node="Exit"):
    """
    Generates a weighted directed graph for navigation based on slot IDs.
    Format:
    {
        "Entry": {"SLOT1": 2, "SLOT2": 3, ...},
        "SLOT1": {"Exit": 1},
        "SLOT2": {"Exit": 1},
        ...
        "Exit": {}
    }
    """
    graph = {entry_node: {}, exit_node: {}}

    for i, slot_id in enumerate(slot_list):
        graph[entry_node][slot_id] = 2 + i  # Entry → SLOTx with increasing weight
        graph[slot_id] = {exit_node: 1}     # SLOTx → Exit

    return graph
