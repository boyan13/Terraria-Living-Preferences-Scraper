
from typing import Optional
from pandas import DataFrame


class NPC:

	def __init__(self, name: str, living_preferences: Optional[DataFrame] = None):
		self.name = name
		self.living_preferences = living_preferences

	@property
	def favorite_biomes(self):
		if self.living_preferences is not None:
			liking_scale = list(self.living_preferences.index)
			for liking in liking_scale:
				biome = self.living_preferences['Biome'][liking]
				if biome != 'N/A':
					favorite = [s.strip() for s in biome.split(', ')]
					return favorite
		return ['N/A']

	@property
	def favorite_neighbors(self):
		if self.living_preferences is not None:
			liking_scale = list(self.living_preferences.index)
			for liking in liking_scale:
				neighbor = self.living_preferences['Neighbor'][liking]
				if neighbor != 'N/A':
					favorite = [s.strip() for s in neighbor.split(', ')]
					return favorite
		return ['N/A']

	@property
	def least_favorite_biomes(self):
		if self.living_preferences is not None:
			disliking_scale = reversed(list(self.living_preferences.index))
			for disliking in disliking_scale:
				biome = self.living_preferences['Biome'][disliking]
				if biome != 'N/A':
					least_favorite = [s.strip() for s in biome.split(', ')]
					return least_favorite
		return ['N/A']

	@property
	def least_favorite_neighbors(self):
		if self.living_preferences is not None:
			disliking_scale = reversed(list(self.living_preferences.index))
			for disliking in disliking_scale:
				neighbor = self.living_preferences['Neighbor'][disliking]
				if neighbor != 'N/A':
					least_favorite = [s.strip() for s in neighbor.split(', ')]
					return least_favorite
		return ['N/A']

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