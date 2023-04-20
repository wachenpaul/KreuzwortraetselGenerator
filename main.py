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


def get_word_with_letter(letter, exclude=[]):
    # return a word that contains the given letter
    for word in WORDLIST:
        if letter in word and word not in [word.word for word in CROSSWORDS] and word not in exclude:
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
    square_size = 500 / max_word_len
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
        for word_letter in word.letters:
            if letter.x == word_letter.x and letter.y == word_letter.y and letter.letter != word_letter.letter:
                print(
                    f"{word_letter.x}, {word_letter.y} is already taken by {letter.letter} with coordinates {letter.x}, {letter.y}")
                return True

            origin = (word_letter.x, word_letter.y)
            # print out if the letter is a crossing of two words or not. This is determined by the number of related words, 1 means it is not a crossing, 2 means it is a crossing
            if not len(letter.related_words) == 2:
                # if it is not a crossing, check around the letter so that words that dont have the same related word are not touching each other
                print(
                    f"checking around {word_letter.letter} at {word_letter.x}, {word_letter.y}")
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if x == 0 and y == 0:
                            continue
                        if (word_letter.x + x, word_letter.y + y) == origin:
                            continue
                        # TODO

    print(f"No overlap found for word {word.word}")
    return False


def check_common_list_item(list1, list2):
    for item in list1:
        if item in list2:
            return True
    return False


def search_coordinate(x, y):
    for word in CROSSWORDS:
        for letter in word.letters:
            if letter.x == x and letter.y == y:
                return letter
    return None


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

        old_words = []
        while check_overlap(new_word):
            old_words.append(new_word.word)
            # remove the old word from the list of related words
            self.letters[word_index].related_words.remove(new_word)
            word_index = random.randint(0, len(self.word) - 1)
            crossword, crossword_index = get_word_with_letter(
                self.word[word_index], exclude=old_words)
            print(
                f"got new crossword: {crossword} for letter {self.word[word_index]} with index {word_index}")
            new_word = Word(crossword, not self.horizontal)
            self.letters[word_index].related_words.append(new_word)
            new_word.letters[crossword_index] = self.letters[word_index]

            new_word.set_coordinates(crossword_index)

        CROSSWORDS.append(new_word)


load_words()

CROSSWORDS.append(Word(get_random_word()))

for i in range(2):
    CROSSWORDS[random.randint(0, len(CROSSWORDS) - 1)].create_crossword()

display_crossword()
