# SafeRoute – WWII Simulation Mapping Tool

**Hack Forsyth Hackathon Project (Forsyth County)**
_Created by Shreyas Boddani, Shourya Mishra, and Brandon Potter_

SafeRoute is a simulation project developed during the inaugural Hack Forsyth hackathon, where teams had 24 hours to build projects inspired by historical contexts before the 1980s. Our team focused on **World War II**, designing an interactive tool that imagines how modern mapping and routing technology might have helped civilians survive during wartime.

The project is not powered by historical datasets. Instead, it simulates how civilians could manage resources, evade dynamic threats, and find safe passage in a challenging WWII-style scenario.

---

## Features

-   **Global Location Search:** Enter any location (e.g., “London” or “Berlin”) to center the map.
-   **Dynamic Unit Movement:** Ground units like tanks and troops patrol the map, while air units perform fly-bys. All units are oriented in their direction of travel for added realism.
-   **Resource Management:** Your food, water, and medical supplies deplete over time, adding a survival element. Low-supply warnings will alert you to seek resources.
-   **Air Raid Swarms:** During an air raid, bomber planes will swarm and patrol within the designated danger zone, creating a visually intense event.
-   **Time and Weather System:** A day/night cycle and changing weather conditions (clear, rainy, foggy) affect visibility and the overall atmosphere.
-   **Shelter & Hospital Routing:** Calculate and display safe paths to nearby hospitals or shelters.
-   **Immersive UI:** Retro-inspired 1940s visuals with alert banners and muted wartime colors.

---

## Technologies Used

-   **Languages & Frameworks:** Python, Tkinter, CustomTkinter
-   **Mapping:** tkintermapview, OpenStreetMap Nominatim API (geocoding), OSRM (routing)
-   **Graphics:** Pillow (PIL)
-   **Logic:** Threading for smooth, non-blocking simulation updates

---

## Usage

-   **Launch the program**
-   **Search Locations:** Type any city or place name into the search bar to center the map.
-   **Manage Resources:** Keep an eye on your resource panel. When supplies get low, find a hospital or a supply drop.
-   **Observe Dynamic Events:** Watch for moving enemy patrols. Their icons will rotate to show their direction of travel.
-   **Survive Air Raids:** When the siren sounds, find shelter! The map will show the danger zone filled with patrolling bombers.
-   **Find Supply Drops:** When a supply drop appears, click "Yes" on the prompt to get directions and automatically replenish your supplies.
-   **Find Routes:** Use the routing buttons to locate the nearest hospitals or shelters.
-   **Simulate New Day:** Click the “Simulate New Day” button to advance time and generate new random events.

---

## Future Improvements

-   Integrate historical datasets for more realistic WWII scenarios.
-   Add more types of safe zones (e.g., bunkers, supply caches).
-   Expand simulation events, like artillery strikes or propaganda drops.
-   Improve UI responsiveness and add map overlays for historical front lines.
-   Deploy as a standalone desktop application or web app for easier access.

---

## Acknowledgments

-   Developed during the inaugural **Hack Forsyth Hackathon (2025)**.
-   Inspired by civilian resilience during WWII and the potential impact of modern technology on survival strategies.
-   **Team Members:** Shreyas Boddani, Shourya Mishra, Brandon Potter
