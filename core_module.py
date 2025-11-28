import asyncio
import logging
import uuid
from rx.subject import Subject
import json

from cli_body import CLIBody
from real_time_queue import RealTimeQueue

# Import cognitive architecture modules (ensure paths are correct)
from nova_core.nova_brain_v4 import NovaBrainV4
from nova_core.models.declarative_memory import DeclarativeMemory
from nova_core.models.procedural_memory import ProceduralMemory
from nova_core.models.working_memory import WorkingMemory
from nova_core.models.situational_model import SituationalModel, SituationalAwareness
from nova_core.models.chain_of_thought import ChainOfThoughts
from nova_core.memory_manager import ChromaMemoryManager

# Import external perceptive modules
from perceptions.wallet_surveillance import WalletSurveillance
from perceptions.time_cartel import TimeCartel
from perceptions.system_snitch import SystemSnitch

        # 4. Initialize Actuators
from actuators.actuator_manager import ActuatorManager
from actuators.network_actuator import NetworkActuator
from actuators.market_actuator import MarketActuator
from actuators.research_actuator import ResearchActuator
from agents.research_agent import WebCrawler
class CoreModule:
    """
    Phase 2 Core Module:
    - Uses CLIBody for perception
    - Integrates full NovaBrainV3 cognitive cycle
    - Memory modules subscribed via UCP
    - Routes brain-generated commands to EventBus
    """
    def __init__(self, bus_url: str = None):
        logging.basicConfig(level=logging.WARNING)
        # Silence noisy libraries
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("chromadb").setLevel(logging.WARNING)
        
        self.real_time_queue = RealTimeQueue()
        self.ucp = Subject()

        # Cognitive architecture components
        self.working_memory = WorkingMemory()
        self.declarative_memory = DeclarativeMemory()
        self.procedural_memory = ProceduralMemory()
        self.situational_model = SituationalModel()
        self.situational_awareness = SituationalAwareness()
        self.chain_of_thought = ChainOfThoughts(device_id="NovaCore")
        
        # Unified Memory
        self.memory = ChromaMemoryManager()

        
        self.actuator_manager = ActuatorManager()
        self.actuator_manager.register_actuator(NetworkActuator())
        self.actuator_manager.register_actuator(MarketActuator())

        self.actuator_manager.register_actuator(ResearchActuator(web_crawler=None, memory_manager=self.memory))

        self.brain = NovaBrainV4(
            ucp=self.ucp,
            working_memory=self.working_memory,
            declarative_memory=self.declarative_memory,
            procedural_memory=self.procedural_memory,
            situational_awareness=self.situational_awareness,
            chain_of_thought=self.chain_of_thought,
            real_time_queue=self.real_time_queue,
            actuator_manager=self.actuator_manager,
            memory_manager=self.memory
        )
        
        # Perception component
        self.body = CLIBody(self.real_time_queue)

    async def initialize(self):
        # Start perception
        asyncio.create_task(self.body.start())

        # Start external perception modules
        self.wallet_surveillance = WalletSurveillance(self.real_time_queue)
        self.time_cartel = TimeCartel(self.real_time_queue)
        self.system_snitch = SystemSnitch(self.real_time_queue)
        
        # Initialize Research Agent (Passive)
        self.web_crawler = WebCrawler(self.real_time_queue)
        
        # Inject crawler into ResearchActuator
        if "research" in self.actuator_manager.actuators:
            self.actuator_manager.actuators["research"].web_crawler = self.web_crawler

        self.brain.tools = {"web_crawler": self.web_crawler}

        # Publish system startup
        startup = {"node_id": uuid.uuid4().hex}
        await self.real_time_queue.enqueue(startup)



    async def start(self):
        await self.initialize()

        # Start the cognitive cycle
        asyncio.create_task(self.brain.cognitive_cycle())

        # Keep running
        while True:
            await asyncio.sleep(1)

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            logging.info("[Phase2] Shutting down...")
            self.brain.running = False
        finally:
            loop.close()