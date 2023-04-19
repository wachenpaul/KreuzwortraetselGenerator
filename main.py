import os
import random
import pygame
import math

WORDLIST = []

CROSSWORDS = []


def load_words():
    with open('words.txt', 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            line = line.upper()
            if line:
                WORDLIST.append(line)
        f.close()
    # mix the words
    random.shuffle(WORDLIST)


def get_random_word():
    return random.choice(WORDLIST)


def get_word_with_letter(letter):
    # return a word that contains the given letter
    for word in WORDLIST:
        if letter in word and word not in [word.word for word in CROSSWORDS]:
            return word, word.index(letter)


def display_crossword():
    # calculate the matrix size
    max_x = -math.inf
    max_y = -math.inf
    for word in CROSSWORDS:
        for letter in word.letters:
            if letter.x > max_x:
                max_x = letter.x
            if letter.y > max_y:
                max_y = letter.y

    min_x = math.inf
    min_y = math.inf
    for word in CROSSWORDS:
        for letter in word.letters:
            if letter.x < min_x:
                min_x = letter.x
            if letter.y < min_y:
                min_y = letter.y

    print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}")

    max_word_len = max(len(word.word) for word in CROSSWORDS)
    # calculate square_size based on the length of the longest word
    square_size = 1/max_word_len * 750
    width = (max_x - min_x + 1) * square_size
    height = (max_y - min_y + 1) * square_size

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Crossword')

    # fill the background with white
    screen.fill((255, 255, 255))

    # draw the grid
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            pygame.draw.rect(screen, (0, 0, 0), (square_size * (x - min_x),
                                                 square_size * (y - min_y), square_size, square_size), 1)

    # draw the letters
    for letter in [letter for word in CROSSWORDS for letter in word.letters]:
        font = pygame.font.Font(None, round(square_size * 0.8))
        text = font.render(letter.letter, True, (0, 0, 0))
        text_rect = text.get_rect(center=((letter.x - min_x) * square_size + square_size / 2,
                                          (letter.y - min_y) * square_size + square_size / 2))
        screen.blit(text, text_rect)

    # draw small coordinates in the bottom middle of a square
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            font = pygame.font.Font(None, round(square_size * 0.3))
            text = font.render(f"({x}, {y})", True, (120, 120, 120))
            text_rect = text.get_rect(center=((x - min_x) * square_size + square_size / 2,
                                              (y - min_y) * square_size + square_size / 2 + 15))
            screen.blit(text, text_rect)

    pygame.display.flip()

    # wait for the user to close the window
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                os._exit(0)


def check_overlap(word):
    ALL_LETTERS = [letter for word in CROSSWORDS for letter in word.letters]

    for letter in ALL_LETTERS:
        if letter.x == word.letters[0].x and letter.y == word.letters[0].y and letter.related_words[0] != word:
            print(f"Overlap found for word {word.word}")
            print(
                f"Letter {letter.letter} at ({letter.x}, {letter.y}) is already in word {letter.related_words[0].word}")
            return True
    print(f"No overlap found for word {word.word}")
    return False

    print(f"No overlap found for word {word.word}")


class Letter:
    def __init__(self, letter, x, y, related_word):
        self.letter = letter
        self.related_words = [related_word]
        self.x = x
        self.y = y


class Word:
    def __init__(self, word, is_horizontal=True):
        self.word = word
        self.horizontal = is_horizontal
        self.letters = []
        self.set_letters()

    def set_letters(self):
        for letter in self.word:
            if self.horizontal:
                self.letters.append(Letter(letter, len(self.letters), 0, self))
            else:
                self.letters.append(Letter(letter, 0, len(self.letters), self))

    def set_coordinates(self, index):
        for letterIndex, letter in enumerate(self.letters):
            origin = (self.letters[index].x, self.letters[index].y)
            if self.horizontal:
                letter.x = origin[0] + letterIndex - index
                letter.y = origin[1]
            else:
                letter.x = origin[0]
                letter.y = origin[1] + letterIndex - index

    def create_crossword(self):
        word_index = random.randint(0, len(self.word) - 1)
        crossword, crossword_index = get_word_with_letter(
            self.word[word_index])

        new_word = Word(crossword, not self.horizontal)
        self.letters[word_index].related_words.append(new_word)
        new_word.letters[crossword_index] = self.letters[word_index]

        new_word.set_coordinates(crossword_index)

        if check_overlap(new_word):
            self.create_crossword()

        CROSSWORDS.append(new_word)


load_words()

CROSSWORDS.append(Word(get_random_word()))

for i in range(10):
    CROSSWORDS[random.randint(0, len(CROSSWORDS) - 1)].create_crossword()

display_crossword()
