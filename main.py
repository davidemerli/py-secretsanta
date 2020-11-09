import time
from collections import defaultdict
from secret import *
import yagmail
import csv
import random as r
import networkx as nx
import matplotlib.pyplot as plt

MAX_TRIES = 1000000


def parse_bans(participants):
    cannot_send_to = dict()

    for p in participants:
        cannot_send_to[p] = {p}

    with open('avoid_matches.txt') as bans:
        lines = [line.strip() for line in bans.readlines() if line.strip()]

        for i, line in enumerate(lines):
            # double ban
            if '<->' in line:
                involved = line.split('<->')

                if len(involved) != 2:
                    raise Exception('Wrong format here ->', line, f'[line {i}]')

                cannot_send_to[involved[0]].add(involved[1])
                cannot_send_to[involved[1]].add(involved[0])

            # single ban, first to second
            elif '->' in line:
                involved = line.split('->')

                if len(involved) != 2:
                    raise Exception('Wrong format here ->', line, f'[line {i}]')

                cannot_send_to[involved[0]].add(involved[1])

            # single ban, second to first
            elif '<-' in line:
                involved = line.split('<-')

                if len(involved) != 2:
                    raise Exception('Wrong format here ->', line, f'[line {i}]')

                cannot_send_to[involved[1]].add(involved[0])

    return cannot_send_to


def get_participants():
    participants = defaultdict()

    with open('participants.csv') as csvfile:
        reader = csv.DictReader(csvfile)

        for p in reader:
            participants[p['name']] = p

    return participants


def compute_extraction(participants, bans):
    deliveries = defaultdict()

    for try_index in range(MAX_TRIES):
        for p in participants:
            choose_from = [other for other in participants if other not in bans[p]]
            # need_present.remove(send_to)

            deliveries[p] = r.choice(choose_from)

        # print('\n\n\n')
        # for p in deliveries:
        #     print(p, '->', deliveries[p])

        if len(set(deliveries.values())) == len(participants):
            return deliveries, (try_index + 1)
        else:
            deliveries.clear()

    raise Exception(f'Could not find a viable extraction in {MAX_TRIES} tries')


def draw_graph(vertices, edges):
    g = nx.DiGraph()
    g.add_nodes_from(vertices)
    pos = nx.spring_layout(g, k=2, iterations=20)

    options = {
        'node_color': '#ff6666',
        'node_size': 1500,
        'width': 2,
        'arrowsize': 10,
        'pos': pos,
    }

    for edge in edges.keys():
        g.add_edge(edge, edges[edge])

    nx.draw_networkx(g, **options)
    plt.draw()
    plt.show()


participants = get_participants()
participants_list = list(participants.keys())

bans = parse_bans(participants_list)

extraction, tries = compute_extraction(participants_list, bans)

for p in extraction.keys():
    print(f'{p} -> {extraction[p]}')

draw_graph(participants, extraction)

print(f'Found in {tries} tries')


# parse_bans(participants.keys())

# yag = yagmail.SMTP(email_address, email_password)

# contents = [
#     "This is the body, and here is just text http://somedomain/image.png",
#     "You can find an audio file attached.", '/local/path/to/song.mp3'
# ]
# yag.send('davidecuber@gmail.com', 'Test!', contents)
