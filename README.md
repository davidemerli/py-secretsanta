# Py-SecretSanta

<img src="https://raw.githubusercontent.com/S0NN1/py-secretsanta/6427c0a1807baa731cd0eefc76eb8d64264fa3b1/.github/sleigh-solid.svg" width=150px height=150px align="right"  />

Python script for Secret Santa!

This script will send emails to all partecipants containing address' info.

Fill `partecipants.csv` with all the partecipants following column order (DO NOT DELETE FIRST ROW!).

You need to fill this file with the following data:
`name, address, postal_code, city, province, mail, phone, extra`

## Installation
You need python3 and pip

```bash
pip3 install -r requirements.txt
```

or 

```bash
pip install -r requirements.txt
```

then run the script with

```bash
python3 main.py
```

or 

```bash
python main.py
```

## Authentication

This script uses email and password to authenticate the email that sends every email to the partecipants.

If you use a google account, make sure you enable untrusted apps:

Go to: `https://www.google.com/settings/security/lesssecureapps` while logged in.
Then enable it with the switch button.

You need to put your credentials in the `.env` file

## Template email

You can personalize the emails by editing `mail-text.txt` file.
You can also personalize the TEST message by editing `test-mail-text.txt` file.

To configure the mail text, you can use the following variables:

```
$to_fullname, $to_firstname, $to_phone, $to_address, 
$to_province, $to_city, $to_postalcode, $to_extra

$from_fullname, $from_firstname, $from_phone, $from_address, 
$from_province, $from_city, $from_postalcode, $from_extra
```

... where obviously `from` is the one who needs to send the present, `to` is the one who will receive it.

The script will select a random present suggestion for each partecipant if you include `$random_suggestion` in the mail text.

Suggestions are taken from `suggestions.txt` file. Put one per line.

## Avoid Specific Matches

To avoid matches simply add `name1->name2`, `name1<->name2` or `name1<-name2` to `avoid_matches.txt` (one per row).

for example if you want to avoid matches between `name1` and `name2`, where `name1` is the sender and `name2` is the receiver, you can add: `name1->name2`

putting `<->` will avoid every match between `name1` and `name2`
