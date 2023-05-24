# Hangman Game API 

API for a Hangman game. Player can guess in upper or lower case. eg json body = letter: "a".
Player cannot guess the same letter twice (notified if they try).

`POST /games/`  
Starts a new game of Hangman. This endpoint should initialize a new game with a word and return a game ID.

`GET /games/{game_id}`  
Retrieves the current state of the game identified by the provided `game_id`. The response should include the word with masked letters, the incorrect guesses made so far, the number of remaining attempts, and the game status (e.g. `in progress,` `won` or `lost`).

`POST /games/{game_id}/guesses`  
Allows the player to make a letter guess for the game identified by `game_id`. The guess should be submitted as the request body in JSON format, containing the guessed letter. The response should include the updated game state after the guess.

`DELETE /games/{game_id}`  
Remove the game data for the given id. This action is non-rversable.
