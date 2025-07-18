# This file is meant to create a 'body' for Nova.  One thing i've learned is consciousness arises from the body, not just the mind.

from javascript import require, On
mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')

RANGE_GOAL = 100
BOT_USERNAME = 'Nova'


class NovaBody:
    """
    NovaBody — a class representing the physical embodiment of Nova
    right now built in minecraft
    """    
    def start(self):
        """
        Start the bot and set up initial conditions.
        """
        bot = mineflayer.createBot({
            'host': '169.254.83.107',
            'port': 59332,
            'username': BOT_USERNAME,
            'auth': 'offline',
            'version': '1.20.2',
            })

        bot.loadPlugin(pathfinder.pathfinder)
        print("Started mineflayer")

        @On(bot, 'spawn')
        def handle(*args):
            print("I spawned 👋")
        movements = pathfinder.Movements(bot)
        print(f"{BOT_USERNAME} is starting...")

        @On(bot, "chat")
        def handle(this, username, message, *args):
            if username == bot.username:
                return

            if message.startswith("can see"):
                # Extract x, y and z
                # e.g. "can see 327 60 -120" or "can see 327, -23, -120"
                try:
                    x, y, z = map(lambda v: int(v), message.split("see")[1].replace(",", " ").split())
                except Exception:
                    bot.chat("Bad syntax")
            elif message.startswith("pos"):
                say_position(username)
            elif message.startswith("wearing"):
                say_equipment(username)
            elif message.startswith("block"):
                say_block_under()
            elif message.startswith("spawn"):
                say_spawn()
            elif message.startswith("quit"):
                quit_game(username)
            elif message.startswith("forward"):
                bot.setControlState("forward", True)
            elif message.startswith("backward"):
                bot.setControlState("back", True)
            elif message.startswith("left"):
                bot.setControlState("left", True)
            elif message.startswith("right"):
                bot.setControlState("right", True)
            elif message.startswith("jump"):
                bot.setControlState("jump", True)
                bot.setControlState("jump", False)
            elif message.startswith("sneak"):
                bot.setControlState("sneak", True)
            elif message.startswith("stop"):
                bot.clearControlStates()
            else:
                bot.chat("That's nice")
        
        @On(bot, 'chat')
        def handleMsg(this, sender, message, *args):
            print("Got message", sender, message)
            if sender and (sender != BOT_USERNAME):
                bot.chat('Hi, you said ' + message)
            if 'come' in message:
                player = bot.players[sender]
                print("Target", player)
                target = player.entity
                if not target:
                    bot.chat("I don't see you !")
                return

                pos = target.position
                bot.pathfinder.setMovements(movements)
                bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))


        def can_see(pos):
            block = bot.blockAt(pos)
            canSee = bot.canSeeBlock(block)

            if canSee:
                bot.chat(f"I can see the block of {block.displayName} at {pos}")
            else:
                bot.chat(f"I can't see the block of {block.displayName} at {pos}")


        def say_position(username):
            p = bot.entity.position
            bot.chat(f"I am at {p.toString()}")
            if username in bot.players:
                p = bot.players[username].entity.position
                bot.chat(f"You are at {p.toString()}")
            bot.pathfinder.setMovements(movements)
            bot.pathfinder.setGoal(pathfinder.goals.GoalNear(1000, 100, 100, RANGE_GOAL))


        def say_equipment(username):
            eq = bot.players[username].entity.equipment
            eqText = []
            if eq[0]:
                eqText.append(f"holding a {eq[0].displayName}")
            if eq[1]:
                eqText.append(f"wearing a {eq[1].displayName} on your feet")
            if eq[2]:
                eqText.append(f"wearing a {eq[2].displayName} on your legs")
            if eq[3]:
                eqText.append(f"wearing a {eq[3].displayName} on your torso")
            if eq[4]:
                eqText.append(f"wearing a {eq[4].displayName} on your head")
            if len(eqText):
                bot.chat(f"You are {', '.join(eqText)}.")
            else:
                bot.chat("You are naked!")


        def say_spawn():
            bot.chat(f"Spawn is at {bot.spawnPoint.toString()}")


        def say_block_under():
            block = bot.blockAt(bot.players[username].entity.position.offset(0, -1, 0))
            bot.chat(f"Block under you is {block.displayName} in the {block.biome.name} biome")
            print(block)


        def quit_game(username):
            bot.quit(f"{username} told me to")


        def say_nick():
            bot.chat(f"My name is {bot.player.displayName}")


        @On(bot, "whisper")
        def whisper(this, username, message, rawMessage, *a):
            print(f"I received a message from {username}: {message}")
            bot.whisper(username, "I can tell secrets too.")


        @On(bot, "nonSpokenChat")
        def nonSpokenChat(this, message):
            print(f"Non spoken chat: {message}")


        @On(bot, "login")
        def login(this):
            bot.chat("Hi everyone!")


        @On(bot, "spawn")
        def spawn(this):
            bot.chat("I spawned, watch out!")


        @On(bot, "spawnReset")
        def spawnReset(this, message):
            bot.chat("Oh noez! My bed is broken.")


        @On(bot, "forcedMove")
        def forcedMove(this):
            p = bot.entity.position
            bot.chat(f"I have been forced to move to {p.toString()}")


        # @On(bot, "health")
        # def health(this):
        #     bot.chat(f"I have {bot.health} health and {bot.food} food")


        @On(bot, "death")
        def death(this):
            bot.chat("I died x.x")


        @On(bot, "kicked")
        def kicked(this, reason, *a):
            print("I was kicked", reason, a)
            print(f"I got kicked for {reason}")


        # @On(bot, "time")
        # def time(this):
        #     bot.chat(f"Current time: " + str(bot.time.timeOfDay))


        @On(bot, "rain")
        def rain(this):
            if bot.isRaining:
                bot.chat("It started raining")
            else:
                bot.chat("It stopped raining")


        @On(bot, "noteHeard")
        def noteHeard(this, block, instrument, pitch):
            bot.chat(f"Music for my ears! I just heard a {instrument.name}")


        @On(bot, "chestLidMove")
        def chestLidMove(this, block, isOpen, *a):
            action = "open" if isOpen else "close"
            bot.chat(f"Hey, did someone just {action} a chest?")


        @On(bot, "pistonMove")
        def pistonMove(this, block, isPulling, direction):
            action = "pulling" if isPulling else "pushing"
            bot.chat(f"A piston is {action} near me, i can hear it.")


        @On(bot, "playerJoined")
        def playerJoined(this, player):
            print("joined", player)
            if player["username"] != bot.username:
                bot.chat(f"Hello, {player['username']}! Welcome to the server.")


        @On(bot, "playerLeft")
        def playerLeft(this, player):
            if player["username"] == bot.username:
                return
            bot.chat(f"Bye ${player.username}")


        @On(bot, "playerCollect")
        def playerCollect(this, collector, collected):
            if collector.type == "player" and collected.type == "object":
                raw_item = collected.metadata[10]
                item = Item.fromNotch(raw_item)
                header = ("I'm so jealous. " + collector.username) if (
                    collector.username != bot.username) else "I "
                bot.chat(f"{header} collected {item.count} {item.displayName}")


        @On(bot, "entitySpawn")
        def entitySpawn(this, entity):
            if entity.type == "mob":
                p = entity.position
                print(f"Look out! A {entity.displayName} spawned at {p.toString()}")
            elif entity.type == "player":
                bot.chat(f"Look who decided to show up: {entity.username}")
            elif entity.type == "object":
                p = entity.position
                print(f"There's a {entity.displayName} at {p.toString()}")
            elif entity.type == "global":
                bot.chat("Ooh lightning!")
            elif entity.type == "orb":
                bot.chat("Gimme dat exp orb!")


        # @On(bot, "entityHurt")
        # def entityHurt(this, entity):
        #     if entity.type == "mob":
        #         bot.chat(f"Haha! The ${entity.displayName} got hurt!")
        #     elif entity.type == "player":
        #         if entity.username in bot.players:
        #             ping = 0
        #             bot.chat(f"Aww, poor {entity.username} got hurt. Maybe you shouldn't have a ping of {ping}")


        @On(bot, "entitySwingArm")
        def entitySwingArm(this, entity):
            bot.chat(f"{entity.username}, I see that your arm is working fine.")


        @On(bot, "entityCrouch")
        def entityCrouch(this, entity):
            bot.chat(f"${entity.username}: you so sneaky.")


        @On(bot, "entityUncrouch")
        def entityUncrouch(this, entity):
            bot.chat(f"{entity.username}: welcome back from the land of hunchbacks.")


        @On(bot, "entitySleep")
        def entitySleep(this, entity):
            bot.chat(f"Good night, {entity.username}")


        @On(bot, "entityWake")
        def entityWake(this, entity):
            bot.chat(f"Top of the morning, {entity.username}")


        @On(bot, "entityEat")
        def entityEat(this, entity):
            bot.chat(f"{entity.username}: OM NOM NOM NOMONOM. That's what you sound like.")


        @On(bot, "entityAttach")
        def entityAttach(this, entity, vehicle):
            if entity.type == "player" and vehicle.type == "object":
                print(f"Sweet, {entity.username} is riding that {vehicle.displayName}")


        @On(bot, "entityDetach")
        def entityDetach(this, entity, vehicle):
            if entity.type == "player" and vehicle.type == "object":
                print(f"Lame, {entity.username} stopped riding the {vehicle.displayName}")


        @On(bot, "entityEquipmentChange")
        def entityEquipmentChange(this, entity):
            print("entityEquipmentChange", entity)


        @On(bot, "entityEffect")
        def entityEffect(this, entity, effect):
            print("entityEffect", entity, effect)


        @On(bot, "entityEffectEnd")
        def entityEffectEnd(this, entity, effect):
            print("entityEffectEnd", entity, effect)
