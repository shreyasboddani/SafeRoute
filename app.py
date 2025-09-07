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
import time

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
        self.geometry("1000x800")

        self.configure(fg_color=THEME["bg_color"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.is_air_raid_active = False

        # --- Resource Management ---
        self.food = 100
        self.water = 100
        self.medical = 100
        self.low_med_warning_shown = False


        # --- MODIFIED: Standardized fonts ---
        self.title_font = customtkinter.CTkFont(family="Courier New", size=32, weight="bold")
        self.slogan_font = customtkinter.CTkFont(family="Courier New", size=14)
        self.button_font = customtkinter.CTkFont(family="Courier New", size=14, weight="bold")
        self.status_font = customtkinter.CTkFont(family="Courier New", size=18, weight="bold")
        self.entry_font = customtkinter.CTkFont(family="Courier New", size=12)
        self.resource_font = customtkinter.CTkFont(family="Courier New", size=12)


        # --- MODIFIED: Header Frame with border ---
        header_frame = customtkinter.CTkFrame(self, fg_color="transparent",
                                              border_color=THEME["border_color"], border_width=2)
        header_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        title_label = customtkinter.CTkLabel(header_frame, text="SafeRoute", font=self.title_font, text_color=THEME["text_color"])
        title_label.grid(row=0, column=0, pady=(5,0))
        slogan_label = customtkinter.CTkLabel(header_frame, text="Turning fear into survival, one alert at a time.", font=self.slogan_font, text_color=THEME["text_color"])
        slogan_label.grid(row=1, column=0, pady=(0,5))

        # --- MODIFIED: Location Entry Frame styling ---
        location_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        location_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
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
        self.status_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.alert_status_label = customtkinter.CTkLabel(
            self.status_frame, text="STATUS: ALL CLEAR", font=self.status_font, text_color="white"
        )
        self.alert_status_label.grid(row=0, column=0, padx=10, pady=10)

        # --- MODIFIED: Map Widget with border ---
        map_frame = customtkinter.CTkFrame(self, fg_color="transparent",
                                           border_color=THEME["border_color"], border_width=2)
        map_frame.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        map_frame.grid_rowconfigure(0, weight=1)
        map_frame.grid_columnconfigure(0, weight=1)
        self.map_widget = MapWidget(map_frame, app=self, corner_radius=0)
        self.map_widget.grid(row=0, column=0, sticky="nsew")
        
        # --- Control Panel ---
        control_panel = customtkinter.CTkFrame(self, fg_color="transparent")
        control_panel.grid(row=3, column=0, padx=10, pady=5, sticky="ns")
        
        # --- Resource Management ---
        resource_frame = customtkinter.CTkFrame(control_panel, fg_color=THEME["frame_color"], border_color=THEME["border_color"], border_width=2)
        resource_frame.pack(padx=5, pady=5, fill="x")
        resource_label = customtkinter.CTkLabel(resource_frame, text="Resources", font=self.button_font, text_color=THEME["text_color"])
        resource_label.pack(pady=5)
        
        self.food_label = customtkinter.CTkLabel(resource_frame, text=f"Food: {self.food}%", font=self.resource_font, text_color=THEME["text_color"])
        self.food_label.pack(pady=2)
        self.water_label = customtkinter.CTkLabel(resource_frame, text=f"Water: {self.water}%", font=self.resource_font, text_color=THEME["text_color"])
        self.water_label.pack(pady=2)
        self.med_label = customtkinter.CTkLabel(resource_frame, text=f"Medical: {self.medical}%", font=self.resource_font, text_color=THEME["text_color"])
        self.med_label.pack(pady=2)

        # --- Time and Weather ---
        time_weather_frame = customtkinter.CTkFrame(control_panel, fg_color=THEME["frame_color"], border_color=THEME["border_color"], border_width=2)
        time_weather_frame.pack(padx=5, pady=5, fill="x")
        self.time_label = customtkinter.CTkLabel(time_weather_frame, text="Time: 08:00", font=self.resource_font, text_color=THEME["text_color"])
        self.time_label.pack(pady=2)
        self.weather_label = customtkinter.CTkLabel(time_weather_frame, text="Weather: Clear", font=self.resource_font, text_color=THEME["text_color"])
        self.weather_label.pack(pady=2)


        # --- Button Frame ---
        button_frame = customtkinter.CTkFrame(control_panel, fg_color="transparent")
        button_frame.pack(padx=5, pady=10, fill="x")

        self.create_button(button_frame, "Report Danger", self.report_danger).pack(padx=5, pady=5, fill="x")
        self.create_button(button_frame, "Find Hospital", self.find_hospital).pack(padx=5, pady=5, fill="x")
        self.create_button(button_frame, "Find Shelter", self.find_shelter).pack(padx=5, pady=5, fill="x")

        # --- Simulate Button ---
        self.simulate_button = self.create_button(self, "Simulate New Day", self.simulate_day)
        self.simulate_button.grid(row=5, column=0, columnspan=2, padx=15, pady=(5, 15), sticky="ew")

        self.fullscreen_state = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)
        
        self.update_resources()

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

    def create_button(self, parent, text, command):
        return customtkinter.CTkButton(
            parent, text=text, command=command, font=self.button_font,
            fg_color=THEME["button_color"], hover_color=THEME["button_hover"],
            text_color="white",
            border_color=THEME["border_color"],
            border_width=2,
            corner_radius=2
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
        self.update_time_and_weather()
        for _ in range(random.randint(1, 2)):
            self.generate_random_event()
        self.generate_supply_drop()


    def trigger_air_raid(self):
        if self.is_air_raid_active: return
        if self.check_event_chance(0.30):
            self.is_air_raid_active = True
            self.update_status_banner("!! AIR RAID IMMINENT !!", "danger")
            self.simulate_button.configure(state=tkinter.DISABLED)
            self.map_widget.draw_air_raid_zone()
            self.map_widget.spawn_air_raid_planes(50)
            messagebox.showwarning("IMMINENT DANGER", "Air raid sirens detected! Take shelter immediately!")
            self.after(15000, self.end_air_raid)
        else:
            messagebox.showinfo("Status Update", "Threats nearby, stay vigilant!")

    def end_air_raid(self):
        self.is_air_raid_active = False
        self.update_status_banner("STATUS: ALL CLEAR", "ok")
        self.simulate_button.configure(state=tkinter.NORMAL)
        self.map_widget.clear_air_raid_zone()
        self.map_widget.clear_air_raid_planes()
        messagebox.showinfo("All Clear", "The air raid warning has passed. Remain vigilant.")

    def generate_random_event(self):
        event_types = ["tanks", "troops"]
        chosen_event = random.choice(event_types)
        threading.Thread(target=self.map_widget.place_event_on_land, args=(chosen_event,), daemon=True).start()
        
    def generate_supply_drop(self):
        if self.check_event_chance(0.40):
             threading.Thread(target=self.map_widget.place_event_on_land, args=("supply_drop",), daemon=True).start()


    def update_time_and_weather(self):
        current_time = self.time_label.cget("text").split(" ")[1]
        hour = int(current_time.split(":")[0])
        new_hour = (hour + random.randint(4, 8)) % 24
        self.time_label.configure(text=f"Time: {new_hour:02d}:00")

        weather_conditions = ["Clear", "Rainy", "Foggy"]
        new_weather = random.choice(weather_conditions)
        self.weather_label.configure(text=f"Weather: {new_weather}")

    def update_resources(self):
        self.food = max(0, self.food - random.uniform(0.1, 0.5))
        self.water = max(0, self.water - random.uniform(0.2, 0.6))
        self.medical = max(0, self.medical - random.uniform(0.05, 0.2))

        self.food_label.configure(text=f"Food: {int(self.food)}%")
        self.water_label.configure(text=f"Water: {int(self.water)}%")
        self.med_label.configure(text=f"Medical: {int(self.medical)}%")

        if self.medical < 25 and not self.low_med_warning_shown:
            self.low_med_warning_shown = True
            messagebox.showwarning("Low Supplies", "Medical supplies are critically low! Find a hospital or supply drop soon.")
            self.update_status_banner("WARNING: LOW MEDICAL SUPPLIES", "danger")
        elif self.medical >= 25 and self.low_med_warning_shown:
            self.low_med_warning_shown = False
            if not self.is_air_raid_active:
                self.update_status_banner("STATUS: ALL CLEAR", "ok")

        self.after(5000, self.update_resources)

    def replenish_resources(self):
        self.food = 100
        self.water = 100
        self.medical = 100
        messagebox.showinfo("Supplies Replenished", "You have restocked your food, water, and medical supplies.")
        if self.low_med_warning_shown:
            self.low_med_warning_shown = False
            if not self.is_air_raid_active:
                self.update_status_banner("STATUS: ALL CLEAR", "ok")


    def update_status_banner(self, text, status_type):
        color = THEME["status_ok_bg"] if status_type == "ok" else THEME["status_danger_bg"]
        self.status_frame.configure(fg_color=color)
        self.alert_status_label.configure(text=text)

class MapWidget(tkintermapview.TkinterMapView):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.loc_lat, self.loc_lon = 40.7128, -74.0060

        self.marker_photo_images = []
        self.air_raid_polygon = None
        self.navigation_path = None
        self.zone_polygons = []
        self.air_raid_planes = {}
        self.patrolling_units = {}

        self.clear_button = customtkinter.CTkButton(self, text="X", command=self.clear_map,
                                                      width=30, height=30, font=("Courier New", 14, "bold"),
                                                      fg_color=THEME["map_clear_button"], hover_color=THEME["accent_red"],
                                                      text_color="white",
                                                      border_width=2,
                                                      border_color=THEME["border_color"],
                                                      corner_radius=2)
        self.clear_button.place(x=20, y=100)

        self._load_icons()

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
        icon_paths = {
            "troops": "troop.png", "tanks": "tank.png",
            "fighters": "fighter.png", "bombers": "bomber.png",
            "danger": "danger.png", "hospital": "hospital.png",
            "shelter": "shelter.png", "supply_drop": "supply_drop.png"
        }
        for name, path in icon_paths.items():
            if os.path.exists(path):
                img = Image.open(path)
                self.icon_images[name] = {
                    "base": img,
                    "default": img.resize((35, 35)),
                    "small": img.resize((20, 20))
                }
            else:
                print(f"Warning: Icon '{name}' not found at path '{path}'")
                self.icon_images[name] = None

    def add_marker_at_loc_location(self, marker_type, lat=None, lon=None):
        if lat is None: lat = self.loc_lat
        if lon is None: lon = self.loc_lon
            
        icon_set = self.icon_images.get(marker_type)
        if not icon_set: return
        
        icon = icon_set["default"]
        photo_image = ImageTk.PhotoImage(icon)
        self.marker_photo_images.append(photo_image)
        
        if marker_type == "danger":
            self.create_zone(lat, lon, radius_m=400, text="DANGER REPORTED", icon=photo_image)
            messagebox.showinfo("Report Received", "Danger reported, alerting everyone in your area!")
        elif marker_type == "supply_drop":
            self.set_marker(lat, lon, text="Supply Drop", icon=photo_image)
            if messagebox.askyesno("Supply Drop", "A supply drop is nearby. Get directions?"):
                self.draw_path_to_point((lat, lon))
                self.app.replenish_resources()
        else:
            self.set_marker(lat, lon, icon=photo_image)

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
        self.patrolling_units.clear()
        self.clear_air_raid_planes()
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
    
    def _is_point_in_polygon(self, point, polygon_vertices):
        lat, lon = point
        n = len(polygon_vertices)
        inside = False
        p1_lat, p1_lon = polygon_vertices[0]
        for i in range(n + 1):
            p2_lat, p2_lon = polygon_vertices[i % n]
            if lon > min(p1_lon, p2_lon):
                if lon <= max(p1_lon, p2_lon):
                    if lat <= max(p1_lat, p2_lat):
                        if p1_lon != p2_lon:
                            lat_intersection = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                        if p1_lat == p2_lat or lat <= lat_intersection:
                            inside = not inside
            p1_lat, p1_lon = p2_lat, p2_lon
        return inside
            
    def spawn_air_raid_planes(self, count=50):
        if not self.air_raid_polygon: return

        min_lat = min(p[0] for p in self.air_raid_polygon.position_list)
        max_lat = max(p[0] for p in self.air_raid_polygon.position_list)
        min_lon = min(p[1] for p in self.air_raid_polygon.position_list)
        max_lon = max(p[1] for p in self.air_raid_polygon.position_list)
        
        icon_set = self.icon_images.get("bombers")
        if not icon_set: return
        
        small_icon_base = icon_set["small"]

        for _ in range(count):
            rand_lat = random.uniform(min_lat, max_lat)
            rand_lon = random.uniform(min_lon, max_lon)
            
            if self._is_point_in_polygon((rand_lat, rand_lon), self.air_raid_polygon.position_list):
                angle = random.randint(0, 360)
                photo_image = ImageTk.PhotoImage(small_icon_base.rotate(angle, expand=True))
                self.marker_photo_images.append(photo_image)
                marker = self.set_marker(rand_lat, rand_lon, icon=photo_image, icon_anchor="center")
                self.air_raid_planes[marker] = (angle, 20)
                self.patrol_in_zone(marker)
            
    def patrol_in_zone(self, marker, speed=0.0002):
        if self.air_raid_polygon is None or marker not in self.canvas_marker_list or marker not in self.air_raid_planes:
            if marker in self.air_raid_planes:
                del self.air_raid_planes[marker]
            return

        angle, steps_before_check = self.air_raid_planes[marker]
        
        lat, lon = marker.position
        rad_angle = math.radians(angle)
        
        new_lat = lat - speed * math.cos(rad_angle) 
        new_lon = lon + speed * math.sin(rad_angle)
        
        steps_before_check -= 1
        new_angle = angle

        if steps_before_check <= 0:
            if not self._is_point_in_polygon((new_lat, new_lon), self.air_raid_polygon.position_list):
                new_angle = (angle + 180 + random.randint(-45, 45)) % 360
                
                # Rotate image to new direction
                icon_set = self.icon_images.get("bombers")
                if icon_set:
                    new_photo = ImageTk.PhotoImage(icon_set["small"].rotate(new_angle, expand=True))
                    self.marker_photo_images.append(new_photo)
                    marker.change_icon(new_photo)
            steps_before_check = 20

        marker.set_position(new_lat, new_lon)
        self.air_raid_planes[marker] = (new_angle, steps_before_check)
        self.after(50, lambda: self.patrol_in_zone(marker, speed))

            
    def clear_air_raid_planes(self):
        for marker in list(self.air_raid_planes.keys()):
            marker.delete()
        self.air_raid_planes.clear()


    def create_movement(self, unit_type, latitude, longitude, direction_angle=0):
        icon_set = self.icon_images.get(unit_type)
        if not icon_set: return
        base_image = icon_set["default"]
        
        rotated_image = base_image.rotate(-direction_angle, expand=True)
        photo_image = ImageTk.PhotoImage(rotated_image)
        self.marker_photo_images.append(photo_image)
        marker = self.set_marker(latitude, longitude, icon=photo_image, icon_anchor="center")
        
        if unit_type in ["tanks", "troops"]:
            self.start_patrol(marker, unit_type)

    def start_patrol(self, marker, unit_type):
        start_lat, start_lon = marker.position
        target_lat = start_lat + random.uniform(-0.02, 0.02)
        target_lon = start_lon + random.uniform(-0.02, 0.02)
        self.patrolling_units[marker] = (target_lat, target_lon, unit_type)
        self.update_patrol_position(marker)

    def update_patrol_position(self, marker, speed=0.0001):
        if marker not in self.canvas_marker_list or marker not in self.patrolling_units:
            if marker in self.patrolling_units:
                del self.patrolling_units[marker]
            return

        target_lat, target_lon, unit_type = self.patrolling_units[marker]
        current_lat, current_lon = marker.position

        distance = self._calculate_distance(current_lat, current_lon, target_lat, target_lon)

        if distance < 0.01:
            self.start_patrol(marker, unit_type)
            return
            
        angle_rad = math.atan2(target_lon - current_lon, target_lat - current_lat)
        angle_deg = math.degrees(angle_rad)

        # Rotate the icon to face the direction of movement
        icon_set = self.icon_images.get(unit_type)
        if icon_set:
            rotated_image = icon_set["base"].resize((35,35)).rotate(-angle_deg + 90, expand=True)
            photo_image = ImageTk.PhotoImage(rotated_image)
            marker.change_icon(photo_image)
            self.marker_photo_images.append(photo_image) # Keep reference

        new_lat = current_lat + speed * math.sin(angle_rad)
        new_lon = current_lon + speed * math.cos(angle_rad)
        marker.set_position(new_lat, new_lon)

        self.after(100, lambda: self.update_patrol_position(marker, speed))

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
        threading.Thread(target=self._find_and_draw_nearest_path, args=(query,), daemon=True).start()
        
    def draw_path_to_point(self, end_pos):
        if self.navigation_path is not None:
            self.navigation_path.delete()
            self.navigation_path = None
        
        route_points = self._get_route_from_osrm((self.loc_lat, self.loc_lon), end_pos)
        if not route_points:
            self.after(0, messagebox.showerror, "Routing Error", "Could not calculate a route. Drawing a straight line instead.")
            route_points = [(self.loc_lat, self.loc_lon), end_pos]
            
        def draw_on_main_thread():
            self.navigation_path = self.set_path(route_points, color=THEME["button_color"], width=4)
        
        self.after(0, draw_on_main_thread)


    def _get_route_from_osrm(self, start_coords, end_coords):
        start_lat, start_lon = start_coords
        end_lat, end_lon = end_coords
        url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 'Ok' and data.get('routes'):
                route_coords = data['routes'][0]['geometry']['coordinates']
                return [(lat, lon) for lon, lat in route_coords]
            return None
        except requests.exceptions.RequestException as e:
            print(f"OSRM API Error: {e}")
            return None
            
    def _is_water(self, lat, lon):
        url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
        headers = {"User-Agent": "SafeRouteApp/1.0"}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()

            if 'error' in data:
                return 'Unable to geocode' in data.get('error', '')
            
            category = data.get('category')
            osm_type = data.get('type')
            
            water_categories = ['water', 'waterway']
            water_types = ['river', 'riverbank', 'lake', 'sea', 'ocean', 'coastline', 'bay', 'strait']
            
            return category in water_categories or osm_type in water_types

        except requests.exceptions.RequestException as e:
            print(f"API Error in _is_water check: {e}")
            return True

    def place_event_on_land(self, event_type):
        max_retries = 10
        for i in range(max_retries):
            lat, lon = self.get_position()
            rand_lat = lat + random.uniform(-0.05, 0.05)
            rand_lon = lon + random.uniform(-0.05, 0.05)
            
            if not self._is_water(rand_lat, rand_lon):
                direction = random.randint(0, 360)
                if event_type == "supply_drop":
                     self.after(0, self.add_marker_at_loc_location, event_type, rand_lat, rand_lon)
                else:
                    self.after(0, self.create_movement, event_type, rand_lat, rand_lon, direction)
                return
            else:
                print(f"Attempt {i+1}: Found water at ({rand_lat:.4f}, {rand_lon:.4f}). Retrying...")
        
        print(f"Could not find a land location for {event_type} after {max_retries} tries.")


    def _find_and_draw_nearest_path(self, query):
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
            
            self.draw_path_to_point(end_pos)
            
            icon_set = self.icon_images.get(query)
            icon = ImageTk.PhotoImage(icon_set["default"]) if icon_set else None
            if icon: self.marker_photo_images.append(icon)

            def draw_on_main_thread():
                self.set_marker(end_pos[0], end_pos[1], icon=icon, text=f"Nearest: {nearest_location['display_name'].split(',')[0]}")
            self.after(0, draw_on_main_thread)
        except requests.exceptions.RequestException as e:
            self.after(0, messagebox.showerror, "Search Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app = SafeRouteApp()
    app.mainloop()
