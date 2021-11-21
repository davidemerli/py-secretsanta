from logging import DEBUG, INFO, debug, info
from collections import defaultdict
from random import shuffle, choice
import matplotlib.pyplot as plt
from string import Template
from tqdm import tqdm
import networkx as nx
from secret import *
import random as r
import numpy as np
import yagmail
import logging
import dotenv
import pickle
import click
import csv
import os

MAX_TRIES = 1000000

logging.basicConfig(format="%(levelname)s:%(message)s", level=INFO)

dotenv.load_dotenv()

AUTHOR_MAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
AUTHOR_MAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

with open("suggestions.txt") as f:
    SUGGESTIONS = [line.strip() for line in f.readlines() if line.strip()]


def parse_bans(participants):
    """
    Parses avoid_matches.txt returning a dictionary with participants as keys.
    For every participants it is associated a list of matches to avoid.
    Convention is:   KEY -should not send to-> VALUES
    """
    cannot_send_to = dict()

    for p in participants:
        cannot_send_to[p] = {p}

    def are_participants(involved):
        return all(x in participants for x in involved)

    def check_involved(involved):
        if len(involved) != 2:
            raise Exception("Wrong format here ->", line, f"[line {i}]")

        if not are_participants(involved):
            raise Exception(
                "Found a name not in participants here ->", line, f"[line {i}]"
            )

    with open("avoid_matches.txt") as bans:
        lines = [line.strip() for line in bans.readlines() if line.strip()]
        lines = [line for line in lines if line[0] != "#"]

        for i, line in enumerate(lines):
            splitter = "<->" if "<->" in line else "->" if "->" in line else "<-"

            involved = line.split(splitter)
            check_involved(involved)

            cannot_send_to[involved[0]].add(involved[1])

            if splitter == "<->":
                cannot_send_to[involved[1]].add(involved[0])

    return cannot_send_to


def get_participants():
    """
    Parses participants.csv to retrieve a dictionary with participants as keys
    and as values another dictionary for each participants containing all valuable informations
    """
    participants = defaultdict()

    with open("participants.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        for p in reader:
            participants[p["name"]] = p

    return participants


def compute_extraction(participants, bans):
    """
    Given a list of participants and matches to avoid, naively tries to create a valid
    list of matches to return.

    With many banned combinations may take a while to find a valid set, consider changing MAX_TRIES
    """
    deliveries = defaultdict()

    for try_index in range(MAX_TRIES):
        for p in participants:
            choose_from = [other for other in participants if other not in bans[p]]

            deliveries[p] = r.choice(choose_from)

        if len(set(deliveries.values())) == len(participants):
            return deliveries, (try_index + 1)
        else:
            deliveries.clear()

    raise Exception(f"Could not find a viable extraction in {MAX_TRIES} tries")


def draw_graph(vertices, edges, hide_names=True):
    """
    Draws the randomly chosen set of matches a graph for an easy visualization.
    """
    g = nx.DiGraph()

    vertices = list(vertices.keys())
    shuffle(vertices)

    if hide_names:
        remap = {key: vertices.index(key) for key in vertices}
        vertices = remap.values()
        edges = {remap[key]: remap[value] for key, value in edges.items()}

    g.add_nodes_from(vertices)

    pos = nx.spring_layout(g, k=0.3 * 1 / np.sqrt(len(g.nodes())), iterations=1000)

    options = {
        "node_color": "#ff6666",
        "with_labels": True,
        "node_size": 7000,
        "width": 4,
        "arrowsize": 40,
        "pos": pos,
        "alpha": 0.8,
        "arrowstyle": "->",
    }

    g.add_edges_from(edges.items())

    pickle.dump(g, open("graph.pickle", "wb"))

    info("Saved matches graph as 'graph.pickle'")

    nx.draw_networkx(g, **options)
    plt.draw()
    plt.show()


def send_test_emails(participants_dict):
    """
    Sends a test email to everyone, using yagmail and the account specified in 'secret.py'
    """
    yag = yagmail.SMTP(email_address, email_password)

    for from_ in tqdm(participants_dict.keys(), desc="Sending test emails", ncols=75):
        from_ = participants_dict[from_]

        content = read_template_file("test-mail-text.txt", from_, defaultdict(str))
        content += "\n\n\n\n\n\nSent by py-secretsanta: https://github.com/davidemerli/py-secretsanta"

        debug("#####################################################")
        debug(content)
        debug("#####################################################")

        yag.send(to=from_["mail"], subject="[TEST] py-secretsanta", contents=content)


def find_replacements(to, from_):
    return {
        "to_fullname": to["name"],
        "to_firstname": to["name"].split(" ")[0],
        "to_phone": to["phone"],
        "to_address": to["address"],
        "to_province": to["province"],
        "to_city": to["city"],
        "to_postalcode": to["postal_code"],
        "to_extra": to["extra"],
        "from_fullname": from_["name"],
        "from_firstname": from_["name"].split(" ")[0],
        "from_phone": from_["phone"],
        "from_address": from_["address"],
        "from_province": from_["province"],
        "from_city": from_["city"],
        "from_postalcode": from_["postal_code"],
        "from_extra": from_["extra"],
        "random_suggestion": choice(SUGGESTIONS),
    }


def read_template_file(filename, from_, to):
    with open(filename) as f:
        # ignore comments
        text = [
            line for line in f.readlines() if not line.strip() or line.strip()[0] != "#"
        ]

        src = Template("".join(text))
        return src.substitute(find_replacements(to, from_))


def send_emails(participants_dict, extraction):
    """
    Sends emails to everyone, using yagmail and the account specified in .env
    """

    yag = yagmail.SMTP(email_address, email_password)

    for from_, to in tqdm(extraction.items(), desc="Sending emails", ncols=75):
        from_ = participants_dict[from_]
        to = participants_dict[to]

        content = read_template_file("mail-text.txt", from_, to)
        content += "\n\n\n\n\n\nSent by py-secretsanta: https://github.com/davidemerli/py-secretsanta"

        from_email = from_["mail"]

        debug(f"sent email to {from_email}")
        debug(content)

        yag.send(to=from_email, subject="Secret Santa 2021!", contents=content)


def main():
    # retrieve participants
    participants_dict = get_participants()
    # get only the keys
    participants = list(participants_dict.keys())
    info("Parsed participants")

    # send participants their information to check that everything is ok
    if click.confirm(
        "Do you want to send everyone a test mail to verify everything is working?"
    ):
        send_test_emails(participants_dict)

        info("Done! Please rerun the script once verified!")
        return

    # retrieve matches to avoid
    bans = parse_bans(participants)
    info("Parsed matches to avoid")

    # extract matches
    extraction, tries = compute_extraction(participants, bans)

    for v, k in extraction.items():
        debug(f"{v} -> {k}")

    info(
        f"Considering {sum([len(k) for _, k in bans.items()])} matches to avoid, "
        f"I found a valid combination in {tries} tries"
    )

    send_emails(participants_dict, extraction)

    if click.confirm(
        "Do you want to display the matches as a graph "
        "(keep in mind that this will not preserve the secretness of the event!) ?",
        default=False,
    ):

        hide_names = click.confirm(
            "Do you want to spoof the names as numbers?", default=True
        )

        draw_graph(participants_dict, extraction, hide_names=hide_names)


if __name__ == "__main__":
    main()
