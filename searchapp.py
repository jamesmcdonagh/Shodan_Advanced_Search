import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shodan
import csv
import json
import folium
from geopy.geocoders import Nominatim
from io import BytesIO
from PIL import Image, ImageTk

# Retrieve the Shodan API key from environment variables
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')

if not SHODAN_API_KEY:
    raise ValueError("Please set the SHODAN_API_KEY environment variable")

# Initialize the Shodan API client
api = shodan.Shodan(SHODAN_API_KEY)
geolocator = Nominatim(user_agent="shodan_gui")

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
            org_str = result.get("org", "Unknown Organization")
            ip_str = result["ip_str"]
            start = result_text.index(tk.END)
            result_text.insert(tk.END, f'{org_str}\n\n')
            end = result_text.index(tk.END)
            result_text.tag_add(ip_str, start, end)
            result_text.tag_config(ip_str, foreground="blue", underline=True)
            # Ensure the correct IP is passed by using a closure
            result_text.tag_bind(ip_str, "<Button-1>", lambda e, ip=ip_str: show_host_info(ip))
    except shodan.APIError as e:
        messagebox.showerror("Error", f'Shodan API error: {e}')

def on_search():
    query = search_var.get()
    country_code = country_var.get()
    port = port_var.get()
    service = service_var.get()
    search_shodan(query, country_code, port, service)

def show_host_info(ip):
    def fetch_host_info(ip):
        try:
            host = api.host(ip)
            info = f'IP: {host["ip_str"]}\nOrganization: {host.get("org", "n/a")}\nOperating System: {host.get("os", "n/a")}\n\n'
            for item in host['data']:
                info += f'Port: {item["port"]}\nBanner: {item["data"]}\n\n'
            
            # Show host info in a new window
            info_window = tk.Toplevel(root)
            info_window.title(f"Host Information - {ip}")
            info_text = tk.Text(info_window, wrap=tk.WORD, height=20, width=80)
            info_text.insert(tk.END, info)
            info_text.pack(pady=10)

            # Show map with host location
            lat = host.get("location", {}).get("latitude")
            lon = host.get("location", {}).get("longitude")
            if lat and lon:
                map = folium.Map(location=[lat, lon], zoom_start=13)
                folium.Marker([lat, lon], popup=ip).add_to(map)
                map_data = BytesIO()
                map.save(map_data, close_file=False)
                map_image = Image.open(map_data)
                map_photo = ImageTk.PhotoImage(map_image)
                map_label = tk.Label(info_window, image=map_photo)
                map_label.image = map_photo  # Keep a reference to avoid garbage collection
                map_label.pack(pady=10)

        except shodan.APIError as e:
            messagebox.showerror("Error", f'Shodan API error: {e}')

    # Ensure only one window is opened
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()
    fetch_host_info(ip)

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

def save_search():
    search_query = {
        "query": search_var.get(),
        "country": country_var.get(),
        "port": port_var.get(),
        "service": service_var.get()
    }
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as file:
            json.dump(search_query, file)
        messagebox.showinfo("Success", f"Search saved to {file_path}")

def load_search():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'r') as file:
            search_query = json.load(file)
        search_var.set(search_query.get("query", ""))
        country_var.set(search_query.get("country", ""))
        port_var.set(search_query.get("port", ""))
        service_var.set(search_query.get("service", ""))

# Create main window
root = tk.Tk()
root.title("Shodan Search GUI")
root.geometry("1000x600")

# Create a frame for the search criteria
frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

# Create a frame for the results
frame_right = tk.Frame(root)
frame_right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Search criteria widgets
search_label = tk.Label(frame_left, text="Search Criteria:")
search_label.pack(pady=5)

search_var = tk.StringVar()
search_dropdown = ttk.Combobox(frame_left, textvariable=search_var)
search_dropdown['values'] = ("apache", "nginx", "ssh", "ftp", "telnet", "http")
search_dropdown.pack(pady=5)

country_label = tk.Label(frame_left, text="Country Code:")
country_label.pack(pady=5)

country_var = tk.StringVar()
country_dropdown = ttk.Combobox(frame_left, textvariable=country_var)
country_dropdown['values'] = (
    "",  # Allow for no country filter
    "US", "CA", "GB", "DE", "FR", "JP", "CN", "RU", "BR", "IN"  # Add more as needed
)
country_dropdown.pack(pady=5)

port_label = tk.Label(frame_left, text="Port:")
port_label.pack(pady=5)

port_var = tk.StringVar()
port_entry = tk.Entry(frame_left, textvariable=port_var)
port_entry.pack(pady=5)

service_label = tk.Label(frame_left, text="Service:")
service_label.pack(pady=5)

service_var = tk.StringVar()
service_entry = tk.Entry(frame_left, textvariable=service_var)
service_entry.pack(pady=5)

search_button = tk.Button(frame_left, text="Search", command=on_search)
search_button.pack(pady=5)

export_button = tk.Button(frame_left, text="Export Results", command=export_results)
export_button.pack(pady=5)

save_button = tk.Button(frame_left, text="Save Search", command=save_search)
save_button.pack(pady=5)

load_button = tk.Button(frame_left, text="Load Search", command=load_search)
load_button.pack(pady=5)

# Result text box
result_text = tk.Text(frame_right, wrap=tk.WORD, height=25, width=80)
result_text.pack(pady=10, fill=tk.BOTH, expand=True)

# Run the application
root.mainloop()
