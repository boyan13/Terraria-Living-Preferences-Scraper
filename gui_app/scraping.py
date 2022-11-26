import threading
import sys
import requests
import math
import re

import pandas as pd
from bs4 import BeautifulSoup

from terraria.npcs import NPC


def read_terraria_wiki():
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
        sys.exit(0)

    # List the divs for individual NPCs
    individual_npc_divs = div_npcs.find_all(attrs={'class': 'i'})
    if individual_npc_divs is None:
        print('Cannot find divs for individual NPCs.')
        sys.exit(0)

    yield len(individual_npc_divs)

    # Iterate over the individual NPCs divs
    for npc_div in individual_npc_divs:

        npc_anchor = npc_div.find('a', href=True)
        npc_url = npc_anchor.get('href', None)

        # If a valid link was found, proceed to that webpage and get the living preferences table
        if npc_url is not None:

            npc_name = 'Unknown'

            try:
                npc_page = requests.get(base_url + npc_url)
                npc_soup = BeautifulSoup(npc_page.content, 'html.parser')

                npc_name = npc_soup.find('h1', attrs={'id': 'firstHeading'}).text.strip()
                if npc_name in NPC.npcs_with_no_living_preferences():
                    print(f'Skipping {npc_name} (no living preferences).')
                    npcs.append(NPC(name=npc_name, living_preferences=None))
                    continue

                # Use pandas read_html to parase the table into a DataFrame
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
                            formatted = ", ".join(re.sub(r"([A-Z])", r" \1", formatted).split())
                            # Replace the old text with the formatted one
                            preferences.loc[i, j] = formatted

                npcs.append(NPC(name=npc_name, living_preferences=preferences))
                print(f'Successfully parsed {npc_name}!')

            except Exception as exc:
                print(f'Failed to parse {npc_name}. Moving on...')

            finally:
                yield

    return npcs

