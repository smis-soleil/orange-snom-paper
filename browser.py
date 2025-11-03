from AnyQt.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QRadioButton, QPushButton, QTabWidget
from AnyQt.QtCore import Qt, QEvent, QObject
from AnyQt.QtWidgets import QWidget, QSplitter

from orangecanvas.scheme.signalmanager import SignalManager
from orangecanvas.registry.description import WidgetDescription

from orangewidget.workflow.widgetsscheme import WidgetsScheme

from Orange.widgets.data.owfile import OWFile
from Orange.widgets.data.owtable import OWTable
from orangecontrib.spectroscopy.widgets.owpreprocess import OWPreprocess
from orangecontrib.spectroscopy.widgets.owhyper import OWHyper
from orangecontrib.spectroscopy.widgets.owpreprocess import OWPreprocess
from owfilebrowser import OWFileBrowser
from orangecontrib.spectroscopy.io.neaspec import NeaReader
from orangecontrib.spectroscopy.widgets.owoverlay import OWOverlay
from orangecontrib.snom.widgets.owpreprocessimage import OWPreprocessImage


class EventFilterEscape(QObject):

    def __init__(self, parent):
        super().__init__(parent)
        parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        if not obj.__dict__:  # object destruction in progress
            return True
        if event.type() == QEvent.KeyPress and event.key() in [Qt.Key_Escape]:
            return True
        else:
            return obj.eventFilter(obj, event)


class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('SNOM data browser')
        self.workflow = WidgetsScheme()
        # Create a splitter
        splitter = QSplitter(Qt.Horizontal)
        # Create Quasar widgets
        # File browser
        self.file_node, self.file = self.create_widget(OWFileBrowser)
        self.file.toggle_infobox()
        self.file.set_fixed_readers(["NeaSPEC"])
        # self.file_node.state_changed.connect(self.check_node_states)
        EventFilterEscape(self.file)
        # Image preprocessor
        self.image_process_node, self.image_process = self.create_widget(OWPreprocessImage)
        EventFilterEscape(self.image_process)
        # Spectra preprocessor
        self.spectra_process_node, self.spectra_process = self.create_widget(OWPreprocess)
        EventFilterEscape(self.spectra_process)
        # Image overlay node
        self.overlay_node, self.overlay = self.create_widget(OWOverlay)
        EventFilterEscape(self.overlay)
        # Spectra and image viewer
        self.viewer_node, self.viewer = self.create_widget(OWHyper)
        EventFilterEscape(self.viewer)
        self.viewer_node.state_changed.connect(self.check_node_states)
        
        # Set up layout
        layout = QHBoxLayout()
        layout.addWidget(splitter)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.preprocess_tab = QWidget()
        self.view_tab = QWidget()
        # Add tabs
        self.tabs.addTab(self.preprocess_tab, "Process")
        self.tabs.addTab(self.view_tab, "View")

        splitter.addWidget(self.file)
        splitter.addWidget(self.tabs)

        # Set up some tools (extend as needed)
        tool_widget = QWidget()
        tool_widget.setFixedHeight(50)
        tool_layout = QHBoxLayout()
        self.add_reference_button = QPushButton("Add as reference")
        self.add_reference_button.clicked.connect(lambda: self.add_reference(self.file.filepath))
        self.add_overlay_button = QPushButton("Add as overlay")
        self.add_overlay_button.clicked.connect(lambda: self.add_overlay(self.file.filepath))
        tool_layout.addWidget(self.add_reference_button)
        tool_layout.addWidget(self.add_overlay_button)
        tool_widget.setLayout(tool_layout)

        self.preprocess_tab.layout = QVBoxLayout()
        self.view_tab.layout = QVBoxLayout()
        self.preprocess_tab.layout.addWidget(tool_widget)
        self.preprocess_tab.layout.addWidget(self.image_process)
        self.preprocess_tab.layout.addWidget(self.spectra_process)
        self.view_tab.layout.addWidget(self.viewer)
        self.preprocess_tab.setLayout(self.preprocess_tab.layout)
        self.view_tab.setLayout(self.view_tab.layout)

        self.spectra_process.setHidden(True)
        self.overlay.setHidden(True)

        widget = QWidget()
        widget.setLayout(layout)

        self.im2view_link = None
        self.sp2view_link = None
        # Create links between widgets
        self.workflow.new_link(self.file_node, "data", self.image_process_node, "data")
        self.workflow.new_link(self.file_node, "data", self.spectra_process_node, "data")
        self.im2view_link = self.workflow.new_link(self.image_process_node, "preprocessed_data", self.overlay_node, "maindata")
        self.workflow.new_link(self.overlay_node, "outdata", self.viewer_node, "data")
        self.add_reference_button.setDisabled(True)

        sm = SignalManager()
        sm.set_workflow(self.workflow)

        self.file.show()
        self.image_process.show()

        sm.start()

        self.setCentralWidget(widget)
        self.viewer._OWBaseWidget__toggleControlArea()

    def create_widget(self, cl):
        """ Create a widget and its node in the workflow """
        node = self.workflow.new_node(WidgetDescription(**cl.get_widget_description()))
        widget = self.workflow.widget_for_node(node)
        return node, widget
    
    def check_node_states(self,v):
        """ Switch between image and spectra processing based on the file type """
        if self.file.reader:
            if self.file.filepath.endswith(".gsf"):
                self.spectra_process.setHidden(True)
                self.image_process.setHidden(False)
                if self.sp2view_link is not None:
                    self.workflow.remove_link(self.sp2view_link) 
                    self.im2view_link = self.workflow.new_link(self.image_process_node, "preprocessed_data", self.overlay_node, "maindata")
                    self.sp2view_link = None
                    self.add_overlay_button.setDisabled(False)
                    self.add_reference_button.setDisabled(True)
            elif self.file.filepath.endswith(".txt"):
                self.image_process.setHidden(True)
                self.spectra_process.setHidden(False)
                if self.im2view_link is not None:
                    self.workflow.remove_link(self.im2view_link) 
                    self.sp2view_link = self.workflow.new_link(self.spectra_process_node, "preprocessed_data", self.overlay_node, "maindata")
                    self.im2view_link = None
                    self.add_overlay_button.setDisabled(True)
                    self.add_reference_button.setDisabled(False)

    def add_reference(self, absolute_filename):
        """ Add the currently selected file as reference to the spectra processor """
        reader = NeaReader(absolute_filename)
        reader.sheet = self.file.sheet
        reference_data = reader.read()
        if reference_data is not None:
            self.spectra_process.set_reference(reference_data)

    def add_overlay(self, absolute_filename):
        """ Add the currently selected file as overlay data to the OWOverlay widget """
        reader = NeaReader(absolute_filename)
        overlay_data = reader.read()
        if overlay_data is not None:
            self.overlay.set_overlaydata(overlay_data)

app = QApplication([])
window = mainwindow()

window.show()
app.exec()