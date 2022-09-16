from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class SimulationResult:

    @abstractmethod
    def display(self) -> str:
        ...


@dataclass
class Simulation:

    @abstractmethod
    def simulate(self) -> SimulationResult:
        ...
