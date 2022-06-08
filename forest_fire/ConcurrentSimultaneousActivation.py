from mesa.time import BaseScheduler
from concurrent.futures import ThreadPoolExecutor, wait


class ConcurrentSimultaneousActivation(BaseScheduler):
    def step(self) -> None:
        agent_keys = list(self._agents.keys())
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.step_agent, agent_key) for agent_key in agent_keys}
            wait(futures)

            futures = {executor.submit(self.advance_agent, agent_key) for agent_key in agent_keys}
            wait(futures)

        self.steps += 1
        self.time += 1

    def step_agent(self, agent_key):
        self._agents[agent_key].step()
        print("Task Completed")

    def advance_agent(self, agent_key):
        self._agents[agent_key].advance()
        print("Task Completed")
