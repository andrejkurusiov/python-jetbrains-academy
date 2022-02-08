"""The HANGMAN game."""
from random import choice
from string import ascii_lowercase

GUESS_WORDS = ['python', 'java', 'kotlin', 'javascript']
MAX_MISTAKES = 8  # number of tries for guessing a word


def show_chosen_letter(word: str, letters: set) -> str:
    """Shows guessed <letters> letters of a given <word>; the rest is replaced by '-' symbol."""
    shadow_word = list('-' * len(word))
    for i, letter in enumerate(word):
        if letter in letters:
            shadow_word[i] = letter
    return ''.join(shadow_word)


def check_incorrect_input(user_input: str) -> str:
    """Checks if user has a single lower ascii char input, and if not return an error message."""
    if len(user_input) != 1:
        return 'You should input a single letter'
    if user_input not in ascii_lowercase:
        return 'Please enter a lowercase English letter'
    return None


if __name__ == '__main__':
    print('H A N G M A N')
    while menu := input('Type "play" to play the game, "exit" to quit: '):
        if menu == 'exit':
            break
        elif menu != 'play':
            continue
        chosen_word = choice(GUESS_WORDS)
        letters = set()
        lives = MAX_MISTAKES
        # Play game
        while True:
            shadow_word = show_chosen_letter(chosen_word, letters)
            print('\n' + shadow_word)
            # win condition
            if shadow_word == chosen_word:
                print("You guessed the word!\nYou survived!")
                break
            # check input
            user_letter = input('Input a letter: ')
            if error_msg := check_incorrect_input(user_letter):
                print(error_msg)
                continue
            # letter was guessed before
            if user_letter in letters:
                print("You've already guessed this letter")
                continue
            letters.add(user_letter)
            # wrong guess
            if user_letter not in chosen_word:
                print("That letter doesn't appear in the word")
                lives -= 1
            # loosing condition
            if lives <= 0:
                print('You lost!')
                break
