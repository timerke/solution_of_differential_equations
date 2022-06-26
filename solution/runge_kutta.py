"""
File with functions to solve differential equation by Runge-Kutta method.
"""

import math
from typing import List, Tuple
from PyQt5.QtCore import pyqtSignal, QObject


class RungeKutta(QObject):
    """
    Class to solve differential equation by Runge-Kutta method.
    """

    INITIAL_STEP: float = 0.1
    calculation_finished: pyqtSignal = pyqtSignal(list, list)
    calculation_started: pyqtSignal = pyqtSignal(int)
    step_done: pyqtSignal = pyqtSignal()

    def __init__(self, equation_order: int, coefficients: List[float], borders: List[float], limits: Tuple[int]):
        """
        :param equation_order: equation order;
        :param coefficients: coefficients of equation;
        :param borders: values of border equations;
        :param limits: segment in which to find solution.
        """

        super().__init__()
        self._borders: List[float] = borders
        self._coefficients: List[float] = coefficients
        self._equation_order: int = equation_order
        self._max_x: int = limits[1]
        self._min_x: int = limits[0]
        self._variables: List[List[float]] = []

    def _calculate_k_1(self) -> List[float]:
        return [self._function_for_variable(index_of_variable, self._variables[-1]) for index_of_variable in
                range(len(self._variables[-1]))]

    def _calculate_k_2(self, step: float, k_1: List[float]) -> List[float]:
        variables = [variable + k_1[index_of_variable] * step / 2 for index_of_variable, variable in
                     enumerate(self._variables[-1])]
        return [self._function_for_variable(index_of_variable, variables) for index_of_variable in
                range(len(self._variables[-1]))]

    def _calculate_k_3(self, step: float, k_2: List[float]) -> List[float]:
        variables = [variable + k_2[index_of_variable] * step / 2 for index_of_variable, variable in
                     enumerate(self._variables[-1])]
        return [self._function_for_variable(index_of_variable, variables) for index_of_variable in
                range(len(self._variables[-1]))]

    def _calculate_k_4(self, step: float, k_3: List[float]) -> List[float]:
        variables = [variable + k_3[index_of_variable] * step for index_of_variable, variable in
                     enumerate(self._variables[-1])]
        return [self._function_for_variable(index_of_variable, variables) for index_of_variable in
                range(len(self._variables[-1]))]

    def _function_for_highest_derivative(self, variables: List[float]) -> float:
        return self._coefficients[-1] - sum([self._coefficients[index + 1] * variable for index, variable in
                                             enumerate(variables)]) / self._coefficients[0]

    @staticmethod
    def _function_for_rest_derivatives(index_of_variable: int, variables: List[float]) -> float:
        return variables[index_of_variable - 1]

    def _function_for_variable(self, index_of_variable: int, variables: List[float]) -> float:
        if index_of_variable == 0:
            return self._function_for_highest_derivative(variables)
        return self._function_for_rest_derivatives(index_of_variable, variables)

    def solve(self):
        """
        Method solves equation.
        """

        step = self.INITIAL_STEP
        self.calculation_started.emit(math.ceil((self._max_x - self._min_x) / step))
        x = self._min_x
        variables = []
        for d_index in range(self._equation_order - 1):
            if d_index == 0:
                value = self._function_for_highest_derivative(self._borders)
            else:
                value = self._function_for_rest_derivatives(d_index, self._borders)
            variables.append(value)
        self._variables.append(variables)
        xs = [x]
        while x <= self._max_x:
            k_1 = self._calculate_k_1()
            k_2 = self._calculate_k_2(step, k_1)
            k_3 = self._calculate_k_3(step, k_2)
            k_4 = self._calculate_k_4(step, k_3)
            variables = [variable + 1 / 6 * step * (k_1[index] + 2 * k_2[index] + 2 * k_3[index] + k_4[index])
                         for index, variable in enumerate(self._variables[-1])]
            self._variables.append(variables)
            x += step
            xs.append(x)
            self.step_done.emit()
        self.calculation_finished.emit(xs, [variables[-1] for variables in self._variables])
