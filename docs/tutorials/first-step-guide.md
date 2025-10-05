This file provides a concrete, goal-oriented tutorial for a new user, distinct from the reference-style content in the other folders. It assumes the user has completed installation and configuration.

Markdown

# Tutorial: Your First [Action/Feature]

This guide will walk you through performing a common task: **[e.g., Creating your first project, running a simple query, processing a batch of data]**.

## Goal: [State the clear, simple goal]

By the end of this tutorial, you will have successfully **[e.g., created a new configuration file and started the service]**.

## Prerequisites

* You have completed the **[Installation guide](../getting-started/installation.md)**.
* You have a terminal window open in the root directory of your project.

## Step 1: Initialize the [Component]

First, we need to create the basic boilerplate for the [component, e.g., project, data source].

Run the following command:

```bash
your-project-name init --name my-first-task
You should see an output similar to:

INFO: Project 'my-first-task' created successfully in ./my-first-task/
Step 2: Modify the Configuration
Navigate into the new directory and open the configuration file.

Bash

cd my-first-task/
nano config.json # or use your preferred editor
Change the logging_level from "INFO" to "DEBUG".

Original config.json:

JSON

{
  "name": "my-first-task",
  "logging_level": "INFO", 
  "timeout_seconds": 60
}
Modified config.json:

JSON

{
  "name": "my-first-task",
  "logging_level": "DEBUG", 
  "timeout_seconds": 60 
}
Step 3: Run the Task
Execute the project using the configuration file you just modified.

Bash

your-project-name run --config config.json
Success! 🎉
If the terminal output now shows logs prefixed with [DEBUG] instead of just [INFO], you have successfully configured and run your first task with the new logging level!

Next, explore the API Reference to learn more about advanced usage.







