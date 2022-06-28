"""
File with main solver of differential equation.
"""

import time
from enum import auto, Enum
from typing import List, Tuple
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from solution.runge_kutta import RungeKutta


class SolutionMethod(Enum):
    """
    Class with methods of solution of differential equation.
    """

    EULER = auto()
    RUNGE_KUTTA = auto()


class Solver(QObject):
    """
    Class to solve differential equation.
    """

    MAX_NUMBER_OF_POINTS: int = 100
    MAX_NUMBER_OF_ITERATIONS: int = 20
    calculation_finished: pyqtSignal = pyqtSignal()
    calculation_for_step_finished: pyqtSignal = pyqtSignal(list, list, float)
    calculation_for_step_started: pyqtSignal = pyqtSignal(int, float)
    calculation_started: pyqtSignal = pyqtSignal(list, list)
    max_iterations_used: pyqtSignal = pyqtSignal(int)
    segment_done: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.accuracy: float = -1
        self.calculation_stopped: bool = False
        self.runge_kutta: RungeKutta = RungeKutta()
        self.solver: RungeKutta = None
        self.xs: List[float] = None
        self.ys: List[List[float]] = None

    @staticmethod
    def analyze_input_data(coefficients: List[float], borders: List[float]) -> Tuple[List[float], List[float]]:
        """
        Method analyzes input data of equation and determines order of equation.
        :param coefficients: coefficients in equation;
        :param borders: values in border equations.
        :return: correct coefficients in equation and values in border equations.
        """

        for index in range(len(coefficients) - 1, -1, -1):
            if coefficients[index] != 0:
                break
            coefficients.pop(index)
            borders.pop(index - 1)
        return coefficients, borders

    @pyqtSlot(SolutionMethod, float, list, float, list, tuple)
    def start_calculation(self, solution_method: SolutionMethod, accuracy: float, coefficients: List[float],
                          free_argument: float, borders: List[float], limits: Tuple[int]):
        """
        Slot creates task to solve differential equation.
        :param solution_method: method to solve equation;
        :param accuracy: required solution accuracy;
        :param coefficients: coefficients in equation;
        :param free_argument: free argument in equation;
        :param borders: values in border equations;
        :param limits: segment in which to find solution.
        """

        self.accuracy = accuracy
        self.calculation_stopped = False
        coefficients, borders = self.analyze_input_data(coefficients, borders)
        self.calculation_started.emit(coefficients, borders)
        if solution_method == SolutionMethod.RUNGE_KUTTA:
            self.solver = self.runge_kutta
        self.solver.set_data(coefficients, free_argument, borders, limits, self.segment_done,
                             self.calculation_for_step_started)
        while not self.calculation_stopped:
            iteration_number, current_accuracy, self.xs, self.ys = self.solver.solve()
            number = len(self.xs)
            points_number = number if number < self.MAX_NUMBER_OF_POINTS else self.MAX_NUMBER_OF_POINTS
            d_number = round(number / points_number)
            self.calculation_for_step_finished.emit(self.xs[::d_number], self.ys[::d_number], current_accuracy)
            if current_accuracy != -1 and current_accuracy <= self.accuracy:
                self.calculation_finished.emit()
                break
            if iteration_number > self.MAX_NUMBER_OF_POINTS:
                self.max_iterations_used.emit(self.MAX_NUMBER_OF_POINTS)
                break
            time.sleep(0.2)
