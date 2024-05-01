from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QDesktopServices
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QUrl
from datetime import datetime
import time
from threading import Thread
import os
import pickle
import pandas as pd
from .worker_thread import WorkerThread
from .utils import text_changed, fetch_soup


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.new_data = []

        # Load the UI file
        loadUi("ui/JobCheckerGUI.ui", self)

        # Connect signals and slots
        self.runButton.clicked.connect(self.run_main_in_thread)
        self.quitButton.clicked.connect(self.save_and_quit)
        self.addRowButton.clicked.connect(self.add_row)
        self.deleteLastRowButton.clicked.connect(self.delete_last_row)
        self.deleteSelectedRowButton.clicked.connect(self.delete_selected_row)
        self.loadFromDictButton.clicked.connect(self.load_from_dict)

        self.dataTable.cellClicked.connect(self.update_display_box)

        # Set user agent
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
        }

        # Load configuration
        self.load_configuration()

        self.dataTable.itemClicked.connect(self.on_item_clicked)

    @pyqtSlot(QTableWidgetItem)
    def on_item_clicked(self, item):
        if item.column() == 1:  # Check if it's the URL column
            url = item.text()
            QDesktopServices.openUrl(QUrl(url))

    @pyqtSlot()
    def update_last_checked_date(self):
        # Get the current date and time
        current_date_time = datetime.now()
        # Format the date and time as a string
        formatted_date_time = current_date_time.strftime("%Y-%m-%d %H:%M:%S")
        # Set the text of the dateLastCheckedBox
        self.dateLastCheckedBox.setText(formatted_date_time)

    def fetch_urls(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(self.dataTable.rowCount())
        self.threads = []
        for i in range(self.dataTable.rowCount()):
            label_item = self.dataTable.item(i, 0)
            url_item = self.dataTable.item(i, 1)

            try:
                previous_response = self.old_dataframe.loc[self.old_dataframe["Label"] == label_item.text(), "Response"].iloc[0]
            except Exception as e:
                previous_response = None

            if label_item and url_item:
                label = label_item.text()
                url = url_item.text()
                thread = WorkerThread(i, label, url, previous_response)
                thread.update_signal.connect(self.update_result)
                thread.start()
                self.threads.append(thread)
            else:
                print(f"Skipping row {i} as it is incomplete")
                self.progress_bar.setValue(self.progress_bar.value() + 1)

    def update_result(self, thread_id, label, url, response, result):
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        self.dataTable.setItem(thread_id, 2, QTableWidgetItem(result[1]))
        self.new_data.append((thread_id, label, url, response))

    def print_data(self):
        print("Data:")
        for thread_id, index, label, value in self.data_holder.data:
            print(f"Thread {label}: {value}")

    def run_main_in_thread(self):
        main_run_thread = Thread(target=self.main_run)
        main_run_thread.start()

    def main_run(self):
        self.load_previous_dataframe()
        self.fetch_urls()
        self.wait_for_progressbar(self.progress_bar)
        self.make_and_save_dataframe()

    def wait_for_progressbar(self, progress_bar):
        while progress_bar.value() < progress_bar.maximum():
            time.sleep(0.1)  # Adjust sleep duration as needed
        print("All threads have finished")

    def load_previous_dataframe(self):
        try:
            with open("resources/previous_responses.pickle", "rb") as f:
                old_df = pickle.load(f)
        except FileNotFoundError:
            old_df = pd.DataFrame(columns=["Label", "URL", "Response"])
        self.old_dataframe = old_df

    def make_and_save_dataframe(self):
        # Save the current responses to update the pickle file
        new_df = pd.DataFrame(columns=["Index", "Label", "URL", "Response"])
        for index, label, url, response in self.new_data:
            # new_df = new_df.append({"Index": index, "Label": label, "URL": url, "Response": response}, ignore_index=True)
            new_df = new_df._append({"Index": index, "Label": label, "URL": url, "Response": response}, ignore_index=True)
        new_df = new_df.sort_values(by="Index")
        new_df = new_df.drop(columns=["Index"])
        self.newest_responses = new_df

        # Delete old previous_responses.pickle file
        try:
            os.remove("resources/previous_responses.pickle")
        except FileNotFoundError:
            pass

        with open("resources/previous_responses.pickle", "wb") as f:
            pickle.dump(new_df, f)
        print('Data saved to "previous_responses.pickle"')


    def load_configuration(self):
        try:
            with open("config/dataTable_config.pickle", "rb") as f:
                data = pickle.load(f)
                config = data["config"]
                row_sizes = data["row_sizes"]
                column_sizes = data["column_sizes"]

                # Set the row count according to the number of rows in the configuration
                self.dataTable.setRowCount(len(config))

                # Load cell values
                for row, rowData in enumerate(config):
                    for col, value in enumerate(rowData):
                        item = QTableWidgetItem(value)
                        self.dataTable.setItem(row, col, item)

                # Set row sizes
                for row, size in enumerate(row_sizes):
                    self.dataTable.setRowHeight(row, size)

                # Set column sizes
                for col, size in enumerate(column_sizes):
                    self.dataTable.setColumnWidth(col, size)
        except FileNotFoundError:
            pass  # No configuration file found, proceed with default configuration

    def save_configuration(self):
        config = []
        sizes = {
            "rowCount": self.dataTable.rowCount(),
            "columnCount": self.dataTable.columnCount(),
        }
        row_sizes = [self.dataTable.rowHeight(row) for row in range(sizes["rowCount"])]
        column_sizes = [
            self.dataTable.columnWidth(col) for col in range(sizes["columnCount"])
        ]

        for row in range(sizes["rowCount"]):
            rowData = []
            for col in range(sizes["columnCount"]):
                item = self.dataTable.item(row, col)
                value = item.text() if item else ""
                rowData.append(value)
            config.append(rowData)

        with open("config/dataTable_config.pickle", "wb") as f:
            pickle.dump(
                {
                    "config": config,
                    "row_sizes": row_sizes,
                    "column_sizes": column_sizes,
                },
                f,
            )

    def save_and_quit(self):
        self.save_configuration()
        self.close()

    def add_row(self):
        row_count = self.dataTable.rowCount()
        self.dataTable.insertRow(row_count)

    def delete_selected_row(self):
        selected_row = self.dataTable.currentRow()
        if selected_row >= 0:
            self.dataTable.removeRow(selected_row)

    def delete_last_row(self):
        row_count = self.dataTable.rowCount()
        if row_count > 0:
            self.dataTable.removeRow(row_count - 1)

    def update_display_box(self, row, col):
        self.displayBox.setText(f"Selected Row: {row}, Column: {col}")


    def load_from_dict(self):
        # Load the dictionary called uni_urls that has the labels and URLs as key-value pairs
        from data.labels_and_urls import labels_and_urls

        # Delete all rows of table
        self.dataTable.setRowCount(0)

        for i, (label, url) in enumerate(labels_and_urls.items()):
            self.dataTable.insertRow(i)
            self.dataTable.setItem(i, 0, QTableWidgetItem(label))
            self.dataTable.setItem(i, 1, QTableWidgetItem(url))

