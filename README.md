Here's the formatted text for your README file, ready to be copied and pasted:

```markdown
# Shodan Search GUI

Shodan Search GUI is a Python-based application that leverages the Shodan API to perform searches and visualize data from Shodan. The application provides an intuitive graphical user interface (GUI) for conducting advanced searches, viewing detailed host information, exporting results, and visualizing data using charts and maps.

## Features

- **Advanced Search Options**: Filter search results by country, port, service, hostname, and vulnerability.
- **Pagination**: Navigate through search results using pagination controls.
- **Detailed Host Information**: View detailed information about each host, including IP, organization, operating system, and banner data.
- **Export Results**: Export search results to CSV or JSON files.
- **Save and Load Searches**: Save search criteria to a JSON file and load them for future use.
- **Graphical Representations**: Display bar charts showing the distribution of services, countries, and ports.
- **Map View**: Visualize the geographical distribution of search results on an interactive map.

## Installation

### Prerequisites

- Python 3.6 or higher
- Shodan API key (sign up at [Shodan](https://account.shodan.io/register) to obtain your API key)

### Dependencies

Install the required Python packages using pip:

```bash
pip install shodan tkinter folium geopy pillow matplotlib
```

## Usage

1. **Set the Shodan API Key**:

   Set the Shodan API key as an environment variable on your system.

   On Windows:

   ```bash
   set SHODAN_API_KEY=your_shodan_api_key
   ```

   On macOS and Linux:

   ```bash
   export SHODAN_API_KEY=your_shodan_api_key
   ```

2. **Run the Application**:

   ```bash
   python shodan_search_gui.py
   ```

## How to Use

1. **Search Criteria**:
   - Enter the desired search criteria in the provided fields.
   - Select options from the dropdown menus for quick search.
   - Click the "Search" button to perform the search.

2. **View Results**:
   - Results will be displayed on the right side of the application.
   - Click on an organization name to view detailed information about the host.

3. **Pagination**:
   - Use the "Previous" and "Next" buttons to navigate through search results.

4. **Export Results**:
   - Click the "Export Results" button to save the search results to a CSV or JSON file.

5. **Save and Load Searches**:
   - Use the "Save Search" and "Load Search" buttons to save and load search criteria.

6. **Show Map**:
   - Click the "Show Map" button to display an interactive map showing the geographical distribution of search results.

7. **Show Graph**:
   - Click the "Show Graph" button to display bar charts representing the distribution of services, countries, and ports.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Shodan](https://www.shodan.io/) - The search engine for Internet-connected devices.
- [Folium](https://python-visualization.github.io/folium/) - Python library for interactive maps.
- [Geopy](https://geopy.readthedocs.io/en/stable/) - Geocoding library for Python.
- [Matplotlib](https://matplotlib.org/) - Plotting library for Python.
```

You can copy and paste this text into your README.md file, and it should be formatted correctly for Markdown.