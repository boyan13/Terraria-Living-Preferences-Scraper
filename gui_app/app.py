
import threading

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import QStyle

from gui_lib.utils import wrap_in_scroll_area
from gui_lib.basic import Panel, StackedPanel
from gui_lib.tables import DataFrameTableModel
from gui_app.screens import *
from gui_app.scraping import read_terraria_wiki


class ScreenStack(StackedPanel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class AppWindow(Panel):

    # Scraper thread callback API
    scraping_set_max_progress = pyqtSignal(int)
    scraping_increment_progress = pyqtSignal()
    scraping_complete = pyqtSignal()
    scraping_failed = pyqtSignal()

    # Threading events
    scraping_thread_running = threading.Event()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Configure window position, size, title, icon
        self.setGeometry(100, 100, 360, 250)
        self.setMinimumSize(360, 250)
        self.setWindowTitle("Terraria NPC housing preferences extractor!")
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle.StandardPixmap, 'SP_MessageBoxInformation')))

        # Thread unsafe variables
        self.__scraper = None
        self.__npcs = None

        # NPC information (parsed from self.__npcs after scraping)
        self.favorite_biomes_counts = None
        self.favorite_neighbor_counts = None
        self.least_favorite_biomes_counts = None
        self.least_favorite_neighbor_counts = None

        # Screens
        self.start_screen = StartScreen()
        self.progress_screen = LoadingScreen()
        self.tables_screen = TableScreen()

        # Configure screen stack
        self.stack_scroll_area = wrap_in_scroll_area(ScreenStack(self))
        self.stack = self.stack_scroll_area.widget()
        self.stack.addWidget(self.start_screen)
        self.stack.addWidget(self.progress_screen)
        self.stack.addWidget(self.tables_screen)
        self.show_screen(self.start_screen)

        # Configure layout
        QuickHBox(self).add(self.stack_scroll_area)

        # Configure size policies of screens and stack
        self.stack_scroll_area.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.stack.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.tables_screen.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        # Configure events

        # Event: Begin scraping when the start button is pressed
        self.start_screen.start_button.clicked.connect(lambda checked: self.begin_scraping_wiki())
        # Event: Initialize the progress bar when the scraper thread signals the necessary information
        self.scraping_set_max_progress.connect(lambda value: self.progress_screen.init_progress(value))
        # Event: Increment the progress bar when the scraper thread signals progress
        self.scraping_increment_progress.connect(lambda: self.progress_screen.increment_progress())
        # Event: Attach handler
        self.scraping_complete.connect(self._event_scraping_complete)
        # Event: Attach handler
        self.scraping_failed.connect(self._event_scraping_failed)

    def begin_scraping_wiki(self):
        """Begin scraping the wiki using a background daemon thread. Show the progress bar screen."""

        if self.__scraper is not None:  # If the thread already exists, it will be very bad to start another one.
            raise RuntimeError('Attempting to create a scraper thread when a scraper thread already exists.')

        scraper = threading.Thread(name='ScrapingThread', target=self._scrape_wiki)  # Create the scraper thread
        scraper.setDaemon(True)  # Set as daemon thread
        self.__scraper = scraper  # Store a reference of the scraper thread
        scraper.start()  # Start the scraper thread
        self.show_screen(self.progress_screen)  # Show the progress bar screen

    def _scrape_wiki(self):
        """Begin scraping the wiki page. This method will raise an exception if a thread different from the scraper
        thread attempts to execute it."""

        if threading.currentThread() is not self.__scraper:  # If this is not the scraper thread
            raise RuntimeError('Scraping method called with wrong thread.')

        success = False
        result = None

        try:
            scrape = read_terraria_wiki()  # Get a scraping generator

            # Get the total amount of web pages that will be scraped
            self.scraping_set_max_progress.emit(scrape.__next__())

            while True:
                try:
                    scrape.__next__()  # Scrape the next NPC
                except StopIteration as exc:
                    result = exc.value  # Grab the result
                    break  # We are done scraping
                finally:
                    self.scraping_increment_progress.emit()  # Increment the progress bar

            # It would be better to put the result in a Queue so the main thread can safely update the self.__npcs
            # variable to prevent a race condition, however it seems unnecessary to invest in this architecture for
            # just this single variable write, and by design this variable should not be touched by the main thread
            # prior to a scraping_complete signal.
            self.__npcs = result  # Store the result

            success = True

        except Exception as exc:
            pass  # Ignore exceptions, just cancel everything and proceed to the cleanup code in the 'finally' clause.

        finally:
            self.scraping_thread_running.clear()  # Clear the scraper thread "running" event
            self.__scraper = None  # Clear the reference to the scraper thread
            self.scraping_complete.emit() if success else self.scraping_failed.emit()  # Emit scraping status

    def generate_stats(self):
        """Generate some shared stats from the scraped npcs."""
        favorite_biomes_counts = {}
        least_favorite_biomes_counts = {}
        favorite_neighbor_counts = {}
        least_favorite_neighbor_counts = {}

        for npc in self.__npcs:

            for favorite_biome in npc.favorite_biomes:
                if favorite_biome not in favorite_biomes_counts.keys():
                    favorite_biomes_counts[favorite_biome] = 0
                favorite_biomes_counts[favorite_biome] += 1

            for favorite_neighbor in npc.favorite_neighbors:
                if favorite_neighbor not in favorite_neighbor_counts.keys():
                    favorite_neighbor_counts[favorite_neighbor] = 0
                favorite_neighbor_counts[favorite_neighbor] += 1

            for least_favorite_biome in npc.least_favorite_biomes:
                if least_favorite_biome not in least_favorite_biomes_counts.keys():
                    least_favorite_biomes_counts[least_favorite_biome] = 0
                least_favorite_biomes_counts[least_favorite_biome] += 1

            for least_favorite_neighbor in npc.least_favorite_neighbors:
                if least_favorite_neighbor not in least_favorite_neighbor_counts.keys():
                    least_favorite_neighbor_counts[least_favorite_neighbor] = 0
                least_favorite_neighbor_counts[least_favorite_neighbor] += 1

        self.favorite_biomes_counts = favorite_biomes_counts
        self.least_favorite_biomes_counts = least_favorite_biomes_counts
        self.favorite_neighbor_counts = favorite_neighbor_counts
        self.least_favorite_neighbor_counts = least_favorite_neighbor_counts

    def print_stats(self):
        # For now, we'll be printing this, but it should eventually move somewhere in the gui.

        print('\nPrinting stats:')

        print('\nDisplaying favorite biomes amount.\n')
        for biome, amount in self.favorite_biomes_counts.items():
            print('{0:30}{1:2}'.format(biome, amount))

        print('\nDisplaying favorite neighbors amount.\n')
        for neighbor, amount in self.favorite_neighbor_counts.items():
            print('{0:30}{1:2}'.format(neighbor, amount))

        print('\nDisplaying least favorite biomes amount.\n')
        for biome, amount in self.least_favorite_biomes_counts.items():
            print('{0:30}{1:2}'.format(biome, amount))

        print('\nDisplaying least favorite neighbors amount.\n')
        for neighbor, amount in self.least_favorite_neighbor_counts.items():
            print('{0:30}{1:2}'.format(neighbor, amount))

    def _event_scraping_complete(self):
        self.generate_stats()  # Generate some stats
        self.print_stats()
        self.populate_tables_screen()  # Create tables from the scraped data
        self.show_screen(self.tables_screen)  # Show the tables screen

    def _event_scraping_failed(self):
        print('Scraper encountered errors. Terminating program.')
        QTimer.singleShot(1000, self.close)  # Terminate after 1 second

    def populate_tables_screen(self):
        """Create tables from the scraped data and add them to the tables screen."""

        # If the scraper thread is still run, then it is not safe to access the npcs variable.
        if self.scraping_thread_running.isSet():
            raise RuntimeError(
                'Attempting to access thread-unsafe variable "self.__npcs" while the scraping thread is running.'
            )

        for npc in self.__npcs:
            # Get the npc's living preferences data frame if there is one, or create a dummy empty data frame
            df = npc.living_preferences if npc.living_preferences is not None else pd.DataFrame()
            table_model = DataFrameTableModel(df)  # Create a table model from the data frame
            self.tables_screen.add_table(npc.name, table_model)  # Add the table to the tables screen

    def show_screen(self, screen: QWidget):
        """Change the current widget of the view stack, and handle any view-specific initialization or validation."""

        self.stack.setCurrentWidget(screen)
        if screen is self.tables_screen:
            # If the screen is relatively small, we want to make it bigger before displaying the tables screen.
            w = 1200 if self.width() < 1200 else self.width()
            h = 900 if self.height() < 900 else self.height()
            if w != self.width or h != self.height():
                self.setGeometry(200, 100, w, h)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print('All done!')
        super().closeEvent(a0)
