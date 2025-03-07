from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
from schemas import OpenAIChatMessage
import requests
import re
import json

class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        # Let the id be inferred from the filename (api_call_pipe.py)
        self.name = "OllamaModelListPipeline"
        self.valves = self.Valves(**{})

    async def on_startup(self):
        print(f"on_startup: {__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown: {__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(f"pipe: {__name__} - user_message: {user_message}")

        # Check the last message for the integration request
        last_message = messages[-1].get("content", "") if messages and messages[-1].get("content") else user_message
        pattern = r"INTEGRATION_REQUEST_ActionStart \| REQ_(\d{8}_\d{6}) \| GET (http[s]?://\S+)"
        match = re.match(pattern, last_message)
        if not match:
            return "No valid integration request found."

        timestamp = match.group(1)
        url = match.group(2)

        # Call the Ollama API
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            return f"Error: API call failed - {str(e)}"

        # Prepare the ActionEnd response
        action_end = f"INTEGRATION_REQUEST_ActionEnd | REQ_{timestamp} | {json.dumps(data)}"
        return action_end

if __name__ == "__main__":
    # Test the pipeline locally
    test_message = {"role": "user", "content": "INTEGRATION_REQUEST_ActionStart | REQ_20250307_205435 | GET http://192.168.0.25:11434/api/tags"}
    pipeline = Pipeline()
    result = pipeline.pipe("", "", [test_message], {})
    print(result)