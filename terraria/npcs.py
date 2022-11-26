
from typing import Optional
from pandas import DataFrame


class NPC:

	def __init__(self, name: str, living_preferences: Optional[DataFrame] = None):
		self.name = name
		self.living_preferences = living_preferences

		# Stats
		self.favorite_biomes = None
		self.favorite_neighbors = None

		self.generate_stats()

	def generate_stats(self):
		if self.living_preferences is None:
			self.favorite_biomes = []
			self.favorite_neighbors = []
			return

		for liking, biome in self.living_preferences['Biome'].items():
			if biome != 'N/A':
				self.favorite_biomes = [s.strip() for s in biome.split(', ')]
				break

		for liking, neighbor in self.living_preferences['Neighbor'].items():
			if neighbor != 'N/A':
				self.favorite_neighbors = [s.strip() for s in neighbor.split(', ')]
				break

	def __repr__(self):
		if self.living_preferences is not None:
			preferences = self.living_preferences
		else:
			preferences = 'No living preferences.'

		return f'{self.name}\n{preferences}'

	@staticmethod
	def npcs_with_no_living_preferences():
		return (
			'Princess',
			'Traveling Merchant',
			'Old Man',
			'Skeleton Merchant',
			'Mc MoneyPants',
			'Star Merchant',
			'Town Cat',
			'Town Dog',
			'Town Bunny',
			'Confused'
		)