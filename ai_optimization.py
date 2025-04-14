import pennylane as qml
import numpy as np
import networkx as nx
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import time
import random

# 🎯 Generate parking graph
def generate_parking_graph(slot_list, entry_node="Entry", exit_node="Exit"):
    graph = {entry_node: {}, exit_node: {}}
    for i, slot_id in enumerate(slot_list):
        graph[entry_node][slot_id] = 2 + i
        graph[slot_id] = {exit_node: 1}
    return graph

# 🧠 Simple real-world allocation based on weights
def real_world_allocate(slots, vehicle_type):
    weights = {
        'compact_car': 1.0,
        'sedan_car': 1.2,
        'suv_car': 1.4,
        'electric_compact_car': 1.5,
        'electric_sedan_car': 1.7,
        'electric_suv_car': 1.9,
        'motorcycle': 0.6,
        'electric_motorcycle': 0.8,
        'truck': 2.0,
        'electric_truck': 2.2
    }
    scored = [(slot, random.random() * weights.get(vehicle_type.lower(), 1)) for slot in slots]
    best_slot = sorted(scored, key=lambda x: -x[1])[0][0]
    return best_slot

# 💠 QAOA Optimization
def qaoa_optimize(slots):
    G = nx.Graph()
    for i in range(len(slots)):
        for j in range(i + 1, len(slots)):
            G.add_edge(i, j)

    n_wires = len(slots)
    dev = qml.device("default.qubit", wires=n_wires)

    def cost_layer(gamma):
        for (i, j) in G.edges:
            qml.CNOT(wires=[i, j])
            qml.RZ(-gamma, wires=j)
            qml.CNOT(wires=[i, j])

    def mixer_layer(beta):
        for i in range(n_wires):
            qml.RX(2 * beta, wires=i)

    @qml.qnode(dev)
    def circuit(gamma, beta):
        for i in range(n_wires):
            qml.Hadamard(wires=i)
        cost_layer(gamma)
        mixer_layer(beta)
        return qml.probs(wires=range(n_wires))

    def qaoa_objective(params):
        gamma, beta = params
        probs = circuit(gamma, beta)
        return -np.sum(probs)

    opt = qml.GradientDescentOptimizer(stepsize=0.1)
    params = np.array([0.5, 0.5])
    for _ in range(10):
        params = opt.step(qaoa_objective, params)

    final_probs = circuit(*params)
    best_index = np.argmax(final_probs)
    best_bitstring = format(best_index, f"0{n_wires}b")

    selected_slots = [slot for bit, slot in zip(best_bitstring, slots) if bit == '1']
    return selected_slots

# ✅ Fixed QSVM using Fidelity Kernel
def qsvm_slot_classifier(vehicle_types, labels):
    label_encoder = LabelEncoder()
    vehicle_encoded = label_encoder.fit_transform(vehicle_types)

    data = np.array([[x / 10, x / 20] for x in vehicle_encoded])

    dev = qml.device("default.qubit", wires=1)

    def feature_map(x):
        qml.RX(x[0], wires=0)
        qml.RY(x[1], wires=0)

    @qml.qnode(dev)
    def kernel_circuit(x1, x2):
        feature_map(x1)
        qml.adjoint(feature_map)(x2)
        return qml.probs(wires=0)

    def quantum_kernel(X1, X2):
        mat = np.zeros((len(X1), len(X2)))
        for i in range(len(X1)):
            for j in range(len(X2)):
                probs = kernel_circuit(X1[i], X2[j])
                fidelity = probs[0]
                mat[i][j] = fidelity
        return mat

    X = data
    classifier = SVC(kernel=quantum_kernel)
    classifier.fit(X, labels)
    preds = classifier.predict(X)
    print("Quantum SVM Predictions:", preds)
    return preds

# 🚨 CCTV unauthorized check
def detect_unauthorized_parking(assigned_slots, actual_cctv_data):
    unauthorized = []
    for slot in actual_cctv_data:
        if slot['vehicle'] not in assigned_slots:
            unauthorized.append(slot['vehicle'])
    return unauthorized

# 🧪 Benchmark: Classical Genetic Algorithm
def run_classical_optimizer(slots_count, vehicle_count):
    slots = [f"SLOT{i+1}" for i in range(slots_count)]
    assigned = []
    start = time.time()
    for _ in range(vehicle_count):
        assigned.append(real_world_allocate(slots, 'compact_car'))
    end = time.time()
    efficiency = len(set(assigned)) / slots_count
    return {
        "method": "Classical GA",
        "assigned": assigned,
        "efficiency": round(efficiency, 2),
        "time": round(end - start, 4)
    }

# 🧪 Benchmark: Quantum QAOA
def run_qaoa_optimizer(slots_count, vehicle_count):
    slots = [f"SLOT{i+1}" for i in range(slots_count)]
    start = time.time()
    assigned_slots = qaoa_optimize(slots)
    assigned = assigned_slots[:min(vehicle_count, len(assigned_slots))]
    end = time.time()
    efficiency = len(set(assigned)) / slots_count
    return {
        "method": "Quantum QAOA",
        "assigned": assigned,
        "efficiency": round(efficiency, 2),
        "time": round(end - start, 4)
    }

# 🧪 Benchmark: Quantum SVM
def run_qsvm_classifier():
    vehicle_types = ['compact_car', 'motorcycle', 'electric_compact_car', 'electric_suv_car', 'motorcycle']
    labels = [1, 0, 1, 1, 0]

    start = time.time()
    predictions = qsvm_slot_classifier(vehicle_types, labels)
    end = time.time()
    acc = accuracy_score(labels, predictions)

    return {
        "method": "Quantum SVM",
        "accuracy": round(acc, 3),
        "time": round(end - start, 4),
        "true": labels,
        "pred": predictions.tolist()
    }

# 🧪 Benchmark: Classical SVM
def run_classical_svm_classifier():
    vehicle_types = ['compact_car', 'motorcycle', 'electric_compact_car', 'electric_suv_car', 'motorcycle']
    labels = [1, 0, 1, 1, 0]

    label_encoder = LabelEncoder()
    vehicle_encoded = label_encoder.fit_transform(vehicle_types)
    data = np.array([[x / 10, x / 20] for x in vehicle_encoded])

    start = time.time()
    classifier = SVC(kernel='rbf')
    classifier.fit(data, labels)
    predictions = classifier.predict(data)
    end = time.time()
    acc = accuracy_score(labels, predictions)

    return {
        "method": "Classical SVM",
        "accuracy": round(acc, 3),
        "time": round(end - start, 4),
        "true": labels,
        "pred": predictions.tolist()
    }

# 👉 Example test
if __name__ == "__main__":
    print(run_classical_optimizer(10, 5))
    print(run_qaoa_optimizer(10, 5))
    print(run_qsvm_classifier())
    print(run_classical_svm_classifier())
