
# LinkedIn Employee Parser

Welcome to the LinkedIn Employee Parser! This project is based on the LinkedInDumper CLI script and is designed to facilitate the extraction of employee data from LinkedIn company pages. This application is equipped with a user-friendly graphical interface built using PyQt5, allowing users to easily configure and initiate the parsing process without any need for command-line interaction.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Automated Windows Launch](#automated-windows-launch)
- [Acknowledgements](#acknowledgements)
- [License](#license)

## Overview

The LinkedIn Employee Parser enables users to extract employee information from LinkedIn company pages, such as names, positions, and locations, and save the data in both JSON and Excel formats. The application is built with Python and leverages PyQt5 for the graphical user interface (GUI), making it accessible to users of all levels of technical expertise.

## Features

- **Automated Cookie Retrieval:** Automatically retrieves the LinkedIn authentication cookie (`li_at`) from the user's browser, removing the need for manual input.
- **Multiple Companies:** Allows users to parse data from multiple companies by providing URLs separated by commas.
- **Position Filtering:** Users can filter the results based on specific positions or titles using comma-separated filters.
- **Progress Tracking:** Real-time progress tracking of the parsing process with a progress bar.
- **Data Export:** Saves the parsed data into JSON and Excel (.xlsx) formats for easy access and analysis.
- **Welcome Screen:** A friendly welcome screen provides users with information about the application and an option to visit the original LinkedInDumper GitHub page.
- **Customizable Interface:** User-friendly interface with customizable options, including the number of employees to parse and position filters.

## Installation

### Prerequisites

Ensure that you have the following installed on your system:
- Python 3.7+
- pip (Python package installer)

### Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/LinkedInEmployeeParser.git
   cd LinkedInEmployeeParser
   ```

2. **Install Dependencies:**

   Navigate to the project directory and install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**

   Start the application using the following command:

   ```bash
   python linkedindumper.py
   ```

## Usage

1. **Launching the Application:**
   - Upon launching, the application will display a welcome screen with information about the project. Users can choose to visit the original GitHub page or proceed to the main interface.

2. **Configuring Parsing Options:**
   - Enter the LinkedIn company URLs (comma-separated for multiple companies).
   - Select the number of employees to parse.
   - Optionally, enter position filters to refine the search results.

3. **Starting the Parsing Process:**
   - Click on the `Start Parsing` button to begin. The progress bar will update in real-time as the employees are parsed.

4. **Viewing and Saving Results:**
   - Once parsing is complete, the application will save the results in both JSON and Excel formats. The directory containing the Excel file will open automatically.

## Configuration

The application uses a `config.yml` file to store configuration settings, such as whether to show the welcome screen on startup. Users can modify this file to customize the application's behavior.

## Automated Windows Launch

You can automate the setup and launch process on Windows using a batch script provided in this repository. Here's how it works:

### How the Batch Script Works

1. **Python Installation Check:**
   - The script begins by checking if Python is installed at a specified path. If Python is not found, it attempts to locate Python in the system PATH.
   - If Python is still not found, the script automatically downloads and installs Python 3.12.

2. **Virtual Environment Setup:**
   - The script creates a virtual environment in the project directory to isolate the project dependencies.

3. **Dependency Installation:**
   - After setting up the virtual environment, the script installs the required dependencies from the `requirements.txt` file.

4. **Application Launch:**
   - Finally, the script activates the virtual environment and runs the LinkedIn Employee Parser application.

### Running the Batch Script

1. **Create the Script:**
   - Copy the provided batch script code into a new text file and save it with a `.bat` extension, e.g., `start_linkedin_parser.bat`.

2. **Run the Script:**
   - Double-click the `.bat` file to execute the script. The script will handle the entire setup and launch process for you.

## Acknowledgements

This project is inspired by the [LinkedInDumper](https://github.com/l4rm4nd/LinkedInDumper) CLI script. Special thanks to the original author for their work on the LinkedInDumper tool.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
