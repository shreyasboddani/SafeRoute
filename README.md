# SafeRoute – WWII Simulation Mapping Tool

**Hack Forsyth Hackathon Project (Denmark High School, Forsyth County)**  
_Created by Shreyas Boddani, Shourya Mishra, and Brandon Potter_

SafeRoute is a simulation project developed during the inaugural Hack Forsyth hackathon, where teams had 24 hours to build projects inspired by historical contexts before the 1980s. Our team focused on **World War II**, designing an interactive tool that imagines how modern mapping and routing technology might have helped civilians survive during wartime.

The project is not powered by historical datasets. Instead, it simulates how civilians could mark unsafe areas, search for locations, and find routes to shelters or hospitals in a WWII-style scenario.

---

## Features

- **Global Location Search:** Enter any location (e.g., “London” or “Berlin”) to center the map.  
- **Danger Zone Marking:** Highlight unsafe areas to simulate bombings, troop advances, or restricted zones.  
- **Shelter & Hospital Routing:** Calculate and display safe paths to nearby hospitals or shelters.  
- **Daily Simulation:** Use the “Simulate New Day” button to generate randomized wartime events, such as air raids or advancing forces.  
- **Immersive UI:** Retro-inspired 1940s visuals with alert banners and muted wartime colors.  
- **Threaded Updates:** Background processes allow events to update dynamically without freezing the interface.  

---

## Technologies Used

- **Languages & Frameworks:** Python, Tkinter, CustomTkinter  
- **Mapping:** tkintermapview, OpenStreetMap Nominatim API (geocoding), OSRM (routing)  
- **Graphics:** Pillow (PIL)  
- **Logic:** Threading for smooth simulation updates 

---

## Usage

- **Launch the program**  
- **Search Locations:** Type any city or place name into the search bar to center the map.  
- **Mark Danger Zones:** Click to mark unsafe areas and simulate bombings or restricted zones.  
- **Find Routes:** Use the routing tool to locate the nearest hospitals or shelters.  
- **Simulate New Day:** Click the “Simulate New Day” button to generate randomized wartime events, such as air raids or troop movements.  
- **Observe Dynamic Changes:** The map updates dynamically without freezing, simulating evolving scenarios.  

---

## Future Improvements

- Integrate historical datasets for more realistic WWII scenarios.  
- Add more types of safe zones (schools, bunkers, supply points).  
- Expand simulation events beyond bombing and troop movement.  
- Improve UI responsiveness and add map overlays for troop lines or air raid zones.  
- Deploy as a standalone desktop application or web app for easier access.  

---

## Acknowledgments

- Developed during the inaugural **Hack Forsyth Hackathon (2025)**.  
- Inspired by civilian resilience during WWII and the potential impact of modern technology on survival strategies.  
- **Team Members:** Shreyas Boddani, Shourya Mishra, Brandon Potter
