import tkinter
import tkintermapview
import customtkinter
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import math
import random
import requests
import threading

# --- MODIFIED: Refined retro color theme ---
THEME = {
    "bg_color": "#BFB9AC",          # Lighter, washed-out paper
    "frame_color": "#A9A294",       # Slightly darker frame bg
    "border_color": "#3D352A",      # Dark brown for borders
    "text_color": "#3D352A",        # Dark brown for text
    "button_color": "#5A6644",      # Muted olive green
    "button_hover": "#78865B",      # Brighter hover olive
    "entry_bg": "#D6D1C7",          # Background for text entry
    "accent_red": "#9A3B3B",        # For shelter line/danger
    "status_ok_bg": "#5A6644",      # Matches button color
    "status_danger_bg": "#9A3B3B",  # Matches accent red
    "map_clear_button": "#4B3F35"
}

customtkinter.set_appearance_mode("Light")

class SafeRouteApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("SafeRoute")
        self.geometry("800x800") 
        
        self.configure(fg_color=THEME["bg_color"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.is_air_raid_active = False

        # --- MODIFIED: Standardized fonts ---
        self.title_font = customtkinter.CTkFont(family="Courier New", size=32, weight="bold")
        self.slogan_font = customtkinter.CTkFont(family="Courier New", size=14)
        self.button_font = customtkinter.CTkFont(family="Courier New", size=14, weight="bold")
        self.status_font = customtkinter.CTkFont(family="Courier New", size=18, weight="bold")
        self.entry_font = customtkinter.CTkFont(family="Courier New", size=12)


        # --- MODIFIED: Header Frame with border ---
        header_frame = customtkinter.CTkFrame(self, fg_color="transparent", 
                                              border_color=THEME["border_color"], border_width=2)
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        title_label = customtkinter.CTkLabel(header_frame, text="SafeRoute", font=self.title_font, text_color=THEME["text_color"])
        title_label.grid(row=0, column=0, pady=(5,0))
        slogan_label = customtkinter.CTkLabel(header_frame, text="Turning fear into survival, one alert at a time.", font=self.slogan_font, text_color=THEME["text_color"])
        slogan_label.grid(row=1, column=0, pady=(0,5))

        # --- MODIFIED: Location Entry Frame styling ---
        location_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        location_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        location_frame.grid_columnconfigure(0, weight=1)
        
        self.address_entry = customtkinter.CTkEntry(
            location_frame, 
            placeholder_text="Enter City or Address...",
            font=self.entry_font,
            fg_color=THEME["entry_bg"],
            border_color=THEME["border_color"],
            text_color=THEME["text_color"],
            border_width=2
        )
        self.address_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.set_location_button = self.create_button(location_frame, "Set Location", self.set_new_location)
        self.set_location_button.grid(row=0, column=1, padx=(5, 0), sticky="e")
        self.address_entry.bind("<Return>", self.set_new_location)

        # --- MODIFIED: Status Frame styling ---
        self.status_frame = customtkinter.CTkFrame(self, fg_color=THEME["status_ok_bg"], corner_radius=0)
        self.status_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.alert_status_label = customtkinter.CTkLabel(
            self.status_frame, text="STATUS: ALL CLEAR", font=self.status_font, text_color="white"
        )
        self.alert_status_label.grid(row=0, column=0, padx=10, pady=10)

        # --- MODIFIED: Map Widget with border ---
        map_frame = customtkinter.CTkFrame(self, fg_color="transparent", 
                                           border_color=THEME["border_color"], border_width=2)
        map_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        map_frame.grid_rowconfigure(0, weight=1)
        map_frame.grid_columnconfigure(0, weight=1)
        self.map_widget = MapWidget(map_frame, corner_radius=0) # Pass map_frame as parent
        self.map_widget.grid(row=0, column=0, sticky="nsew")

        # --- Button Frame ---
        button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.create_button(button_frame, "Report Danger", self.report_danger).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.create_button(button_frame, "Find Hospital", self.find_hospital).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.create_button(button_frame, "Find Shelter", self.find_shelter).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # --- Simulate Button ---
        self.simulate_button = self.create_button(self, "Simulate New Day", self.simulate_day)
        self.simulate_button.grid(row=5, column=0, padx=15, pady=(5, 15), sticky="ew")

        self.fullscreen_state = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

    def toggle_fullscreen(self, event=None):
        self.fullscreen_state = not self.fullscreen_state
        self.attributes("-fullscreen", self.fullscreen_state)
        return "break"

    def exit_fullscreen(self, event=None):
        self.attributes("-fullscreen", False)
        self.fullscreen_state = False
        return "break"

    def set_new_location(self, event=None):
        address = self.address_entry.get()
        if address:
            self.map_widget.update_location(address)
        else:
            messagebox.showwarning("Input Error", "Please enter an address or city.")

    # --- MODIFIED: Button creation with retro styling ---
    def create_button(self, parent, text, command):
        return customtkinter.CTkButton(
            parent, text=text, command=command, font=self.button_font,
            fg_color=THEME["button_color"], hover_color=THEME["button_hover"],
            text_color="white", 
            border_color=THEME["border_color"],
            border_width=2, 
            corner_radius=2  #- Sharp corners
        )

    def report_danger(self):
        if messagebox.askyesno("Confirm Danger Report", "Are you sure you want to report DANGER at your current location?"):
            self.map_widget.add_marker_at_loc_location("danger")

    def find_hospital(self):
        self.map_widget.draw_path_to_nearest("hospital")

    def find_shelter(self):
        self.map_widget.draw_path_to_nearest("shelter")

    def check_event_chance(self, chance):
        return random.random() < chance

    def simulate_day(self):
        print("Simulating a new day...")
        self.is_air_raid_active = False
        self.update_status_banner("STATUS: ALL CLEAR", "ok")
        self.trigger_air_raid()
        for _ in range(random.randint(1, 3)):
            self.generate_random_event()
    
    def trigger_air_raid(self):
        if self.is_air_raid_active: return
        if self.check_event_chance(0.30):
            self.is_air_raid_active = True
            self.update_status_banner("!! AIR RAID IMMINENT !!", "danger")
            self.simulate_button.configure(state=tkinter.DISABLED)
            self.map_widget.draw_air_raid_zone()
            messagebox.showwarning("IMMINENT DANGER", "Air raid sirens detected! Take shelter immediately!")
            self.after(5000, self.end_air_raid)
        else:
            messagebox.showinfo("Status Update", "Threats nearby, stay vigilant!")

    def end_air_raid(self):
        self.is_air_raid_active = False
        self.update_status_banner("STATUS: ALL CLEAR", "ok")
        self.simulate_button.configure(state=tkinter.NORMAL)
        self.map_widget.clear_air_raid_zone()
        messagebox.showinfo("All Clear", "The air raid warning has passed. Remain vigilant.")

    def generate_random_event(self):
        event_types = ["bombers", "fighters", "tanks", "troops"]
        chosen_event = random.choice(event_types)
        lat, lon = self.map_widget.get_position()
        rand_lat, rand_lon = lat + random.uniform(-0.05, 0.05), lon + random.uniform(-0.05, 0.05)
        direction = random.randint(0, 360)
        self.map_widget.create_movement(chosen_event, rand_lat, rand_lon, direction_angle=direction)
        
    def update_status_banner(self, text, status_type):
        color = THEME["status_ok_bg"] if status_type == "ok" else THEME["status_danger_bg"]
        self.status_frame.configure(fg_color=color)
        self.alert_status_label.configure(text=text)

class MapWidget(tkintermapview.TkinterMapView):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.loc_lat, self.loc_lon = 40.7128, -74.0060 # New York, NY

        self.marker_photo_images = []
        self.air_raid_polygon = None
        self.navigation_path = None
        self.zone_polygons = []

        self.clear_button = customtkinter.CTkButton(self, text="X", command=self.clear_map,
                                                      width=30, height=30, font=("Courier New", 14, "bold"),
                                                      fg_color=THEME["map_clear_button"], hover_color=THEME["accent_red"],
                                                      text_color="white",
                                                      border_width=2,
                                                      border_color=THEME["border_color"],
                                                      corner_radius=2)
        self.clear_button.place(x=15, y=80)

        self._load_icons()
        
        # --- MODIFIED: Set to the CARTO Voyager tile server for a light, vintage look ---
        self.set_tile_server("https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png", max_zoom=19)

        self.set_position(self.loc_lat, self.loc_lon)
        self.set_zoom(13)
        self.set_marker(self.loc_lat, self.loc_lon, text="My Location", text_color=THEME["text_color"])
        
    def update_location(self, address: str):
        messagebox.showinfo("Geocoding", f"Searching for {address}...")
        threading.Thread(target=self._geocode_and_update, args=(address,), daemon=True).start()

    def _geocode_and_update(self, address: str):
        url = f"https://nominatim.openstreetmap.org/search?q={address.replace(' ', '+')}&format=json&limit=1"
        headers = {"User-Agent": "SafeRouteApp/1.0"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            results = response.json()
            
            if not results:
                self.after(0, messagebox.showerror, "Error", f"Could not find location: {address}")
                return
            
            new_lat = float(results[0]["lat"])
            new_lon = float(results[0]["lon"])
            
            self.after(0, self._apply_new_location, new_lat, new_lon, results[0]['display_name'])

        except requests.exceptions.RequestException as e:
            self.after(0, messagebox.showerror, "Network Error", f"Could not connect to service: {e}")
    
    def _apply_new_location(self, lat, lon, full_address):
        self.loc_lat = lat
        self.loc_lon = lon
        self.clear_map()
        self.set_position(lat, lon)
        self.set_zoom(13)
        self.set_marker(lat, lon, text="My Location", text_color=THEME["text_color"])
        messagebox.showinfo("Location Updated", f"Map centered on:\n{full_address}")

    def _load_icons(self):
        self.icon_images = {}
        icon_size = (35, 35)
        icon_paths = {
            "troops": "troop.png", "tanks": "tank.png",
            "fighters": "fighter.png", "bombers": "bomber.png",
            "danger": "danger.png", "hospital": "hospital.png", 
            "shelter": "shelter.png"
        }
        for name, path in icon_paths.items():
            if os.path.exists(path):
                self.icon_images[name] = Image.open(path).resize(icon_size)
            else:
                print(f"Warning: Icon '{name}' not found at path '{path}'")
                self.icon_images[name] = None

    def add_marker_at_loc_location(self, marker_type):
        icon = self.icon_images.get(marker_type)
        photo_image = ImageTk.PhotoImage(icon) if icon else None
        if photo_image: self.marker_photo_images.append(photo_image)
        if marker_type == "danger":
            self.create_zone(self.loc_lat, self.loc_lon, radius_m=1600, text="DANGER REPORTED", icon=photo_image)
        else:
            self.set_marker(self.loc_lat, self.loc_lon, icon=photo_image)
        messagebox.showinfo("Report Received", "Danger has been reported, alerting everyone in your area!")

    def create_zone(self, latitude, longitude, radius_m=100, icon=None, text=None, **kwargs):
        circle_polygon = self.set_circle(latitude, longitude, radius_m=radius_m, **kwargs)
        self.zone_polygons.append(circle_polygon)
        if text:
            self.set_marker(latitude, longitude, icon=icon, text_color=kwargs.get("outline_color", "black"))
    
    def clear_map(self):
        if self.navigation_path:
            self.navigation_path.delete()
            self.navigation_path = None
        for zone in self.zone_polygons:
            zone.delete()
        self.zone_polygons.clear()
        self.delete_all_marker()
        self.marker_photo_images.clear()
        self.set_marker(self.loc_lat, self.loc_lon, text="My Location", text_color=THEME["text_color"])
    
    def set_circle(self, latitude, longitude, radius_m=100, num_segments=36, **kwargs):
        polygon_points = []
        lat_diff = radius_m / 111132.0
        lon_diff = radius_m / (111320.0 * abs(math.cos(math.radians(latitude))))
        for i in range(num_segments):
            angle = math.radians(i * (360 / num_segments))
            point_lat = latitude + lat_diff * math.cos(angle)
            point_lon = longitude + lon_diff * math.sin(angle)
            polygon_points.append((point_lat, point_lon))
        return self.set_polygon(polygon_points, fill_color=kwargs.get("fill_color", "yellow"), outline_color=kwargs.get("outline_color", "red"))

    def draw_air_raid_zone(self):
        self.clear_air_raid_zone()
        center_lat, center_lon = self.loc_lat, self.loc_lon
        polygon_points = []
        num_vertices = random.randint(5, 8)
        for i in range(num_vertices):
            angle = math.radians(i * (360 / num_vertices) + random.uniform(-10, 10))
            radius = random.uniform(0.005, 0.015)
            point_lat = center_lat + radius * math.cos(angle)
            point_lon = center_lon + radius * math.sin(angle) * 1.5
            polygon_points.append((point_lat, point_lon))
        self.air_raid_polygon = self.set_polygon(
            polygon_points, fill_color=THEME["accent_red"], outline_color="black", name="air_raid_zone"
        )
    
    def clear_air_raid_zone(self):
        if self.air_raid_polygon is not None:
            self.air_raid_polygon.delete()
            self.air_raid_polygon = None

    def create_movement(self, unit_type, latitude, longitude, direction_angle=0):
        base_image = self.icon_images.get(unit_type)
        if not base_image: return
        rotated_image = base_image.rotate(-direction_angle, expand=True)
        photo_image = ImageTk.PhotoImage(rotated_image)
        self.marker_photo_images.append(photo_image)
        self.set_marker(latitude, longitude, icon=photo_image, icon_anchor="center")
        
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371 
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        a = math.sin(dLat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dLon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def draw_path_to_nearest(self, query):
        messagebox.showinfo("Navigation Search", f"Searching for the nearest '{query}' and calculating route...")
        path_thread = threading.Thread(target=self._find_and_draw_nearest_path, args=(query,), daemon=True)
        path_thread.start()

    def _get_route_from_osrm(self, start_coords, end_coords):
        start_lat, start_lon = start_coords
        end_lat, end_lon = end_coords
        url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data['code'] == 'Ok' and data['routes']:
                route_coords_lon_lat = data['routes'][0]['geometry']['coordinates']
                return [(lat, lon) for lon, lat in route_coords_lon_lat]
            return None
        except requests.exceptions.RequestException as e:
            print(f"OSRM API Error: {e}")
            return None

    def _find_and_draw_nearest_path(self, query):
        if self.navigation_path is not None:
            self.navigation_path.delete()
            self.navigation_path = None
        radius = 0.1
        bbox = f"{self.loc_lon - radius},{self.loc_lat - radius},{self.loc_lon + radius},{self.loc_lat + radius}"
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&viewbox={bbox}&bounded=1"
        headers = {"User-Agent": "SafeRouteApp/1.0"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            results = response.json()
            if not results:
                self.after(0, messagebox.showwarning, "Not Found", f"Could not find any '{query}' locations nearby.")
                return
            nearest_location = min(results, key=lambda r: self._calculate_distance(self.loc_lat, self.loc_lon, float(r["lat"]), float(r["lon"])))
            end_pos = (float(nearest_location["lat"]), float(nearest_location["lon"]))
            route_points = self._get_route_from_osrm((self.loc_lat, self.loc_lon), end_pos)
            if not route_points:
                self.after(0, messagebox.showerror, "Routing Error", "Could not calculate a route. Drawing a straight line instead.")
                route_points = [(self.loc_lat, self.loc_lon), end_pos]
            if query == "hospital": line_color = "#3498db"
            elif query == "shelter": line_color = THEME["accent_red"]
            else: line_color = "#f1c40f"
            icon = ImageTk.PhotoImage(self.icon_images.get(query)) if self.icon_images.get(query) else None
            if icon: self.marker_photo_images.append(icon)
            def draw_on_main_thread():
                self.navigation_path = self.set_path(route_points, color=line_color, width=4)
                self.set_marker(end_pos[0], end_pos[1], icon=icon, text=f"Nearest: {nearest_location['display_name'].split(',')[0]}")
            self.after(0, draw_on_main_thread)
        except requests.exceptions.RequestException as e:
            self.after(0, messagebox.showerror, "Search Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app = SafeRouteApp()
    app.mainloop()