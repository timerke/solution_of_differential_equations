"""
File with solver to solve differential equation by Runge-Kutta method.
"""

import math
from typing import List, Tuple
from PyQt5.QtCore import pyqtSignal


class RungeKutta:
    """
    Class to solve differential equation by Runge-Kutta method.
    """

    INITIAL_STEP: float = 0.1

    def __init__(self):
        self._borders: List[float] = []
        self._calculation_for_step_started_signal: pyqtSignal = None
        self._coefficients: List[float] = []
        self._equation_order: int = None
        self._free_argument: float = None
        self._iteration_number: int = 1
        self._max_x: int = None
        self._min_x: int = None
        self._segment_done_signal: pyqtSignal = None
        self._step: float = self.INITIAL_STEP
        self._variables: List[List[float]] = []

    def _calculate_k_1(self, variables: List[List[float]]) -> List[float]:
        return [self._function_for_variable(index_of_variable, variables[-1]) for index_of_variable in
                range(len(variables[-1]))]

    def _calculate_k_2(self, step: float, k_1: List[float], variables: List[List[float]]) -> List[float]:
        variables_for_x = [variable + k_1[index_of_variable] * step / 2 for index_of_variable, variable in
                           enumerate(variables[-1])]
        return [self._function_for_variable(index_of_variable, variables_for_x) for index_of_variable in
                range(len(variables[-1]))]

    def _calculate_k_3(self, step: float, k_2: List[float], variables: List[List[float]]) -> List[float]:
        variables_for_x = [variable + k_2[index_of_variable] * step / 2 for index_of_variable, variable in
                           enumerate(variables[-1])]
        return [self._function_for_variable(index_of_variable, variables_for_x) for index_of_variable in
                range(len(variables[-1]))]

    def _calculate_k_4(self, step: float, k_3: List[float], variables: List[List[float]]) -> List[float]:
        variables_for_x = [variable + k_3[index_of_variable] * step for index_of_variable, variable in
                           enumerate(variables[-1])]
        return [self._function_for_variable(index_of_variable, variables_for_x) for index_of_variable in
                range(len(variables[-1]))]

    @staticmethod
    def _check_accuracy(variables_for_step: List[List[float]], variables_for_2step: List[List[float]]) -> float:
        """
        Method calculates accuracy of solution.
        :param variables_for_step: solution for step;
        :param variables_for_2step: solution for double step.
        :return: accuracy of solution.
        """

        max_difference = None
        for index in range(len(variables_for_2step)):
            if 2 * index >= len(variables_for_step):
                break
            accuracy = math.fabs(variables_for_2step[index][0] - variables_for_step[2 * index][0]) / 15
            if max_difference is None or max_difference < accuracy:
                max_difference = accuracy
        return max_difference

    def _function_for_highest_derivative(self, variables: List[float]) -> float:
        return self._free_argument - sum([self._coefficients[index] * variable for index, variable in
                                          enumerate(variables)]) / self._coefficients[-1]

    @staticmethod
    def _function_for_rest_derivatives(index_of_variable: int, variables: List[float]) -> float:
        return variables[index_of_variable + 1]

    def _function_for_variable(self, index_of_variable: int, variables: List[float]) -> float:
        if index_of_variable == self._equation_order - 1:
            return self._function_for_highest_derivative(variables)
        return self._function_for_rest_derivatives(index_of_variable, variables)

    def _solve_for_step(self, step: float) -> Tuple[List[float], List[List[float]]]:
        """
        Method solves equation for given step.
        :param step: step.
        :return: solution.
        """

        x = self._min_x
        variables = [self._borders[:]]
        xs = [x]
        progress = 0
        number_of_segments = math.ceil((self._max_x - self._min_x) / self._step) + 1
        while x <= self._max_x:
            k_1 = self._calculate_k_1(variables)
            k_2 = self._calculate_k_2(step, k_1, variables)
            k_3 = self._calculate_k_3(step, k_2, variables)
            k_4 = self._calculate_k_4(step, k_3, variables)
            variables_for_x = [variable + 1 / 6 * step * (k_1[index] + 2 * k_2[index] + 2 * k_3[index] + k_4[index])
                               for index, variable in enumerate(variables[-1])]
            variables.append(variables_for_x)
            x += step
            xs.append(x)
            current_progress = round(100 * len(xs) / number_of_segments)
            if current_progress != progress:
                progress = current_progress
                self._segment_done_signal.emit()
        return xs, variables

    def set_data(self, coefficients: List[float], free_argument: float, borders: List[float], limits: Tuple[int],
                 segment_done_signal: pyqtSignal, calculation_for_step_started_signal: pyqtSignal):
        """
        Method sets new params for equation to solve.
        :param coefficients: coefficients of equation;
        :param free_argument: free argument of equation;
        :param borders: values of border equations;
        :param limits: segment in which to find solution;
        :param segment_done_signal: signal for event that equation was integrated
        on dx segment;
        :param calculation_for_step_started_signal: signal for event that
        equation was integrated on all segment with given step.
        """

        self._borders = borders
        self._calculation_for_step_started_signal = calculation_for_step_started_signal
        self._coefficients = coefficients
        self._equation_order: int = len(coefficients) - 1
        self._free_argument = free_argument
        self._iteration_number = 0
        self._min_x, self._max_x = limits
        self._step = 2 * self.INITIAL_STEP
        self._segment_done_signal = segment_done_signal

    def solve(self) -> Tuple[int, float, List[float], List[List[float]]]:
        """
        Method solves equation.
        :return: accuracy of calculation.
        """

        self._iteration_number += 1
        self._step /= 2
        self._calculation_for_step_started_signal.emit(self._iteration_number, self._step)
        xs, variables = self._solve_for_step(self._step)
        if self._variables:
            accuracy = self._check_accuracy(variables, self._variables)
        else:
            accuracy = -1
        self._variables = variables
        return self._iteration_number, accuracy, xs, variables
