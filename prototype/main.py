"""
CDRS Prototype — Entry Point

Runs both example scenarios to demonstrate the full decision cycle.
"""

print("Constraint-Driven Reasoning System (CDRS)")
print("Prototype v0.1")
print("Original concept: Sami Ahmed Yusuf Kolarkar, 2026")
print()

print("Running: Overtake Decision Example")
print("-" * 40)
import prototype.examples.overtake_example

print()
print("Running: Task Scheduling Example")
print("-" * 40)
import prototype.examples.scheduling_example
