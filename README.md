Shodan Search GUI
Shodan Search GUI is a Python-based application that leverages the Shodan API to perform searches and visualize data from Shodan. The application provides an intuitive graphical user interface (GUI) for conducting advanced searches, viewing detailed host information, exporting results, and visualizing data using charts and maps.

Features
Advanced Search Options: Filter search results by country, port, service, hostname, and vulnerability.
Pagination: Navigate through search results using pagination controls.
Detailed Host Information: View detailed information about each host, including IP, organization, operating system, and banner data.
Export Results: Export search results to CSV or JSON files.
Save and Load Searches: Save search criteria to a JSON file and load them for future use.
Graphical Representations: Display bar charts showing the distribution of services, countries, and ports.
Map View: Visualize the geographical distribution of search results on an interactive map.
Installation
Prerequisites
Python 3.6 or higher
Shodan API key (sign up at Shodan to obtain your API key)
Dependencies
Install the required Python packages using pip:

bash
Copy code
pip install shodan tkinter folium geopy pillow matplotlib
Usage
Set the Shodan API Key:

Set the Shodan API key as an environment variable on your system.

On Windows:

bash
Copy code
set SHODAN_API_KEY=your_shodan_api_key
On macOS and Linux:

bash
Copy code
export SHODAN_API_KEY=your_shodan_api_key
Run the Application:

bash
Copy code
python shodan_search_gui.py
How to Use
Search Criteria:

Enter the desired search criteria in the provided fields.
Select options from the dropdown menus for quick search.
Click the "Search" button to perform the search.
View Results:

Results will be displayed on the right side of the application.
Click on an organization name to view detailed information about the host.
Pagination:

Use the "Previous" and "Next" buttons to navigate through search results.
Export Results:

Click the "Export Results" button to save the search results to a CSV or JSON file.
Save and Load Searches:

Use the "Save Search" and "Load Search" buttons to save and load search criteria.
Show Map:

Click the "Show Map" button to display an interactive map showing the geographical distribution of search results.
Show Graph:

Click the "Show Graph" button to display bar charts representing the distribution of services, countries, and ports.
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgements
Shodan - The search engine for Internet-connected devices.
Folium - Python library for interactive maps.
Geopy - Geocoding library for Python.
Matplotlib - Plotting library for Python.
Feel free to customize this README file further to suit your project's specific details and needs.