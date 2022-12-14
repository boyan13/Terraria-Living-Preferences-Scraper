
import requests
import math
import re

import pandas as pd
from bs4 import BeautifulSoup

from terraria.npcs import NPC


def read_terraria_wiki():
    """A generator function that scrapes the Terraria wiki web page for information on the individual NPCs' living
    preferences, constructs an NPC object instance for each NPC using this data, and returns a list of NPCs.
    On the first yield, the function yields the number of web pages that will be scraped, and then it yields after
    each page, until it returns the list at the end."""

    # Result list
    npcs = []

    # Urls
    base_url = "https://terraria.fandom.com/"
    npcs_url = "wiki/NPCs"

    # Load web page
    url = base_url + npcs_url
    page = requests.get(url)
    print(f'Loading web page: {url}')
    print(f'Page returned status code: {page.status_code}')

    # Create soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find the div holding all NPC links
    div_npcs = soup.find('div', attrs={'class': 'title'}, text='NPCs').parent
    if div_npcs is None:
        print('Failed to locate NPCs div.')
        return npcs

    # List the divs for individual NPCs
    individual_npc_divs = div_npcs.find_all(attrs={'class': 'i'})
    if individual_npc_divs is None:
        print('Cannot find divs for individual NPCs.')
        return npcs

    # Yield the number of web pages that will be scraped (equal to the number of NPC divs)
    yield len(individual_npc_divs)

    # Iterate over the individual NPCs divs
    for npc_div in individual_npc_divs:

        npc_anchor = npc_div.find('a', href=True)
        npc_url = npc_anchor.get('href', None)

        npc_name = 'Unknown'

        try:

            npc_page = requests.get(base_url + npc_url)  # Proceed to the npc's webpage
            npc_soup = BeautifulSoup(npc_page.content, 'html.parser')  # Make soup

            npc_name = npc_soup.find('h1', attrs={'id': 'firstHeading'}).text.strip()  # Get the npc's name
            if npc_name in NPC.npcs_with_no_living_preferences():  # Should we look for living preferences?
                print(f'Skipping {npc_name} (no living preferences).')  # If not
                npcs.append(NPC(name=npc_name, living_preferences=None))  # Build with dummy preferences
                continue

            # Use pandas read_html to find and parase the living preferences html table into a DataFrame
            preferences = pd.read_html(base_url + npc_url, attrs={'class': 'terraria living-preferences'})[0]

            # Grab the first (unnamed) column, as it contains the row titles in it
            first_col = preferences.loc[:, preferences.columns[0]]

            # Create a dict mapping that maps the current DataFrame indices to the semantic names
            new_names = {k: v for k, v in zip(preferences.index, first_col)}

            # Rename the index using the new names mapping
            preferences.rename(mapper=new_names, inplace=True)

            # Drop the unnamed column of containing the row names
            del preferences[preferences.columns[0]]

            # Purge parsing artifacts and reformat
            for i in preferences.index:
                for j in preferences.columns:
                    item = preferences.loc[i, j]

                    if type(item) is float and math.isnan(item):
                        # Replace {float} nan with 'N/A'
                        preferences.loc[i, j] = 'N/A'

                    elif type(item) is str:
                        # Remove the '\u200b' character from the string.
                        formatted = item.replace('\u200b', '').strip()
                        # When the text of the cell contains multiple values, they come glued together
                        # without spaces, which is hard to read. Split the string by capital letter, and then
                        # join it back using comma + space.
                        formatted = re.sub(r"([a-z])([A-Z])", r'\1, \2', formatted)
                        # Replace the old text with the formatted one
                        preferences.loc[i, j] = formatted

            npcs.append(NPC(name=npc_name, living_preferences=preferences))  # Instantiate and add NPC to list
            print(f'Successfully parsed {npc_name}!')

        except Exception as exc:
            print(f'Failed to parse {npc_name}. Moving on...')

        finally:
            yield  # Yield after each web page. Useful for denoting progress or cancelling the thread.

    return npcs

