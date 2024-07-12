# ComfyUI Event Reporter Plugin

## Introduction

The ComfyUI Event Reporter Plugin is an extension designed for ComfyUI, aimed at providing real-time reporting of workflow execution status. It captures the start and completion events of workflows and sends this information to a specified API endpoint.

## Features

- Automatic capture of ComfyUI workflow execution status
- Support for mapping multiple client IDs and prompt IDs
- Real-time sending of workflow completion events to a specified API
- Detailed execution logs for debugging and monitoring

## Installation

1. Ensure that you have ComfyUI installed.
2. Place the `event_reporter.py` file in the `custom_nodes` directory of your ComfyUI installation.
3. Restart the ComfyUI service.

## Configuration

In the `event_reporter.py` file, locate the following line and modify the API endpoint address:

```python
reporter = EventReporter("http://your-client-api.com/events")
```

Replace `http://your-client-api.com/events` with your actual API endpoint address.

## Usage

The plugin runs automatically without requiring additional user actions. When ComfyUI executes a workflow, the plugin will:

1. Capture the client_id and prompt_id when the workflow is added to the queue.
2. Send an event to the configured API endpoint when the workflow execution is completed.

## API Response Format

The event data sent to the API follows this format:

```json
{
  "event_type": "workflow_completed",
  "data": {
    "client_id": "client_id_here",
    "prompt_id": "prompt_id_here",
    "status": "success",
    "image_names": ["image1.png", "image2.png"]
  }
}
```

If the workflow execution fails, `status` will be "failed", and `image_names` will be replaced with `error_message`.

## Debugging

The plugin uses Python's logging module. To view detailed debug information, ensure that the log level is set to DEBUG:

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## Notes

- Ensure that your API endpoint can handle POST requests sent by the plugin.
- The plugin depends on ComfyUI's internal structure; it may need adjustments if ComfyUI is updated.
- It's recommended to check the logs periodically to ensure the plugin is functioning correctly.

## Contributing

Issue reports and suggestions for improvements are welcome. If you want to contribute code, please open an issue first to discuss your ideas.

## License

MIT License

Copyright (c) [2024] [Xianfeng Chen]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
