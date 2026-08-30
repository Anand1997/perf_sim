# SICP Digital Circuit Simulator

![Class Diagram](doc/uml_class_circuit_sim.png)
![Sequence Diagram](doc/uml_sequence_circuit_sim.png)

# Project Struct 
```cmd
digital-circuit-simulator/
├── main.rkt
├── core/
│   ├── queue.rkt
│   ├── wire.rkt
│   └── agenda.rkt
├── primitives/
│   ├── delays.rkt
│   └── gates.rkt
├── circuits/
│   ├── half-adder.rkt
│   ├── full-adder.rkt
│   └── ripple-carry-adder.rkt
├── utils/
│   ├── table.rkt
│   └── probe.rkt
└── tests/
    └── test-half-adder.rkt
```
