## **HR-ASSIST Agentic AI System**

\---

HR ASSIST is an Agentic AI system designed to help HR teams automate routine workflows. This example demonstrates automation of the employee onboarding process, streamlining tasks that typically require manual intervention.

In terms of technical architecture, for MCP client we use Claude Desktop and the code base here represents the MCP server with necessary tools that will be used by MCP client

🛠️ Setup Instructions

To set up and run HR ASSIST, follow these steps:

* Configure claude\_desktop\_config.json
Add the following configuration to your claude\_desktop\_config.json file:

&#x20;   ```json
    {
    "mcpServers": {
        "hr-assist": {
        "command": "C:\\\\Users\\\\dhaval\\\\.local\\\\bin\\\\uv",
        "args": \[
            "--directory",
            "C::\\\\code\\\\atliq-hr-assist",
            "run",
            "server.py"
        ],
        "env": {
            "CB\_EMAIL": "YOUR\_EMAIL",
            "CB\_EMAIL\_PWD": "YOUR\_APP\_PASSWORD"
        }
        }
    }
    }
    ```

* Replace YOUR\_EMAIL with your actual email.
* Replace YOUR\_APP\_PASSWORD with your email provider’s app-specific password (e.g., for Gmail).
* Run `uv init` and `uv add mcp\[cli]` as per the video tutorial in the course.

**Usage**

* Click on the `+` icon and select the `Add from hr-assist` option, and send the request.
* Fill the details for the new employee:

<img src="resources\\image.jpg" alt="Claude desktop prompt with fields" style="width:auto;height:300px;padding-left:30px">

Alternatively, you can draft a custom prompt and let the agent take over.

