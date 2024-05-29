import os
import tkinter as tk
from tkinter import ttk, messagebox
import shodan

# Retrieve the Shodan API key from environment variables
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')

if not SHODAN_API_KEY:
    raise ValueError("Please set the SHODAN_API_KEY environment variable")

# Initialize the Shodan API client
api = shodan.Shodan(SHODAN_API_KEY)

def search_shodan(query, country_code):
    try:
        # Append the country filter to the query if a country is selected
        if country_code:
            query += f' country:{country_code}'
        
        results = api.search(query)
        result_text.delete(1.0, tk.END)  # Clear previous results
        result_text.insert(tk.END, f'Results found: {results["total"]}\n\n')
        for result in results['matches']:
            result_text.insert(tk.END, f'IP: {result["ip_str"]}\n{result["data"]}\n\n')
    except shodan.APIError as e:
        messagebox.showerror("Error", f'Shodan API error: {e}')

def on_search():
    query = search_var.get()
    country_code = country_var.get()
    search_shodan(query, country_code)

# Create main window
root = tk.Tk()
root.title("Shodan Search GUI")
root.geometry("800x600")

# Create search criteria dropdown
search_label = tk.Label(root, text="Search Criteria:")
search_label.pack(pady=5)

search_var = tk.StringVar()
search_dropdown = ttk.Combobox(root, textvariable=search_var)
search_dropdown['values'] = ("apache", "nginx", "ssh", "ftp", "telnet", "http")
search_dropdown.pack(pady=5)

# Create country filter dropdown
country_label = tk.Label(root, text="Country Code:")
country_label.pack(pady=5)

country_var = tk.StringVar()
country_dropdown = ttk.Combobox(root, textvariable=country_var)
country_dropdown['values'] = (
    "",  # Allow for no country filter
    "US", "CA", "GB", "DE", "FR", "JP", "CN", "RU", "BR", "IN"  # Add more as needed
)
country_dropdown.pack(pady=5)

# Create search button
search_button = tk.Button(root, text="Search", command=on_search)
search_button.pack(pady=5)

# Create result text box
result_text = tk.Text(root, wrap=tk.WORD, height=25, width=90)
result_text.pack(pady=10)

# Run the application
root.mainloop()
