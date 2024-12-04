from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput


# Uncomment the following line to use an example of a custom tool
from research_assistant.tools.custom_tool import Preprocess, PreprocessOutput, ModelSelectionOutput, ESMFoldTool, BoltzTool
import os

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

@CrewBase
class ResearchAssistant():
	"""ResearchAssistant crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@before_kickoff # Optional hook to be executed before the crew starts
	def pull_data_example(self, inputs):
		# Example of pulling data from an external API, dynamically changing the inputs
		# inputs['extra_data'] = "This is extra data"
		return inputs

	@after_kickoff # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output
	
	@agent
	def preprocess_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['preprocess_agent'],
			verbose=True, 
			tools=[Preprocess(result_as_answer=True)],
		)
	
	@task
	def preprocess_task(self) -> Task:
		return Task(
			config=self.tasks_config['preprocess_task']
		)
	
	@agent
	def model_selection_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['model_selection_agent'],
			verbose=True,
		)
	
	@task
	def model_selection_task(self) -> Task:
		return Task(
			config=self.tasks_config['model_selection_task'], 
			context=[self.preprocess_task()], 
			human_input=True
		)
	
	@agent
	def esmfold_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['esmfold_agent'],
			verbose=True,
			tools=[ESMFoldTool(result_as_answer=True)]
		)

	@task
	def esmfold_task(self) -> Task:
		return Task(
			config=self.tasks_config['esmfold_task'],
			context=[self.preprocess_task(), self.model_selection_task()], 
			agent=self.esmfold_agent(), 
			async_execution=True
		)

	@agent
	def boltz_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['boltz_agent'],
			verbose=True,
			tools=[BoltzTool(result_as_answer=True)]
		)

	@task
	def boltz_task(self) -> Task:
		return Task(
			config=self.tasks_config['boltz_task'],
			context=[self.preprocess_task(), self.model_selection_task()], 
			agent=self.boltz_agent(),
			async_execution=True
		)
	
	# @agent
	# def igfold_agent(self) -> Agent:
	# 	return Agent(
	# 		config=self.agents_config['igfold_agent'],
	# 		verbose=True,
	# 		tools=[IgFoldTool()]
	# 	)

	# @task
	# def igfold_task(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['igfold_task'],
	# 		context=[self.preprocess_task(), self.model_selection_task()], 
	# 		agent=self.igfold_agent(), 
	# 	)

	@agent
	def reporter_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['reporter_agent'],
			context=[self.esmfold_task(), self.boltz_task()], # add more folding tasks here 
			verbose=True,
		)
	
	@task
	def reporter_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporter_task'],
			context=[self.esmfold_task(), self.boltz_task()], # add more folding tasks here 
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the ResearchAssistant crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
		)
