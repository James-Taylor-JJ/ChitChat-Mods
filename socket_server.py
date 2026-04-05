import logging
import socket
import threading

logging.basicConfig(filename="chitchat_server.log", level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

def get_weather(city):
    """Return a weather string for the given city, or an error message."""
    try:
        # Step 1: geocode the city name to lat/lon
        geo_url = ("https://geocoding-api.open-meteo.com/v1/search?"
                   + urllib.parse.urlencode({"name": city, "count": 1, "language": "en", "format": "json"}))
        with urllib.request.urlopen(geo_url, timeout=5) as r:
            geo = json.loads(r.read())
 
        if not geo.get("results"):
            return f'** Bot: city "{city}" not found. **'
 
        result = geo["results"][0]
        lat, lon, name = result["latitude"], result["longitude"], result["name"]
        country = result.get("country", "")
 
        # Step 2: fetch current weather for that lat/lon
        wx_url = ("https://api.open-meteo.com/v1/forecast?"
                  + urllib.parse.urlencode({
                      "latitude": lat, "longitude": lon,
                      "current": "temperature_2m,wind_speed_10m,weathercode",
                      "wind_speed_unit": "kmh", "format": "json",
                  }))
        with urllib.request.urlopen(wx_url, timeout=5) as r:
            wx = json.loads(r.read())
 
        current = wx["current"]
        temp = current["temperature_2m"]
        wind = current["wind_speed_10m"]
        code = current["weathercode"]
 
        # WMO weather codes -> readable description
        conditions = {
            0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
            45: "fog", 48: "icy fog", 51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
            61: "light rain", 63: "rain", 65: "heavy rain",
            71: "light snow", 73: "snow", 75: "heavy snow",
            80: "rain showers", 81: "heavy showers", 82: "violent showers",
            95: "thunderstorm", 96: "thunderstorm with hail",
        }
        description = conditions.get(code, f"code {code}")
 
        return f"** Bot: Weather in {name}, {country}: {temp}°C, {description}, wind {wind} km/h **"
 
    except Exception as e:
        return f"** Bot: could not fetch weather ({e}) **"

class ServerThread(threading.Thread):
    def __init__(self, server, client_socket):
        super().__init__(daemon=True)
        self.server = server
        self.client_socket = client_socket
        self.name_label = None
        self.reader = client_socket.makefile(mode="r", buffering=1, encoding="utf-8")
        self.writer = client_socket.makefile(mode="w", buffering=1, encoding="utf-8")

    def send(self, message):
        self.writer.write(message + "\n")
        self.writer.flush()

    def run(self):
        try:
            self.name_label = self.reader.readline().strip()
            self.server.broadcast(f"**[{self.name_label}] Entered**")
            logging.info("CONNECT | %s", self.name_label)
            self.server.broadcast(f"**[{self.name_label}] Entered**")
            
            for data in self.reader:
                data = data.strip()
                if data == "/users":
                    with self.server.lock:
                        names = [c.name_label for c in self.server.clients]
                    self.send("**Users: " + ", ".join(names) + "**")
                else:
                    logging.info("MESSAGE | %s: %s", self.name_label, data)
                    self.server.broadcast(f"[{self.name_label}] {data}")
        except Exception as e:
            print(f"Error handling client communication: {e} ---->")
        finally:
            self.server.remove_thread(self)
            self.server.broadcast(f"**[{self.name_label}] Left**")
            logging.info("DISCONNECT | %s", self.name_label)
            try:
                print(f"{self.client_socket.getpeername()} - [{self.name_label}] Exit")
            except OSError:
                print(f"[{self.name_label}] Exit")
            try:
                self.reader.close()
                self.writer.close()
                self.client_socket.close()
            except Exception:
                pass


class SocketServer:
    def __init__(self, host="127.0.0.1", port=1234):
        self.host = host
        self.port = port
        self.clients = []
        self.lock = threading.Lock()

    def add_thread(self, thread):
        with self.lock:
            self.clients.append(thread)

    def remove_thread(self, thread):
        with self.lock:
            self.clients.remove(thread)

    def broadcast(self, message):
        print(message)
        logging.info("BROADCAST | %s", message)
        with self.lock:
            for client in self.clients:
                try:
                    client.send(message)
                except Exception:
                    pass

    def serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(50)
            print(f"\n Waiting for Client connection on {self.host}:{self.port}")

            while True:
                client_socket, addr = server_socket.accept()
                print(f"{addr} connect")
                logging.info("NEW CONNECTION | %s", addr)

                thread = ServerThread(self, client_socket)
                self.add_thread(thread)
                thread.start()


if __name__ == "__main__":
    SocketServer().serve()
