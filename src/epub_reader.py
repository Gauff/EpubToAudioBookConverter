from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from reference_cleaner import remove_foot_notes
import re
from bs4.element import Comment

authorized_file_name_fragments = [
    "pre",  # preface
    "chap",  # chapter / chapitre
    "ch",  # chapter / chapitre
    "appen",  # appendix
    "section"
]

split_fragments = ["split"]


def get_title_and_chapters_text(epub_file_path):
    book = epub.read_epub(epub_file_path)

    chapters_text = []

    # First try by filtering file names
    items = [x for x in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
             if type(x) is ebooklib.epub.EpubHtml
             and x.media_type == 'application/xhtml+xml'
             and any(fragment in x.file_name for fragment in authorized_file_name_fragments)]

    # If no filename matches, it is probably a split
    if len(items) == 0:
        items = [x for x in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
                 if type(x) is ebooklib.epub.EpubHtml
                 and x.media_type == 'application/xhtml+xml'
                 and any(fragment in x.file_name for fragment in split_fragments)]

    # If no filename matches, take them all
    if len(items) == 0:
        items = [x for x in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
                 if type(x) is ebooklib.epub.EpubHtml
                 and x.media_type == 'application/xhtml+xml']

    for item in items:
        utf8_html_content = item.content.decode('utf-8')
        chapter_text = _html_to_text(utf8_html_content)
        chapters_text.append(chapter_text)

    return book.title, chapters_text


def replace_special_spaces(text):
    text = text.replace("\u00A0", " ").replace("\u2008", " ").replace("\u2009", " ")
    return text


def contains_only_whitespace(text):
    # Define the regular expression pattern
    pattern = re.compile(r'^[\s\r\n]+$')

    # Use match() to check if the entire string matches the pattern
    match = re.match(pattern, text)

    # Return True if there's a match (string contains only whitespace characters), False otherwise
    return bool(match)


def tag_visible_filter(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    #    if contains_only_whitespace(str(element)):
    #        return False
    return True


def contains_not_only_whitespace_filter(element):
    return contains_only_whitespace(str(element)) is False


def concatenate_strings_with_newline(texts):
    concatenated_strings = []
    current_string = ""

    for text in texts:
        # Check if the string is surrounded by "\n"
        if contains_only_whitespace(text):
            # If current_string is not empty, add it to the result list
            if current_string:
                concatenated_strings.append(current_string)
                current_string = ""
        else:
            # Concatenate the string with current_string
            # current_string += text.strip()
            current_string += text

    # Add the last string if it's not empty
    if current_string:
        concatenated_strings.append(current_string)

    return concatenated_strings


def _html_to_text(
        utf8_html_content,
        remove_footnotes=True,
        visible_filter=True,
        concatenate_surrounded_by_newlines=False,
        punctuate=True):
    # Remove footnotes from the HTML content
    if remove_footnotes:
        utf8_html_content = remove_foot_notes(utf8_html_content)

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(utf8_html_content, 'html.parser')

    texts = soup.findAll(text=True)

    if visible_filter:
        texts = filter(tag_visible_filter, texts)

    # Concatenate group of consecutive strings surrounded by only \n
    if concatenate_surrounded_by_newlines:
        texts = concatenate_strings_with_newline(texts)
    else:
        texts = filter(contains_not_only_whitespace_filter, texts)

    texts = [replace_special_spaces(t.strip()) for t in texts]

    if punctuate:
        texts = [t if ends_with_punctuation(t) else f"{t}. " for t in texts]

    text_content = ' '.join(texts)

    return text_content


def ends_with_punctuation(text):
    if text == '':
        return False

    # Define a regular expression pattern to match punctuation at the end of the text
    punctuation_pattern = re.compile(r'[.!?:;,]$')

    # Use search() to find the pattern at the end of the text
    match = re.search(punctuation_pattern, text)

    # Return True if a match is found, indicating the text ends with punctuation
    return bool(match)


def emphasize_speech(text):
    if text == '':
        return text

    # Define the pattern to detect speech markers
    speech_pattern = re.compile(r'(\s*[—–]\s+)([A-Z])')

    # Split the text into lines
    lines = text.split('\n')

    # Iterate through each line and add a carriage return before each speech marker
    emphasized_lines = []
    for line in lines:
        # Use regular expression to detect speech markers and ensure space after them
        line = re.sub(speech_pattern, r'\n\1\2', line)
        emphasized_lines.append(line)

    # Join the lines back into a single string
    emphasized_text = '\n'.join(emphasized_lines)

    return emphasized_text


def remove_carriage_returns(text):
    if text == '':
        return text

    # Step 1: Split the text into sentences based on punctuation marks
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Step 2: Remove carriage returns within each sentence
    cleaned_sentences = []
    for sentence in sentences:
        cleaned_sentence = re.sub(r'(\r\n|\r|\n)', ' ', sentence)
        cleaned_sentences.append(cleaned_sentence.strip())

    # Join the cleaned sentences back into a single string
    cleaned_text = ' '.join(cleaned_sentences)

    return cleaned_text


def convert_whitespace_to_dot(text):
    if text == '':
        return text

    # Define a regular expression pattern to match sequences of 3 or more whitespace characters
    whitespace_pattern = re.compile(r'\s{2,}')

    # Replace matched sequences with a dot
    converted_text = re.sub(whitespace_pattern, '. ', text)

    return converted_text


def fix_first_char_followed_by_a_dot(text):
    pattern = r'\b([A-Z])\. (\w+)'

    # Use sub() to replace the matched pattern with the corrected text
    corrected_text = re.sub(pattern, r'\1\2', text)

    return corrected_text


def remove_dot_after_lowercase(text):
    # Define the regular expression pattern
    pattern = r'\b([a-zA-Z]+)\.\s([a-z]+)'

    # Use sub() to replace the dot and whitespace with a whitespace
    cleaned_text = re.sub(pattern, r'\1 \2', text)

    return cleaned_text


def _get_chapter_text(item):
    utf8_html_content = item.content.decode('utf-8')
    chapter_text = _html_to_text(utf8_html_content)
    chapter_text_2 = remove_carriage_returns(chapter_text)
    chapter_text_3 = convert_whitespace_to_dot(chapter_text_2)
    chapter_text_4 = emphasize_speech(chapter_text_3)
    chapter_text_5 = fix_first_char_followed_by_a_dot(chapter_text_4)
    chapter_text_6 = remove_dot_after_lowercase(chapter_text_5)
    return chapter_text_6


def get_title_and_chapters(epub_file_path):
    book = epub.read_epub(epub_file_path)

    # First try by filtering file names
    chapters_filename_and_text = [(x.file_name, _get_chapter_text(x)) for x in
                                  book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
                                  if type(x) is ebooklib.epub.EpubHtml
                                  and x.media_type == 'application/xhtml+xml']

    chapters_filename_and_text = [x for x in chapters_filename_and_text if x[1].replace('\n', '') != '']

    return book.title, chapters_filename_and_text
