def execute(action):
    """Execute a Minecraft action based on the provided action string."""
    if action == "mine":
        return "Mining block..."
    elif action == "build":
        return "Building structure..."
    elif action == "explore":
        return "Exploring the world..."
    elif action == "fight":
        return "Engaging in combat..."
    elif action == "stop":
        bot.clearControlStates()
    elif action == "jump":
        bot.setControlState("jump", True)
        bot.setControlState("jump", False)
    else:
        return "Unknown action, please try again."