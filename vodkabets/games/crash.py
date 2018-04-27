from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_socketio import emit, Namespace

from base64 import urlsafe_b64encode
from copy import deepcopy
from json import dumps

from vodkabets.application import app

from vodkabets.models.record import Record
from vodkabets.models.user import User

crash_blueprint = Blueprint("crash", __name__)

@crash_blueprint.route("/")
def crash():
    return render_template("/crash/crash.html")

class CrashGame(Namespace):
    def __init__(self, socket):
        super().__init__(namespace="/_crash")
        self.current_round = CrashRound()

        self.socket = socket
        self.socket.on_namespace(self)
        self.socket.start_background_task(self.update)

    def update(self):
        while True:
            print("Sleeping!")
            self.socket.sleep(10)

    def on_connect(self):
        if current_user.is_authenticated:
            print("User " + current_user.username + " joined!")

        # Resend bets list to everyone
        self.update_crash_bets()

    def on_place_bet(self, bet_amount, client_seed):
        #print(bet_amount, client_seed)

        # Only bet if user is authenticated, otherwise show error
        if current_user.is_authenticated:
            # Check if bet has already been placed
            if any(bet["user_sid"] == current_user.get_id() for bet in self.current_round.bets):
                emit("flash", ("You've already placed a bet!", "ERROR"), namespace="/", room=request.sid)
                return

            # Convert the bet amount to be a number
            if bet_amount.isdigit():
                bet_amount = int(bet_amount)
            else:
                emit("flash", ("Invalid bet amount submitted!", "ERROR"), namespace="/", room=request.sid)
                return

            # Be sure bet is a valid amount
            if bet_amount < app.config["CRASH_MIN_BET"]:
                emit("flash", ("Bet is below minimum requirement!", "ERROR"), namespace="/", room=request.sid)
                return
            elif bet_amount > current_user.vlads:
                emit("flash", ("Not enough vlads!", "ERROR"), namespace="/", room=request.sid)
                return

            # Update the amount of vlads that the user has
            current_user.vlads -= bet_amount
            current_user.save()

            # Place the bet
            self.current_round.add_bet(current_user.get_id(), bet_amount, client_seed)

            emit("flash", ("Bet sucessfully placed!", "SUCCESS"), namespace="/", room=request.sid)
            self.update_crash_bets() # Update bets list
        else:
            emit("flash", ("Please login to do that!", "ERROR"), namespace="/", room=request.sid)
            return

    def update_crash_bets(self):
        # slice the list so it's a copy
        bets_list = deepcopy(self.current_round.bets)

        # modify bets so it doesn't leak any important data
        for index, bet in enumerate(bets_list):
            # set the username property to be the better's name
            bet["username"] = User.get(User.session_token == bet["user_sid"]).username

            # Delete private info
            bet.pop("client_seed", None)
            bet.pop("user_sid", None)

        # Gen a base64 encoded version of bets_list and sends to everyone
        b64 = urlsafe_b64encode(dumps(bets_list).encode()).decode()
        emit("update_crash_bets", (b64), broadcast=True)

class CrashRound:
    def __init__(self):
        super().__init__()

        self.bets = []

    def add_bet(self, user_sid, amount, client_seed):
        self.bets.append({
            "user_sid": user_sid,
            "amount": amount,
            "cashout_multiplier": None,
            "profit": None,
            "client_seed": client_seed
        })

    def cashout_bet(self, user_sid, multiplier):
        bet = next(bet["user_sid"] == current_user.get_id() for bet in self.bets)
        if bet["withdraw_multiplier"] or bet["profit"]:
            emit("flash", ("Your bet has already been cashed-out!", "ERROR"), namespace="/", room=request.sid)
            return
        bet["cashout_multiplier"] = multiplier
        bet["profit"] = bet["amount"]*bet["cashout_multiplier"]

    def gen_hash(self):
        pass

    def gen_record(self):
        return Record()
