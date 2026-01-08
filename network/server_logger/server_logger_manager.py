import requests


class ServerLoggerManager:
    def __init__(self, server_url="https://mrag.pythonanywhere.com"):
        self.server_url = server_url
        self.timeout = (1, 1)

    def _post(self, data, url):
        try:
            response = requests.post(f"{self.server_url}/{url}", json=data, timeout=self.timeout)
            if response.status_code == 201:
                return {"success": True}
            else:
                error_data = response.json()
                return {"success": False, "error": error_data.get("error", "Unknown error")}
        except requests.exceptions.Timeout as e:
            return {"success": False, "error": f"Network error: {str(e)}", "data": []}
        except Exception as error:
            return {"success": False, "error": f"Unknown error: {error}", "data": []}

    def add_server(self, server_data: dict):
        return self._post(server_data, "add_server")

    def delete_server(self, server_data: dict):
        return self._post(server_data, "delete_server")

    def update_server(self, server_data: dict):
        return self._post(server_data, "update_server")

    def get_servers_list(self):
        try:
            response = requests.get(f"{self.server_url}/get_servers_list", timeout=self.timeout)
            if response.status_code == 200:
                result_data = response.json().get("data", [])
                return {"success": True, "data": result_data}
            else:
                error_data = response.json()
                return {"success": False, "error": error_data.get("error", "Unknown error"), "data": []}
        except requests.exceptions.Timeout as e:
            return {"success": False, "error": f"Network error: {str(e)}", "data": []}
        except Exception as error:
            return {"success": False, "error": f"Unknown error: {error}", "data": []}
