"""
File with class for main window of application.
"""

import os
from typing import List
import matplotlib.pyplot as plt
import PyQt5.QtWidgets as qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRegExp, Qt, QThread
from PyQt5.QtGui import QCloseEvent, QIcon, QRegExpValidator
import gui.utils as ut
from gui.label import Label
from gui.text_edit import TextEdit
from solution import SolutionMethod, Solver


class MainWindow(qt.QMainWindow):
    """
    Class for main window of application.
    """

    MAX_EQUATION_ORDER: int = 20
    DEFAULT_ACCURACY: float = 0.00001
    DEFAULT_BORDERS: List[float] = [0, 3, -9, -8, 0] + [0] * (MAX_EQUATION_ORDER - 5)
    DEFAULT_COEFFICIENTS: List[float] = [243, 405, 270, 90, 15, 1] + [0] * (MAX_EQUATION_ORDER + 1 - 6)
    DEFAULT_EQUATION_ORDER: int = 5
    DEFAULT_FREE_ARGUMENT: float = 0
    DEFAULT_MAX_X: int = 5
    DEFAULT_MIN_X: int = 0
    MAX_LINE_EDIT_WIDTH: int = 50
    MAX_TEXT_EDIT_HEIGHT: int = 100
    MAX_X: int = 100
    MIN_COMBO_BOX_WIDTH: int = 100
    MIN_SCROLL_AREA_HEIGHT: int = 150
    MIN_SPIN_BOX_WIDTH: int = 50
    MIN_X: int = -100
    calculation_started: pyqtSignal = pyqtSignal(SolutionMethod, float, list, float, list, tuple)
    calculation_stopped: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._borders: List[float] = self.DEFAULT_BORDERS
        self._coefficients: List[float] = self.DEFAULT_COEFFICIENTS
        self._dir_name: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
        self._dir_name_for_save: str = ut.get_dir_name()
        self._equation_order: int = self.DEFAULT_EQUATION_ORDER
        self._free_argument: float = self.DEFAULT_FREE_ARGUMENT
        self._max_x: int = self.DEFAULT_MAX_X
        self._min_x: int = self.DEFAULT_MIN_X
        self._solver: Solver = None
        self._solver_thread: QThread = None
        self._xs: List[float] = []
        self._ys: List[List[float]] = []
        self.button_save_figure: qt.QPushButton = None
        self.button_save_result: qt.QPushButton = None
        self.button_set_equation_order: qt.QPushButton = None
        self.button_solve: qt.QPushButton = None
        self.combo_box_graph: qt.QComboBox = None
        self.figure = plt.figure()
        self.figure_canvas: FigureCanvas = None
        self.labels_borders: List[Label] = []
        self.labels_commas: List[qt.QLabel] = []
        self.labels_dydxs: List[qt.QLabel] = []
        self.labels_pluses: List[qt.QLabel] = []
        self.line_edit_accuracy: qt.QLineEdit = None
        self.line_edit_free_argument: qt.QLineEdit = None
        self.line_edits_borders: List[qt.QLineEdit] = []
        self.line_edits_coefficients: List[qt.QLineEdit] = []
        self.progress_bar: qt.QProgressBar = None
        self.scroll_area: qt.QScrollArea = None
        self.spin_box_equation_order: qt.QSpinBox = None
        self.spin_box_x_max: qt.QSpinBox = None
        self.spin_box_x_min: qt.QSpinBox = None
        self.text_edit: TextEdit = None
        self._init_ui()
        self._start_thread()

    def _clear_graph(self):
        self._xs.clear()
        self._ys.clear()
        self.show_graph(self.combo_box_graph.currentIndex())

    def _enable_widgets(self, enable: bool):
        """
        Method enables and disables some widgets.
        :param enable: if True then widgets will be enabled.
        """

        widgets = (self.button_save_figure, self.button_save_result, self.button_set_equation_order, self.button_solve,
                   self.line_edit_accuracy, self.spin_box_equation_order, self.scroll_area)
        for widget in widgets:
            widget.setEnabled(enable)

    def _init_scroll_area(self) -> qt.QScrollArea:
        """
        Method initializes scroll area with parameters of differential equation.
        :return: scroll area widget.
        """

        h_layout_1 = qt.QHBoxLayout()
        h_layout_2 = qt.QHBoxLayout()
        validator = QRegExpValidator(QRegExp(r"-?\d+\.?(\d+)?"))
        self.labels_borders = []
        self.labels_commas = []
        self.labels_dydxs = []
        self.labels_pluses = []
        self.line_edits_borders = []
        self.line_edits_coefficients = []
        self.spin_box_x_min = qt.QSpinBox()
        self.spin_box_x_min.setMinimumWidth(self.MIN_SPIN_BOX_WIDTH)
        self.spin_box_x_min.setMinimum(self.MIN_X)
        self.spin_box_x_min.setMaximum(self.MAX_X)
        self.spin_box_x_min.valueChanged.connect(self.check_limits)
        form_layout_min = qt.QFormLayout()
        form_layout_min.addRow(qt.QLabel("x<sub>min</sub>"), self.spin_box_x_min)
        self.spin_box_x_max = qt.QSpinBox()
        self.spin_box_x_max.setMinimumWidth(self.MIN_SPIN_BOX_WIDTH)
        self.spin_box_x_max.setMinimum(self.MIN_X)
        self.spin_box_x_max.setMaximum(self.MAX_X)
        self.spin_box_x_max.valueChanged.connect(self.check_limits)
        form_layout_max = qt.QFormLayout()
        form_layout_max.addRow(qt.QLabel("x<sub>max</sub>"), self.spin_box_x_max)
        for index in range(self.MAX_EQUATION_ORDER, -1, -1):
            if index != self.MAX_EQUATION_ORDER:
                label = qt.QLabel("+")
                if self.labels_pluses:
                    self.labels_pluses.insert(0, label)
                else:
                    self.labels_pluses.append(label)
                h_layout_1.addWidget(label)
            line_edit = qt.QLineEdit()
            line_edit.setMaximumWidth(self.MAX_LINE_EDIT_WIDTH)
            line_edit.setValidator(validator)
            if self.line_edits_coefficients:
                self.line_edits_coefficients.insert(0, line_edit)
            else:
                self.line_edits_coefficients.append(line_edit)
            h_layout_1.addWidget(line_edit)
            if index > 0:
                label = qt.QLabel(f"dy<sup>{index}</sup>/dx<sup>{index}</sup>")
                h_layout_1.addWidget(label)
            else:
                label = qt.QLabel("y")
                h_layout_1.addWidget(label)
            if self.labels_dydxs:
                self.labels_dydxs.insert(0, label)
            else:
                self.labels_dydxs.append(label)
            if index == self.MAX_EQUATION_ORDER:
                continue
            line_edit = qt.QLineEdit()
            line_edit.setMaximumWidth(self.MAX_LINE_EDIT_WIDTH)
            line_edit.setValidator(validator)
            if self.line_edits_borders:
                self.line_edits_borders.insert(0, line_edit)
            else:
                self.line_edits_borders.append(line_edit)
            if 0 < index < self.MAX_EQUATION_ORDER:
                label = Label(f"dy<sup>{index}</sup>/dx<sup>{index}</sup>(x<sub>min</sub>)=",
                              f"dy<sup>{index}</sup>/dx<sup>{index}</sup>" + "({})=")
                self.spin_box_x_min.valueChanged.connect(label.update_value)
                h_layout_2.addWidget(label)
                h_layout_2.addWidget(line_edit)
                label_comma = qt.QLabel(", ")
                if self.labels_commas:
                    self.labels_commas.insert(0, label_comma)
                else:
                    self.labels_commas.append(label_comma)
                h_layout_2.addWidget(label_comma)
            else:
                label = Label("y(x<sub>min</sub>)=", "y({})=")
                self.spin_box_x_min.valueChanged.connect(label.update_value)
                h_layout_2.addWidget(label)
                h_layout_2.addWidget(line_edit)
            if self.labels_borders:
                self.labels_borders.insert(0, label)
            else:
                self.labels_borders.append(label)
        h_layout_1.addWidget(qt.QLabel("="))
        self.line_edit_free_argument = qt.QLineEdit()
        self.line_edit_free_argument.setMaximumWidth(self.MAX_LINE_EDIT_WIDTH)
        self.line_edit_free_argument.setValidator(validator)
        h_layout_1.addWidget(self.line_edit_free_argument)
        h_layout_1.addStretch(1)
        h_layout_2.addStretch(1)
        h_layout_3 = qt.QHBoxLayout()
        h_layout_3.addLayout(form_layout_min)
        h_layout_3.addLayout(form_layout_max)
        h_layout_3.addStretch(1)
        v_layout = qt.QVBoxLayout()
        v_layout.addLayout(h_layout_1)
        v_layout.addLayout(h_layout_2)
        v_layout.addLayout(h_layout_3)
        v_layout.addStretch(1)
        widget = qt.QWidget()
        widget.setMinimumHeight(self.MIN_SCROLL_AREA_HEIGHT)
        widget.setLayout(v_layout)
        scroll_area = qt.QScrollArea()
        scroll_area.setWidget(widget)
        return scroll_area

    def _init_ui(self):
        """
        Method initializes widgets on main window.
        """

        self.setWindowTitle("Решатель дифференциальных уравений")
        self.setWindowIcon(QIcon(os.path.join(self._dir_name, "icon.png")))
        self.spin_box_equation_order = qt.QSpinBox()
        spin_box_equation_order_name = "Порядок уравнения"
        self.spin_box_equation_order.setToolTip(spin_box_equation_order_name)
        self.spin_box_equation_order.setMinimumWidth(self.MAX_LINE_EDIT_WIDTH)
        self.spin_box_equation_order.setMinimum(1)
        self.spin_box_equation_order.setMaximum(self.MAX_EQUATION_ORDER)
        form_layout = qt.QFormLayout()
        form_layout.addRow(qt.QLabel(spin_box_equation_order_name), self.spin_box_equation_order)
        button_equation_order_name = "Задать порядок уравнения"
        self.button_set_equation_order = qt.QPushButton(button_equation_order_name)
        self.button_set_equation_order.setToolTip(button_equation_order_name)
        self.button_set_equation_order.clicked.connect(self.set_equation_order)
        h_layout_1 = qt.QHBoxLayout()
        h_layout_1.addLayout(form_layout)
        h_layout_1.addWidget(self.button_set_equation_order, alignment=Qt.AlignmentFlag.AlignTop)
        h_layout_1.addStretch(1)
        self.line_edit_accuracy = qt.QLineEdit()
        line_edit_accuracy_name = "Требуемая точность вычисления"
        self.line_edit_accuracy.setToolTip(line_edit_accuracy_name)
        self.line_edit_accuracy.setValidator(QRegExpValidator(QRegExp(r"\d+\.?(\d+)?")))
        form_layout_accuracy = qt.QFormLayout()
        form_layout_accuracy.addRow(qt.QLabel(line_edit_accuracy_name), self.line_edit_accuracy)
        button_solve_name = "Решить уравнение"
        self.button_solve = qt.QPushButton(button_solve_name)
        self.button_solve.setToolTip(button_solve_name)
        self.button_solve.clicked.connect(self.start_calculation)
        button_save_figure_name = "Сохранить график"
        self.button_save_figure = qt.QPushButton(button_save_figure_name)
        self.button_save_figure.setToolTip(button_save_figure_name)
        self.button_save_figure.clicked.connect(self.save_figure)
        button_save_result_name = "Сохранить числовое решение"
        self.button_save_result = qt.QPushButton(button_save_result_name)
        self.button_save_result.setToolTip(button_save_result_name)
        self.button_save_result.clicked.connect(self.save_result)
        h_layout_2 = qt.QHBoxLayout()
        h_layout_2.addLayout(form_layout_accuracy)
        h_layout_2.addWidget(self.button_solve)
        h_layout_2.addWidget(self.button_save_figure)
        h_layout_2.addWidget(self.button_save_result)
        h_layout_2.addStretch(1)
        self.scroll_area = self._init_scroll_area()
        v_layout = qt.QVBoxLayout()
        v_layout.addLayout(h_layout_1)
        v_layout.addWidget(self.scroll_area)
        v_layout.addLayout(h_layout_2)
        v_layout.addStretch(1)
        group_box_params = qt.QGroupBox("Параметры уравнения")
        group_box_params.setLayout(v_layout)
        self.combo_box_graph = qt.QComboBox()
        combo_box_graph_name = "Какой график показать"
        self.combo_box_graph.setToolTip(combo_box_graph_name)
        self.combo_box_graph.setMinimumWidth(self.MIN_COMBO_BOX_WIDTH)
        self.combo_box_graph.currentIndexChanged.connect(self.show_graph)
        h_layout = qt.QHBoxLayout()
        h_layout.addWidget(qt.QLabel(combo_box_graph_name))
        h_layout.addWidget(self.combo_box_graph)
        h_layout.addStretch(1)
        self.figure_canvas = FigureCanvas(self.figure)
        self.progress_bar = qt.QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setVisible(False)
        self.text_edit = TextEdit()
        self.text_edit.setToolTip("Информация о вычислениях")
        self.text_edit.setReadOnly(True)
        self.text_edit.setMaximumHeight(self.MAX_TEXT_EDIT_HEIGHT)
        v_layout = qt.QVBoxLayout()
        v_layout.addWidget(group_box_params)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.figure_canvas, 1)
        v_layout.addWidget(self.progress_bar)
        v_layout.addWidget(self.text_edit)
        widget = qt.QWidget()
        widget.setLayout(v_layout)
        self.setCentralWidget(widget)
        self._set_default_params()

    def _set_default_params(self):
        """
        Method sets default parameters for differential equation.
        """

        self.spin_box_equation_order.setValue(self.DEFAULT_EQUATION_ORDER)
        self.spin_box_x_max.setValue(self.DEFAULT_MAX_X)
        self.spin_box_x_min.setValue(self.DEFAULT_MIN_X - 1)
        self.spin_box_x_min.setValue(self.DEFAULT_MIN_X)
        for index, coefficient in enumerate(self._coefficients):
            self.line_edits_coefficients[index].setText(str(coefficient))
        self.line_edit_free_argument.setText(str(self._free_argument))
        for index, border in enumerate(self._borders):
            self.line_edits_borders[index].setText(str(border))
        self._update_scroll_area(self._equation_order)
        self.line_edit_accuracy.setText(f"{self.DEFAULT_ACCURACY:.5f}")
        self._set_graphs_to_combo_box(self.DEFAULT_EQUATION_ORDER)

    def _set_graphs_to_combo_box(self, equation_order: int):
        """
        Method sets graphs to combo box widget for given equation order.
        :param equation_order: equation order.
        """

        graphs = []
        for index in range(equation_order):
            if index == 0:
                graphs.append("y(x)")
            else:
                graphs.append(f"dy{index}/dx")
        self.combo_box_graph.clear()
        self.combo_box_graph.addItems(graphs)

    def _start_thread(self):
        """
        Method starts thread for calculation.
        """

        self._solver_thread = QThread(self)
        self._solver_thread.setTerminationEnabled(True)
        self._solver = Solver()
        self._solver.moveToThread(self._solver_thread)
        self._solver.calculation_finished.connect(self.handle_finish_of_calculation)
        self._solver.calculation_for_step_finished.connect(self.handle_finish_of_calculation_for_step)
        self._solver.calculation_for_step_started.connect(self.handle_start_of_calculation_for_step)
        self._solver.calculation_started.connect(self.handle_start_of_calculation)
        self._solver.max_iterations_used.connect(self.handle_using_of_max_iterations)
        self._solver.segment_done.connect(self.handle_step_done)
        self.calculation_started.connect(self._solver.start_calculation)
        self._solver_thread.start()

    def _update_scroll_area(self, equation_order: int):
        """
        Method updates scroll area with parameters of differential equation.
        :param equation_order: new equation order.
        """

        for index in range(self.MAX_EQUATION_ORDER + 1):
            visible = index <= equation_order
            self.labels_dydxs[index].setVisible(visible)
            self.line_edits_coefficients[index].setVisible(visible)
            if index < self.MAX_EQUATION_ORDER:
                visible = index < equation_order
                self.labels_pluses[index].setVisible(visible)
                self.labels_borders[index].setVisible(visible)
                self.line_edits_borders[index].setVisible(visible)
            if index < self.MAX_EQUATION_ORDER - 1:
                self.labels_commas[index].setVisible(index < equation_order - 1)

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

    def closeEvent(self, event: QCloseEvent):
        """
        Method handles close event.
        :param event: close event.
        """

        self._solver_thread.quit()
        super().closeEvent(event)

    @pyqtSlot()
    def handle_finish_of_calculation(self):
        """
        Slot handles signal that calculation was finished.
        """

        self.progress_bar.setVisible(False)
        self.show_graph(self.combo_box_graph.currentIndex())
        self.text_edit.append("Calculation finished\n")
        self._enable_widgets(True)

    @pyqtSlot(list, list, float)
    def handle_finish_of_calculation_for_step(self, xs: List[float], ys: List[float], accuracy: float):
        """
        Slot handles signal that calculation for given step was finished.
        :param xs: list with x coordinates;
        :param ys: list with y coordinates;
        :param accuracy: accuracy of calculation.
        """

        self._xs, self._ys = xs, ys
        self.text_edit.append(f"Calculation accuracy: {accuracy}")

    @pyqtSlot(list, list)
    def handle_start_of_calculation(self, coefficients: List[float], borders: List[float]):
        """
        Slot handles signal that calculation was started.
        :param coefficients: correct coefficients in equation;
        :param borders: correct values of border equations.
        """

        self.text_edit.append("Calculation started")

    @pyqtSlot(int, float)
    def handle_start_of_calculation_for_step(self, iteration_number: int, step: float):
        """
        Slot handles signal that calculation for given step was started.
        :param iteration_number: iteration number of calculation;
        :param step: step of calculation.
        """

        self.text_edit.append(f"Iteration number: {iteration_number}, step size: {step}")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

    @pyqtSlot()
    def handle_step_done(self):
        """
        Slot handles signal that
        """

        self.progress_bar.setValue(self.progress_bar.value() + 1)

    @pyqtSlot(int)
    def handle_using_of_max_iterations(self, iteration_number: int):
        """
        Slot handles signal that max number of iterations to calculate
        equation was used.
        :param iteration_number: number of used iterations to solve equation.
        """

        self._enable_widgets(True)
        self.text_edit.append(f"Maximum number of iterations used ({iteration_number})")

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
        file_name = os.path.join(self._dir_name_for_save, ut.create_file_name(".xlsx"))
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
            self._update_scroll_area(equation_order)
            self._set_graphs_to_combo_box(equation_order)
            self._clear_graph()

    @pyqtSlot(int)
    def show_graph(self, graph_index: int):
        """
        Slot shows graph selected in combo box widget.
        :param graph_index: index of graph to show.
        """

        if not self._xs or graph_index >= len(self._ys[0]):
            self.figure.clear()
            self.figure_canvas.draw()
            return
        y_label = f"d{graph_index}Y/dX" if graph_index else "Y"
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self._xs, [y[graph_index] for y in self._ys], color="blue")
        ax.set_xlabel("X")
        ax.set_ylabel(y_label)
        self.figure_canvas.draw()

    @pyqtSlot()
    def start_calculation(self):
        """
        Method solves equation.
        """

        if all([line_edit.hasAcceptableInput() for line_edit in self.line_edits_coefficients if line_edit.isVisible()])\
                and self.line_edit_free_argument.hasAcceptableInput() and\
                all([line_edit.hasAcceptableInput() for line_edit in self.line_edits_borders if line_edit.isVisible()])\
                and self.spin_box_x_max.hasAcceptableInput() and self.spin_box_x_min.hasAcceptableInput() and\
                self.line_edit_accuracy.hasAcceptableInput():
            self._clear_graph()
            accuracy = float(self.line_edit_accuracy.text())
            borders = [float(line_edit.text()) for line_edit in self.line_edits_borders if line_edit.isVisible()]
            coefficients = [float(line_edit.text()) for line_edit in self.line_edits_coefficients
                            if line_edit.isVisible()]
            free_argument = float(self.line_edit_free_argument.text())
            limits = self.spin_box_x_min.value(), self.spin_box_x_max.value()
            self.calculation_started.emit(SolutionMethod.RUNGE_KUTTA, accuracy, coefficients, free_argument, borders,
                                          limits)
            self._enable_widgets(False)
        else:
            qt.QMessageBox.warning(self, "Предупреждение", "Введите все значения коэффициентов в уравнении и граничные"
                                                           " значения")
