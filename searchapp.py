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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Retrieve the Shodan API key from environment variables
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')

if not SHODAN_API_KEY:
    raise ValueError("Please set the SHODAN_API_KEY environment variable")

# Initialize the Shodan API client
api = shodan.Shodan(SHODAN_API_KEY)
geolocator = Nominatim(user_agent="shodan_gui")

# Global variable to keep track of the current page
current_page = 1
results_per_page = 10
total_results = 0
results = []

def search_shodan(query, country_code, port, service, hostname, vuln, page=1):
    global total_results, results
    try:
        # Build the search query with additional filters
        if country_code:
            query += f' country:{country_code}'
        if port:
            query += f' port:{port}'
        if service:
            query += f' {service}'
        if hostname:
            query += f' hostname:{hostname}'
        if vuln:
            query += f' vuln:{vuln}'
        
        results = api.search(query, page=page)
        total_results = results['total']
        result_text.delete(1.0, tk.END)  # Clear previous results
        result_text.insert(tk.END, f'Results found: {total_results}\n\n')
        for result in results['matches']:
            org_str = result.get("org", "Unknown Organization")
            city = result.get("location", {}).get("city", "Unknown City")
            state = result.get("location", {}).get("region_code", "Unknown State")
            ip_str = result["ip_str"]
            start = result_text.index(tk.END)
            result_text.insert(tk.END, f'{org_str}\n{city}, {state}\n\n')
            end = result_text.index(tk.END)
            result_text.tag_add(ip_str, start, end)
            result_text.tag_config(ip_str, foreground="blue", underline=True)
            result_text.tag_bind(ip_str, "<Button-1>", lambda e, ip=ip_str: show_host_info(ip))
        
        update_pagination_controls()
    except shodan.APIError as e:
        messagebox.showerror("Error", f'Shodan API error: {e}')

def update_pagination_controls():
    global current_page, total_results, results_per_page
    total_pages = (total_results + results_per_page - 1) // results_per_page
    pagination_label.config(text=f"Page {current_page} of {total_pages}")
    prev_button.config(state=tk.NORMAL if current_page > 1 else tk.DISABLED)
    next_button.config(state=tk.NORMAL if current_page < total_pages else tk.DISABLED)

def on_search():
    global current_page
    current_page = 1
    query = search_var.get()
    country_code = country_var.get()
    port = port_var.get()
    service = service_var.get()
    hostname = hostname_var.get()
    vuln = vuln_var.get()
    search_shodan(query, country_code, port, service, hostname, vuln, page=current_page)

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
                map_data.seek(0)
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
        "service": service_var.get(),
        "hostname": hostname_var.get(),
        "vuln": vuln_var.get()
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
        hostname_var.set(search_query.get("hostname", ""))
        vuln_var.set(search_query.get("vuln", ""))

def prev_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        query = search_var.get()
        country_code = country_var.get()
        port = port_var.get()
        service = service_var.get()
        hostname = hostname_var.get()
        vuln = vuln_var.get()
        search_shodan(query, country_code, port, service, hostname, vuln, page=current_page)

def next_page():
    global current_page
    total_pages = (total_results + results_per_page - 1) // results_per_page
    if current_page < total_pages:
        current_page += 1
        query = search_var.get()
        country_code = country_var.get()
        port = port_var.get()
        service = service_var.get()
        hostname = hostname_var.get()
        vuln = vuln_var.get()
        search_shodan(query, country_code, port, service, hostname, vuln, page=current_page)

def show_map():
    if not results:
        messagebox.showwarning("Warning", "No results to show on map.")
        return

    map_window = tk.Toplevel(root)
    map_window.title("Geographical Distribution of Search Results")
    map_center = [0, 0]
    result_map = folium.Map(location=map_center, zoom_start=2)

    for result in results['matches']:
        lat = result.get("location", {}).get("latitude")
        lon = result.get("location", {}).get("longitude")
        if lat and lon:
            org_str = result.get("org", "Unknown Organization")
            folium.Marker([lat, lon], popup=org_str).add_to(result_map)

    map_data = BytesIO()
    result_map.save(map_data, close_file=False)
    map_data.seek(0)
    map_image = Image.open(map_data)
    map_photo = ImageTk.PhotoImage(map_image)
    map_label = tk.Label(map_window, image=map_photo)
    map_label.image = map_photo  # Keep a reference to avoid garbage collection
    map_label.pack(pady=10)

def show_graph():
    if not results:
        messagebox.showwarning("Warning", "No data to display.")
        return

    services = {}
    countries = {}
    ports = {}

    for result in results['matches']:
        service = result.get("product", "Unknown Service")
        country = result.get("location", {}).get("country_name", "Unknown Country")
        port = result.get("port")

        services[service] = services.get(service, 0) + 1
        countries[country] = countries.get(country, 0) + 1
        ports[port] = ports.get(port, 0) + 1

    graph_window = tk.Toplevel(root)
    graph_window.title("Graphical Representation of Data")

    fig, ax = plt.subplots(3, 1, figsize=(10, 15))

    ax[0].bar(services.keys(), services.values(), color='blue')
    ax[0].set_title('Distribution of Services')
    ax[0].set_xlabel('Services')
    ax[0].set_ylabel('Count')

    ax[1].bar(countries.keys(), countries.values(), color='green')
    ax[1].set_title('Distribution of Countries')
    ax[1].set_xlabel('Countries')
    ax[1].set_ylabel('Count')

    ax[2].bar(ports.keys(), ports.values(), color='red')
    ax[2].set_title('Distribution of Ports')
    ax[2].set_xlabel('Ports')
    ax[2].set_ylabel('Count')

    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Create main window
root = tk.Tk()
root.title("Shodan Search GUI")
root.geometry("1200x700")

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

hostname_label = tk.Label(frame_left, text="Hostname:")
hostname_label.pack(pady=5)

hostname_var = tk.StringVar()
hostname_entry = tk.Entry(frame_left, textvariable=hostname_var)
hostname_entry.pack(pady=5)

vuln_label = tk.Label(frame_left, text="Vulnerability:")
vuln_label.pack(pady=5)

vuln_var = tk.StringVar()
vuln_entry = tk.Entry(frame_left, textvariable=vuln_var)
vuln_entry.pack(pady=5)

search_button = tk.Button(frame_left, text="Search", command=on_search)
search_button.pack(pady=5)

export_button = tk.Button(frame_left, text="Export Results", command=export_results)
export_button.pack(pady=5)

save_button = tk.Button(frame_left, text="Save Search", command=save_search)
save_button.pack(pady=5)

load_button = tk.Button(frame_left, text="Load Search", command=load_search)
load_button.pack(pady=5)

map_button = tk.Button(frame_left, text="Show Map", command=show_map)
map_button.pack(pady=5)

graph_button = tk.Button(frame_left, text="Show Graph", command=show_graph)
graph_button.pack(pady=5)

# Result text box
result_text = tk.Text(frame_right, wrap=tk.WORD, height=25, width=80)
result_text.pack(pady=10, fill=tk.BOTH, expand=True)

# Pagination controls
pagination_frame = tk.Frame(frame_right)
pagination_frame.pack(pady=5)

prev_button = tk.Button(pagination_frame, text="Previous", command=prev_page)
prev_button.pack(side=tk.LEFT, padx=5)

pagination_label = tk.Label(pagination_frame, text="")
pagination_label.pack(side=tk.LEFT, padx=5)

next_button = tk.Button(pagination_frame, text="Next", command=next_page)
next_button.pack(side=tk.LEFT, padx=5)

# Run the application
root.mainloop()
