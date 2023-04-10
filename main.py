import os
import sqlite3
import time

from photocard import PhotocardService
from pushed import Pushed

connection = sqlite3.connect("photocard.db")

with open("migrate.sql", 'r') as handle:
    connection.executescript(handle.read())

pushed = Pushed(os.getenv("PUSHED_APP_KEY"), os.getenv("PUSHED_APP_SECRET"))
photocard = PhotocardService()
photocard.logon(os.getenv("TFL_PHOTOCARD_EMAIL"), os.getenv("TFL_PHOTOCARD_PASSWORD"))

cycles = 0
while True:
    print(f"---- Session Cycle {cycles}:")
    photocard.extend_session()
    print(f"Polling cards for person {os.getenv('TFL_PHOTOCARD_PERSON')}")
    cards = photocard.cards_for_person(int(os.getenv("TFL_PHOTOCARD_PERSON")))
    print(f"Cards: {len(cards)}")
    for card in cards:
        print(f"Card Number: {card.oyster_card_number} Type: {card.card_type.name}")
        print("  Polling DB for most recent balance")
        old_balance = connection.execute(
            "SELECT oyster_card_balance FROM oyster_balance WHERE oyster_card_number=? ORDER BY time DESC LIMIT 1",
            (card.oyster_card_number,)).fetchone()
        new_balance = card.prepaid_balance

        if old_balance is None:
            old_balance = -1
        elif isinstance(old_balance, tuple):
            old_balance = old_balance[0]
        print(f"  Balance £{old_balance:.2f} -> £{new_balance:.2f}")
        if old_balance != new_balance or cycles == 0:
            print("  Change or initial cycle detected! Pushing notification")
            card_number_string = ""
            if "NOTIFICATON_PUSH_CARD_NUMBER" in os.environ:
                card_number_string = f" [Oyster: {card.oyster_card_number} {card.card_type.value}]"
            pushed.push_app(f"💷 Your balance is £{new_balance:.2f} (was £{old_balance:.2f})" + card_number_string)

        print(f"  Saving new balance for {card.oyster_card_number}")
        connection.execute("INSERT INTO `oyster_balance` (oyster_card_number, oyster_card_balance) VALUES (?,?)",
                           (card.oyster_card_number, card.prepaid_balance))
    connection.commit()
    cycles += 1
    time.sleep(60)  # Poll every minute
