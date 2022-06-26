"""
File with class to solve differential equation.
"""

import time
from enum import auto, Enum
from queue import Queue
from typing import List, Tuple
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from solution.runge_kutta import RungeKutta


class SolutionMethod(Enum):
    """
    Class with methods of solution of differential equation.
    """

    EULER = auto()
    RUNGE_KUTTA = auto()


class Solver(QThread):
    """
    Class to solve differential equation.
    """

    calculation_finished: pyqtSignal = pyqtSignal(list, list)
    calculation_started: pyqtSignal = pyqtSignal(int)
    step_done: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running: bool = True
        self.task_queue: Queue = Queue()

    @pyqtSlot(int)
    def handle_start_of_calculation(self, number_of_steps: int):
        """
        Slot handles signal that calculation was started.
        :param number_of_steps: number of steps to perform calculation.
        """

        self.calculation_started.emit(number_of_steps)

    def run(self):
        while self.running:
            if self.task_queue.empty():
                time.sleep(1)
            else:
                solution_method, equation_order, coefficients, borders, limits = self.task_queue.get()
                if solution_method == SolutionMethod.RUNGE_KUTTA:
                    runge_kutta = RungeKutta(equation_order, coefficients, borders, limits)
                    runge_kutta.calculation_finished.connect(lambda xs, ys: self.calculation_finished.emit(xs, ys))
                    runge_kutta.calculation_started.connect(self.handle_start_of_calculation)
                    runge_kutta.step_done.connect(lambda: self.step_done.emit())
                    runge_kutta.solve()

    @pyqtSlot(SolutionMethod, int, list, list, tuple)
    def start_calculation(self, solution_method: SolutionMethod, equation_order: int, coefficients: List[float],
                          borders: List[float], limits: Tuple[int]):
        """
        Slot creates task to solve differential equation.
        :param solution_method: method to solve equation;
        :param equation_order: equation order;
        :param coefficients: coefficients in equation;
        :param borders: values in border equations;
        :param limits: segment in which to find solution.
        """

        self.task_queue.put([solution_method, equation_order, coefficients, borders, limits])

    def stop(self):
        self.running = False

    @pyqtSlot()
    def stop_calculation(self):
        pass
