from mesa.time import BaseScheduler
from concurrent.futures import ProcessPoolExecutor, wait


class ConcurrentSimultaneousActivation(BaseScheduler):
    def __init__(self, model):
        super().__init__(model)
        self.number_of_workers = 4
        self.executor = ProcessPoolExecutor(max_workers=self.number_of_workers)

    def __del__(self):
        self.executor.shutdown()

    def step(self) -> None:
        agent_keys = list(self._agents.keys())

        futures = {self.executor.submit(self.step_agent, agent_keys_chunk) for agent_keys_chunk in self.chunks(agent_keys, self.number_of_workers)}
        wait(futures)

        futures = {self.executor.submit(self.advance_agent, agent_keys_chunk) for agent_keys_chunk in self.chunks(agent_keys, self.number_of_workers)}
        wait(futures)

        self.steps += 1
        self.time += 1

    def step_agent(self, agent_keys):
        print("Agent Step Scheduled " + str(agent_keys))
        for agent_key in agent_keys:
            self._agents[agent_key].step()
            print("Agent Step Completed")

    def advance_agent(self, agent_keys):
        print("Agent Advance Scheduled " + str(agent_keys))
        for agent_key in agent_keys:
            self._agents[agent_key].advance()
            print("Agent Advance Completed")

    @staticmethod
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
