"""
File with class for main window of application.
"""

import os
from typing import List
import matplotlib.pyplot as plt
import PyQt5.QtWidgets as qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRegExp, Qt
from PyQt5.QtGui import QIcon, QRegExpValidator
import gui.utils as ut
from solution import SolutionMethod, Solver


class MainWindow(qt.QMainWindow):
    """
    Class for main window of application.
    """

    DEFAULT_BORDERS = [0, -8, -9, 3, 0]
    DEFAULT_COEFFICIENTS = [1, 15, 90, 270, 405, 243, 0]
    DEFAULT_EQUATION_ORDER: int = 5
    DEFAULT_MAX_X: int = 5
    DEFAULT_MIN_X: int = 0
    MAX_EQUATION_ORDER: int = 10
    MAX_LINE_EDIT_WIDTH: int = 50
    MAX_X: int = 100
    MIN_SCROLL_AREA_HEIGHT: int = 150
    MIN_X: int = -100
    solution_started: pyqtSignal = pyqtSignal(SolutionMethod, int, list, list, tuple)
    solution_stopped: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._dir_name: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
        self._dir_name_for_save: str = self._dir_name
        self._equation_order: int = 1
        self._solver: Solver = None
        self._xs: List[float] = []
        self._ys: List[float] = []
        self.button_save_figure: qt.QPushButton = None
        self.button_save_result: qt.QPushButton = None
        self.button_set_equation_order: qt.QPushButton = None
        self.button_solve: qt.QPushButton = None
        self.figure = plt.figure()
        self.figure_canvas: FigureCanvas = None
        self.line_edits_borders: List[qt.QLineEdit] = []
        self.line_edits_coefficients: List[qt.QLineEdit] = []
        self.progress_bar: qt.QProgressBar = None
        self.scroll_area: qt.QScrollArea = None
        self.spin_box_equation_order: qt.QSpinBox = None
        self.spin_box_x_max: qt.QSpinBox = None
        self.spin_box_x_min: qt.QSpinBox = None
        self._init_ui()
        self._start_solver()

    def _init_scroll_area(self, equation_order: int):
        """
        Method initializes scroll area.
        """

        self._equation_order = equation_order
        widget = self.scroll_area.widget()
        del widget
        h_layout_1 = qt.QHBoxLayout()
        h_layout_2 = qt.QHBoxLayout()
        validator = QRegExpValidator(QRegExp(r"-?\d+\.?(\d+)?"))
        self.line_edits_borders.clear()
        self.line_edits_coefficients.clear()
        for index in range(equation_order, -1, -1):
            line_edit = qt.QLineEdit()
            line_edit.setMaximumWidth(self.MAX_LINE_EDIT_WIDTH)
            line_edit.setValidator(validator)
            self.line_edits_coefficients.append(line_edit)
            if index != equation_order:
                h_layout_1.addWidget(qt.QLabel("+"))
            h_layout_1.addWidget(line_edit)
            if index > 0:
                h_layout_1.addWidget(qt.QLabel(f"dy<sup>{index}</sup>/dx<sup>{index}</sup>"))
            else:
                h_layout_1.addWidget(qt.QLabel("y"))
            if index == equation_order:
                continue
            line_edit = qt.QLineEdit()
            line_edit.setMaximumWidth(self.MAX_LINE_EDIT_WIDTH)
            line_edit.setValidator(validator)
            self.line_edits_borders.append(line_edit)
            if 0 < index < equation_order:
                h_layout_2.addWidget(qt.QLabel(f"dy<sup>{index}</sup>/dx<sup>{index}</sup>"
                                               f"({self.spin_box_x_min.value()})="))
                h_layout_2.addWidget(line_edit)
                h_layout_2.addWidget(qt.QLabel(", "))
            elif index == 0:
                h_layout_2.addWidget(qt.QLabel(f"y({self.spin_box_x_min.value()})="))
                h_layout_2.addWidget(line_edit)
        h_layout_1.addWidget(qt.QLabel("="))
        line_edit = qt.QLineEdit()
        line_edit.setMaximumWidth(self.MAX_LINE_EDIT_WIDTH)
        line_edit.setValidator(validator)
        self.line_edits_coefficients.append(line_edit)
        h_layout_1.addWidget(line_edit)
        h_layout_1.addStretch(1)
        h_layout_2.addStretch(1)
        v_layout = qt.QVBoxLayout()
        v_layout.addLayout(h_layout_1)
        v_layout.addLayout(h_layout_2)
        v_layout.addStretch(1)
        widget = qt.QWidget()
        widget.setMinimumHeight(self.MIN_SCROLL_AREA_HEIGHT)
        widget.setLayout(v_layout)
        self.scroll_area.setWidget(widget)

    def _init_ui(self):
        """
        Method initializes widgets on main window.
        """

        self.setWindowTitle("Решатель дифференциальных уравений")
        self.setWindowIcon(QIcon(os.path.join(self._dir_name, "icon.png")))
        self.spin_box_equation_order = qt.QSpinBox()
        self.spin_box_equation_order.setMinimumWidth(self.MAX_LINE_EDIT_WIDTH)
        self.spin_box_equation_order.setMinimum(1)
        self.spin_box_equation_order.setMaximum(self.MAX_EQUATION_ORDER)
        form_layout = qt.QFormLayout()
        form_layout.addRow(qt.QLabel("Порядок уравнения"), self.spin_box_equation_order)
        self.button_set_equation_order = qt.QPushButton("Задать порядок уравнения")
        self.button_set_equation_order.setToolTip("Задать порядок уравнения")
        self.button_set_equation_order.clicked.connect(self.set_equation_order)
        h_layout = qt.QHBoxLayout()
        h_layout.addLayout(form_layout)
        h_layout.addWidget(self.button_set_equation_order, alignment=Qt.AlignmentFlag.AlignTop)
        h_layout.addStretch(1)
        self.scroll_area = qt.QScrollArea()
        self.spin_box_x_min = qt.QSpinBox()
        self.spin_box_x_min.setMinimumWidth(self.MAX_LINE_EDIT_WIDTH)
        self.spin_box_x_min.setMinimum(self.MIN_X)
        self.spin_box_x_min.setMaximum(self.MAX_X)
        self.spin_box_x_min.valueChanged.connect(self.check_limits)
        form_layout_min = qt.QFormLayout()
        form_layout_min.addRow(qt.QLabel("x<sub>min</sub>"), self.spin_box_x_min)
        self.spin_box_x_max = qt.QSpinBox()
        self.spin_box_x_max.setMinimumWidth(self.MAX_LINE_EDIT_WIDTH)
        self.spin_box_x_max.setMinimum(self.MIN_X)
        self.spin_box_x_max.setMaximum(self.MAX_X)
        self.spin_box_x_max.valueChanged.connect(self.check_limits)
        form_layout_max = qt.QFormLayout()
        form_layout_max.addRow(qt.QLabel("x<sub>max</sub>"), self.spin_box_x_max)
        self.button_solve = qt.QPushButton("Решить уравнение")
        self.button_solve.setToolTip("Решить уравнение")
        self.button_solve.clicked.connect(self.solve)
        self.button_save_figure = qt.QPushButton("Сохранить график")
        self.button_save_figure.setToolTip("Сохранить график")
        self.button_save_figure.clicked.connect(self.save_figure)
        self.button_save_result = qt.QPushButton("Сохранить числовое решение")
        self.button_save_result.setToolTip("Сохранить числовое решение")
        self.button_save_result.clicked.connect(self.save_result)
        h_layout_2 = qt.QHBoxLayout()
        h_layout_2.addLayout(form_layout_min)
        h_layout_2.addLayout(form_layout_max)
        h_layout_2.addWidget(self.button_solve)
        h_layout_2.addWidget(self.button_save_figure)
        h_layout_2.addWidget(self.button_save_result)
        h_layout_2.addStretch(1)
        group_box_params = qt.QGroupBox("Параметры уравнения")
        v_layout = qt.QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.scroll_area)
        v_layout.addLayout(h_layout_2)
        v_layout.addStretch(1)
        group_box_params.setLayout(v_layout)
        self.figure_canvas = FigureCanvas(self.figure)
        self.progress_bar = qt.QProgressBar()
        self.progress_bar.setVisible(False)
        v_layout = qt.QVBoxLayout()
        v_layout.addWidget(group_box_params)
        v_layout.addWidget(self.figure_canvas, 1)
        v_layout.addWidget(self.progress_bar)
        widget = qt.QWidget()
        widget.setLayout(v_layout)
        self.setCentralWidget(widget)
        self._set_default_params()

    def _set_default_params(self):
        """
        Method sets default parameters for equation.
        """

        self.spin_box_equation_order.setValue(self.DEFAULT_EQUATION_ORDER)
        self.spin_box_x_max.setValue(self.DEFAULT_MAX_X)
        self.spin_box_x_min.setValue(self.DEFAULT_MIN_X)
        self._init_scroll_area(self.DEFAULT_EQUATION_ORDER)
        for index, default_value in enumerate(self.DEFAULT_COEFFICIENTS):
            self.line_edits_coefficients[index].setText(str(default_value))
        for index, default_value in enumerate(self.DEFAULT_BORDERS):
            self.line_edits_borders[index].setText(str(default_value))

    def _start_solver(self):
        """
        Method starts solver.
        """

        self._solver = Solver()
        self.solution_started.connect(self._solver.start_calculation)
        self.solution_stopped.connect(self._solver.stop_calculation)
        self._solver.calculation_finished.connect(self.handle_finish_of_calculation)
        self._solver.calculation_started.connect(self.handle_start_of_calculation)
        self._solver.step_done.connect(self.handle_step_done)
        self._solver.start()

    @pyqtSlot(int)
    def check_limits(self, new_limit: int):
        """
        Method checks limits.
        :param new_limit: new limit value.
        """

        if self.sender() == self.spin_box_x_min and new_limit >= self.spin_box_x_max.value():
            self.spin_box_x_min.setValue(self.spin_box_x_max.value() - 1)
        elif self.sender() == self.spin_box_x_max and new_limit <= self.spin_box_x_min.value():
            self.spin_box_x_max.setValue(self.spin_box_x_min.value() + 1)

    @pyqtSlot(list, list)
    def handle_finish_of_calculation(self, xs: List[float], ys: List[float]):
        """
        Slot handles signal that calculation was finished.
        :param xs: list with x coordinates;
        :param ys: list with y coordinates.
        """

        self._xs, self._ys = xs, ys
        self.progress_bar.setVisible(False)
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(xs, ys, color="blue")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        self.figure_canvas.draw()

    @pyqtSlot(int)
    def handle_start_of_calculation(self, number_of_steps: int):
        """
        Slot handles signal that calculation was started.
        :param number_of_steps: number of steps to perform calculation.
        """

        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(number_of_steps)
        self.progress_bar.setVisible(True)

    @pyqtSlot()
    def handle_step_done(self):
        """
        Slot handles signal that
        """

        self.progress_bar.setValue(self.progress_bar.value() + 1)

    @pyqtSlot()
    def save_figure(self):
        """
        Slot saves figure.
        """

        if not self._xs:
            qt.QMessageBox.information(self, "Информация", "Нет графика")
            return
        file_name = os.path.join(self._dir_name_for_save, ut.create_file_name(".png"))
        file_name = qt.QFileDialog.getSaveFileName(self, "Сохранить график в файл", directory=file_name,
                                                   filter="Image files (*.png *.jpg)")[0]
        if file_name:
            self._dir_name_for_save = os.path.dirname(file_name)
            self.figure.savefig(file_name)

    @pyqtSlot()
    def save_result(self):
        """
        Slot saves solution of equation.
        """

        if not self._xs:
            qt.QMessageBox.information(self, "Информация", "Нет решения")
            return
        file_name = os.path.join(self._dir_name_for_save, ut.create_file_name(".txt"))
        file_name = qt.QFileDialog.getSaveFileName(self, "Сохранить решение в файл", directory=file_name,
                                                   filter="Text files (*.xlsx *.txt)")[0]
        if file_name:
            self._dir_name_for_save = os.path.dirname(file_name)
            extension = os.path.splitext(file_name)[-1]
            if extension == ".xlsx":
                ut.save_data_to_excel(file_name, self._xs, self._ys)
            else:
                ut.save_data_to_txt(file_name, self._xs, self._ys)

    @pyqtSlot()
    def set_equation_order(self):
        """
        Method sets equation order.
        """

        equation_order = self.spin_box_equation_order.value()
        if equation_order != self._equation_order:
            self._init_scroll_area(equation_order)

    @pyqtSlot()
    def solve(self):
        """
        Method solves equation.
        """

        if all([line_edit.hasAcceptableInput() for line_edit in self.line_edits_coefficients]) and\
                all([line_edit.hasAcceptableInput() for line_edit in self.line_edits_borders]) and\
                self.spin_box_x_max.hasAcceptableInput() and self.spin_box_x_min.hasAcceptableInput():
            borders = [float(line_edit.text()) for line_edit in self.line_edits_borders]
            coefficients = [float(line_edit.text()) for line_edit in self.line_edits_coefficients]
            limits = self.spin_box_x_min.value(), self.spin_box_x_max.value()
            self.solution_started.emit(SolutionMethod.RUNGE_KUTTA, self._equation_order, coefficients, borders, limits)
        else:
            qt.QMessageBox.warning(self, "Предупреждение", "Введите все значения коэффициентов в уравнении и граничные"
                                                           " значения")
