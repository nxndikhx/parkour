# graph_data.py

graph = {
    "ENTRY": [("A", 1), ("B", 4)],
    "A": [("ENTRY", 1), ("C", 2), ("SLOT1", 5)],
    "B": [("ENTRY", 4), ("C", 1), ("D", 3)],
    "C": [("A", 2), ("B", 1), ("D", 1)],
    "D": [("B", 3), ("C", 1), ("SLOT2", 2), ("SLOT3", 3)],
    "SLOT1": [("A", 5)],
    "SLOT2": [("D", 2)],
    "SLOT3": [("D", 3)],
}
