from PyQt5.QtCore import QThread, pyqtSignal
from .utils import fetch_soup, text_changed

class WorkerThread(QThread):
    update_signal = pyqtSignal(int, str, str, object, tuple)

    def __init__(self, thread_id, label, url, previous_response):
        super().__init__()
        self.thread_id = thread_id
        self.label = label
        self.url = url
        self.previous_response = previous_response

    def run(self):
        response = fetch_soup(self.url).get_text()

        # Compare with old data
        if self.previous_response:
            old_text = self.previous_response
            if text_changed(old_text, response):
                result = (True, f'Some text for {self.label} has changed.')
            else:
                result = (False, f'Text has not changed')
        else:
            result = (False, f'No previous response found for "{self.label}"')

        self.update_signal.emit(self.thread_id, self.label, self.url, response, result)

