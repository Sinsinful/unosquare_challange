import uuid
import random

from flask import (Blueprint, abort, jsonify, request)
from werkzeug.exceptions import HTTPException

mod = Blueprint('games', __name__, url_prefix='/games')

games = {}

word_list = ["Banana", "Canine", "Unosquare", "Airport"]

def generate_word():
    return random.choice(word_list)

def mask_word(word, guessed_letters):
    #lower case the word for guesses to match
    masked_word = ""
    word = word.lower()
    for letter in word:
            if letter not in guessed_letters:
                masked_word += "_"
            elif letter in guessed_letters:
                masked_word += letter
    return masked_word.strip()

def is_valid_guess(guess, game):
    if not guess.isalpha() or len(guess) != 1:
        return False
    return True

#helper function to take the correct letters out of guessed letters for the return for incorrect letters
def remove_letters(a, b):
    c = []
    for letter in a:
        if letter not in b:
            c.append(letter)
    return c

#updated with a status field to help with retreival at game won/lost
@mod.route('/', methods=['POST'])
def start_game():
    game_id = str(uuid.uuid4())
    word = generate_word()
    games[game_id] = {
        "word": word,
        "status": "In progress",
        "guessed_letters": [],
        "attempts": 6
    }
    return game_id, 201

@mod.route('/<string:game_id>', methods=['GET'])
def get_game_state(game_id):
    game = games.get(game_id)
    if game is None:
        abort(404)
    masked_word = mask_word(game["word"], game["guessed_letters"])
    return jsonify({
        "incorrect_guesses": remove_letters(game["guessed_letters"], game["word"]),
        "remaining_attempts": game["attempts"],
        "status": game["status"],
        "word": masked_word,
    })

@mod.route('/<string:game_id>/guesses', methods=['POST'])
def make_guess(game_id):
    game = games.get(game_id)
    if game is None:
        abort(404)
    if not request.json or 'letter' not in request.json:
        abort(400)
    guess = request.json['letter'].lower()
    if not is_valid_guess(guess, game):
        return jsonify({"Message": "Guess must be supplied with 1 letter"}), 400
    
    #return error message if letter already used
    if guess in game["guessed_letters"]:
        return jsonify({"Message": "Letter already guessed. Please choose another letter."}), 400
    
    #check for game lost status
    if game["attempts"] == 0:
        game["status"] = "Lost"
        return jsonify({
        "game_over": "Game over no further guesses can be made",
        "incorrect_guesses": remove_letters(game["guessed_letters"], game["word"]),
        "remaining_attempts": game["attempts"],
        "status": game["status"],
        "game word was": game["word"],
    })


   
    #subtract an atttempt if guessed letter not in word
    if guess not in game["word"]:      
        game["attempts"] = game["attempts"] -1
    
    #game loss check 
    if game["attempts"] < 1:
        game["status"] = "Lost"
        return jsonify({
        "incorrect_guesses": remove_letters(game["guessed_letters"], game["word"]),
        "remaining_attempts": game["attempts"],
        "status": game["status"],
        "game word was": game["word"],
    })

    #add guessed letter to guessed list
    game["guessed_letters"] += guess
             
    masked_word = mask_word(game["word"], game["guessed_letters"])
    masked_word = masked_word.lower()
    game["word"] = game["word"].lower()

    #check for game win
    if game["word"] == masked_word:
        game["status"] = "Won"
        return jsonify({
        "winner": "Congratulations you have won.",
        "incorrect_guesses": remove_letters(game["guessed_letters"], game["word"]),
        "remaining_attempts": game["attempts"],
        "status": game["status"],
        "unmasked": game["word"],
    })


    return jsonify({
        "incorrect_guesses": remove_letters(game["guessed_letters"], game["word"]),
        "remaining_attempts": game["attempts"],
        "status": "In Progress",
        "word": masked_word,
        "unmasked": game["word"],
    })

# Added delete game function
@mod.route('/<string:game_id>', methods=['DELETE'])
def delete(game_id):
    games.pop(game_id)

    return jsonify({
        "deleted game": game_id,
        
    })

