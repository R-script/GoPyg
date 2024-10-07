import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import os
import pandas as pd
import pygwalker as pyg
import webbrowser


class GoPyg(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        self.file_buttons = {}
        self.populate_file_list()
        self.main_window.content = self.box
        self.main_window.show()

    def populate_file_list(self):
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        files = [f for f in os.listdir(downloads_folder) if os.path.isfile(os.path.join(downloads_folder, f))]

        # Filter files to only include CSV, JSON, and XLSX
        allowed_extensions = {'.csv', '.json', '.xlsx'}
        filtered_files = [f for f in files if os.path.splitext(f)[1].lower() in allowed_extensions]

        for file in filtered_files:
            file_path = os.path.join(downloads_folder, file)
            file_button = toga.Button(file, on_press=lambda widget, path=file_path: self.open_file(path),
                                      style=Pack(padding=5))
            self.file_buttons[file] = file_path
            self.box.add(file_button)

    def open_file(self, file_path):
        # Generate visualization
        self.generate_visualization(file_path)

    def generate_visualization(self, file_path):
        # Load data
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".json"):
            df = pd.read_json(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            # Handle unsupported file type
            return

        # Generate HTML file for PyGwalker
        output = pyg.walk(df).to_html()
        html_path = os.path.join(os.path.expanduser("~"), "Downloads", "data.html")
        with open(html_path, "w") as file:
            file.write(output)

        # Open the HTML file in the default web browser
        webbrowser.open(f"file://{html_path}")


def main():
    return GoPyg()


if __name__ == '__main__':
    main().main_loop()
