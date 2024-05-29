import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shodan
import csv
import json

# Retrieve the Shodan API key from environment variables
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')

if not SHODAN_API_KEY:
    raise ValueError("Please set the SHODAN_API_KEY environment variable")

# Initialize the Shodan API client
api = shodan.Shodan(SHODAN_API_KEY)

def search_shodan(query, country_code, port, service):
    try:
        # Build the search query with additional filters
        if country_code:
            query += f' country:{country_code}'
        if port:
            query += f' port:{port}'
        if service:
            query += f' {service}'
        
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
    port = port_var.get()
    service = service_var.get()
    search_shodan(query, country_code, port, service)

def export_results():
    results_text = result_text.get(1.0, tk.END)
    if not results_text.strip():
        messagebox.showwarning("Warning", "No results to export.")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")])
    if file_path:
        if file_path.endswith(".csv"):
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Results"])
                writer.writerow([results_text])
        elif file_path.endswith(".json"):
            with open(file_path, 'w') as file:
                json.dump({"results": results_text}, file)
        messagebox.showinfo("Success", f"Results exported to {file_path}")

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

# Create port entry
port_label = tk.Label(root, text="Port:")
port_label.pack(pady=5)

port_var = tk.StringVar()
port_entry = tk.Entry(root, textvariable=port_var)
port_entry.pack(pady=5)

# Create service entry
service_label = tk.Label(root, text="Service:")
service_label.pack(pady=5)

service_var = tk.StringVar()
service_entry = tk.Entry(root, textvariable=service_var)
service_entry.pack(pady=5)

# Create search button
search_button = tk.Button(root, text="Search", command=on_search)
search_button.pack(pady=5)

# Create export button
export_button = tk.Button(root, text="Export Results", command=export_results)
export_button.pack(pady=5)

# Create result text box
result_text = tk.Text(root, wrap=tk.WORD, height=20, width=90)
result_text.pack(pady=10)

# Run the application
root.mainloop()
