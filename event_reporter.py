import json
import requests
import logging
from server import PromptServer

class EventReporter:
    instance = None

    def __init__(self, client_api_url):
        self.server = PromptServer.instance
        self.client_api_url = client_api_url
        self.client_prompt_map = {}

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = EventReporter("http://your-client-api.com/events")
        return cls.instance

    def report_event(self, event_type, data):
        payload = {
            "event_type": event_type,
            "data": data
        }
        
        logging.info(f"Attempting to report event: {event_type}")
        logging.debug(f"Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(self.client_api_url, json=payload)
            logging.info(f"Request sent to: {self.client_api_url}")
            logging.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                logging.info("Event reported successfully")
                try:
                    response_json = response.json()
                    logging.info("Response content:")
                    logging.info(json.dumps(response_json, indent=2))
                except json.JSONDecodeError:
                    logging.warning("Response is not JSON. Raw content:")
                    logging.warning(response.text)
            else:
                logging.error(f"Failed to report event. Status code: {response.status_code}")
                logging.error(f"Response content: {response.text}")

            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Exception occurred while reporting event: {str(e)}")
            return None

    def register_prompt(self, client_id, prompt_id):
        self.client_prompt_map[prompt_id] = client_id
        logging.info(f"Registered prompt: client_id={client_id}, prompt_id={prompt_id}")
        logging.debug(f"Current client_prompt_map: {self.client_prompt_map}")

    def on_executed(self, prompt_id, data):
        logging.info(f"Execution completed for prompt_id: {prompt_id}")
        logging.debug(f"Current client_prompt_map: {self.client_prompt_map}")
        if prompt_id in self.client_prompt_map:
            client_id = self.client_prompt_map[prompt_id]
            output_images = self.get_output_images(data)
            
            event_data = {
                "client_id": client_id,
                "prompt_id": prompt_id,
                "status": "success" if output_images else "failed"
            }

            if output_images:
                event_data["image_names"] = output_images
                logging.info(f"Generated images: {output_images}")
            else:
                event_data["error_message"] = "No images were generated"
                logging.warning("No images were generated")

            self.report_event("workflow_completed", event_data)
            
            del self.client_prompt_map[prompt_id]
            logging.info(f"Removed prompt_id {prompt_id} from client_prompt_map")
            logging.debug(f"Updated client_prompt_map: {self.client_prompt_map}")
        else:
            logging.error(f"prompt_id {prompt_id} not found in client_prompt_map")

    def get_output_images(self, data):
        output_images = []
        outputs = data.get("outputs", {})
        for node_output in outputs.values():
            if "images" in node_output:
                for image in node_output["images"]:
                    if image["type"] == "output":
                        image_name = image["filename"]
                        if image.get("subfolder"):
                            image_name = f"{image['subfolder']}/{image_name}"
                        output_images.append(image_name)
        return output_images

    def on_prompt_handler(self, json_data):
        client_id = json_data.get("client_id")
        if "prompt" in json_data and client_id:
            prompt_id = json_data.get("prompt_id")
            if prompt_id:
                self.register_prompt(client_id, prompt_id)
        return json_data

# 虚拟节点类
class EventReporterNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"dummy": ("STRING", {"default": ""})}}
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "noop"
    CATEGORY = "event_reporter"

    def noop(self, dummy):
        return (dummy,)

# 全局变量
NODE_CLASS_MAPPINGS = {
    "EventReporterNode": EventReporterNode
}

def init_event_reporter():
    reporter = EventReporter.get_instance()
    server = PromptServer.instance

    logging.info("Initializing EventReporter")

    original_task_done = server.prompt_queue.task_done

    def new_task_done(self, item_id, outputs, status):
        logging.info(f"Task done called for item_id: {item_id}")
        prompt = self.currently_running.get(item_id)
        if prompt:
            prompt_id = prompt[1]  # 获取 prompt_id
            logging.info(f"Retrieved prompt_id: {prompt_id}")
            reporter.on_executed(prompt_id, {"outputs": outputs})
        else:
            logging.warning(f"item_id {item_id} not found in currently_running")

        original_task_done(item_id, outputs, status)

    server.prompt_queue.task_done = new_task_done.__get__(server.prompt_queue, type(server.prompt_queue))

    original_put = server.prompt_queue.put

    def new_put(self, item):
        logging.info(f"New item added to queue: {item}")
        if isinstance(item, tuple) and len(item) > 3:
            prompt_id = item[1]
            extra_data = item[3]
            client_id = extra_data.get("client_id")
            if client_id and prompt_id:
                reporter.register_prompt(client_id, prompt_id)
            else:
                logging.warning(f"Missing client_id or prompt_id in queue item: {item}")
        original_put(item)

    server.prompt_queue.put = new_put.__get__(server.prompt_queue, type(server.prompt_queue))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
init_event_reporter()