
from typing import Optional
from pandas import DataFrame


class NPC:

	def __init__(self, name: str, living_preferences: Optional[DataFrame] = None):
		self.name = name
		self.living_preferences = living_preferences

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