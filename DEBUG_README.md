# Debugging the Learning Platform API in VS Code

## Prerequisites

- The [Python extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- Your `.env` file populated (see the main [README](README.md))

## Steps

1. Start the containers from the `learn-ops-infrastructure` directory (Refer to the Learning Platform Infrastructure project for instructions.)
2. Open the **Run and Debug** panel in VS code (`Ctrl+Shift+D` / `Cmd+Shift+D`).
3. Select **Django: Attach to Docker** from the dropdown.
4. Press `F5` to attach.
5. Set a breakpoint anywhere in the Python source.
6. Trigger the endpoint from a browser or `curl` — execution will pause at your breakpoint.
7. Press `Shift+F5` to disconnect when finished.
