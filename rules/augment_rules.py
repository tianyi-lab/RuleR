
import re
import string
import random

import spacy
from collections import Counter

################################################
# DEFINE RULE TYPES
################################################

MAX_COUNT = 5 

RULE_TYPES = [
    'FREQUENCY_WORD',
    'FREQUENCY_ADJ',
    'FREQUENCY_NOUN',
    'FREQUENCY_VERB',
    'FREQUENCY_LETTER',
    'FREQUENCY_CHAR',
    'NUM_WORD',
    'NUM_SENTENCE',
    'NUM_PARAGRAPH',
    'NUM_BULLET',
    'REPEAT_INSTRUCTION',
    'REPEAT_RESPONSE',
    'CASE_LOW',
    'CASE_UP',
    'CASE_UP_LETTER',
    'CASE_UP_WORD',
    'CASE_UP_SENTENCE',
    'CASE_UP_PARAGRAPH',
    'PUNCTUATION_REPLACEMENT',
    'PUNCTUATION_IGNORANCE',
    'FORMAT_WRAP_WORD',
    'FORMAT_WRAP_SENTENCE',
    'FORMAT_WRAP_BULLET',
    'FORMAT_WRAP_PARAGRAPH',
    'FORMAT_WRAP_INSTRUCTION',
    'FORMAT_WRAP_RESPONSE',
]

RULE_TYPES_BULLET = [
    'NUM_BULLET',
    'FORMAT_WRAP_BULLET',
]

RULE_TYPES_NO_BULLET = [
    'FREQUENCY_WORD',
    'FREQUENCY_ADJ',
    'FREQUENCY_NOUN',
    'FREQUENCY_VERB',
    'FREQUENCY_LETTER',
    'FREQUENCY_CHAR',
    'NUM_WORD',
    'NUM_SENTENCE',
    'NUM_PARAGRAPH',
    'REPEAT_INSTRUCTION',
    'REPEAT_RESPONSE',
    'CASE_LOW',
    'CASE_UP',
    'CASE_UP_LETTER',
    'CASE_UP_WORD',
    'CASE_UP_SENTENCE',
    'CASE_UP_PARAGRAPH',
    'PUNCTUATION_REPLACEMENT',
    'PUNCTUATION_IGNORANCE',
    'FORMAT_WRAP_WORD',
    'FORMAT_WRAP_SENTENCE',
    'FORMAT_WRAP_PARAGRAPH',
    'FORMAT_WRAP_INSTRUCTION',
    'FORMAT_WRAP_RESPONSE',
]

RULE_TYPES_NO_BULLET_NO_FORMAT_WRAP = [
    'FREQUENCY_WORD',
    'FREQUENCY_ADJ',
    'FREQUENCY_NOUN',
    'FREQUENCY_VERB',
    'FREQUENCY_LETTER',
    'FREQUENCY_CHAR',
    'NUM_WORD',
    'NUM_SENTENCE',
    'NUM_PARAGRAPH',
    'REPEAT_INSTRUCTION',
    'REPEAT_RESPONSE',
    'CASE_LOW',
    'CASE_UP',
    'CASE_UP_LETTER',
    'CASE_UP_WORD',
    'CASE_UP_SENTENCE',
    'CASE_UP_PARAGRAPH',
    'PUNCTUATION_REPLACEMENT',
    'PUNCTUATION_IGNORANCE',
]

RULE_TYPES_NO_BULLET_FORMAT_WRAP = [
    'FORMAT_WRAP_WORD',
    'FORMAT_WRAP_SENTENCE',
    'FORMAT_WRAP_PARAGRAPH',
    'FORMAT_WRAP_INSTRUCTION',
    'FORMAT_WRAP_RESPONSE',
]

RULE_TYPES_CODE = [
    'REPEAT_INSTRUCTION',
    'REPEAT_RESPONSE',
    'FORMAT_WRAP_INSTRUCTION',
    'FORMAT_WRAP_RESPONSE',
]

OVERALL_INSTRUCTION_LIST = [
    """{meta_instruction}\n{instruction_ori}""",
    """{instruction_ori}\n{meta_instruction}""",
    """{meta_instruction}\n\n{instruction_ori}""",
    """{instruction_ori}\n\n{meta_instruction}""",
]

def do_NONE(data_item):
    data_item['type'] = 'None'
    return data_item

################################################
# DEFINE FOTMAT
################################################

FORMAT_BRACKET_LIST = [
    '({text})', 
    '(({text}))', 
    '[{text}]', 
    '[[{text}]]', 
    '<{text}>',
    '<<{text}>>',
    '|{text}|',
    '[|{text}|]',
    '<|{text}|>',
    '||{text}||',
    '|-|{text}|-|',
    '-|{text}|-',
    '-{text}-',
    '#{text}#',
    '###{text}#',
    '##{text}#',
    '\{text}\\',
    '\{text}/',
    '/{text}\\',
    '*{text}*', 
    '**{text}**', 
    '***{text}***', 
    '***{text}*', 
    '**{text}*', 
    '"{text}"', 
    '@{text}@', 
    '@@{text}@@', 
    '@@@{text}@', 
    '${text}$', 
    '$${text}$$', 
    '$$${text}$', 
]

FORMAT_TEXT_LIST = [
    ('BEGAIN','END'),
    ('START','END'),
    ('RESPONSE','END'),
    ('RESPONSE','CLOSE'),
    ('OPEN', 'CLOSE'),
    ('INITIATE', 'TERMINATE'),
    ('ENTRY', 'EXIT'),
    ('LAUNCH', 'CONCLUDE'),
    ('COMMENCE', 'COMPLETE'),
    ('START POINT', 'END POINT'),
    ('ORIGIN', 'DESTINATION'),
    ('KICKOFF', 'WRAP UP'),
    ('RES_START', 'RES_END'),
    ('RES_BEGIN', 'RES_END'),
    ('RES', '/RES'),
    ('BEGIN', 'FINISH'),
    ('ACTIVATE', 'DEACTIVATE'),
    ('BEGINNING', 'CLOSURE'),
    ('STARTUP', 'SHUTDOWN'),
    ('INIT', 'FINALIZE'),
    ('BOOT', 'HALT'),
    ('ENGAGE', 'DISENGAGE'),
    ('LAUNCH', 'LAND'),
    ('BEGIN_ACTION', 'END_ACTION'),
    ('START_SESSION', 'END_SESSION'),
    ('ON', 'OFF'),
    ('TRIGGER', 'STOP'),
    ('INITIATE_PROCESS', 'TERMINATE_PROCESS'),
    ('STARTUP_SEQUENCE', 'SHUTDOWN_SEQUENCE'),
    ('OPEN_SESSION', 'CLOSE_SESSION')
]

FORMAT_ORDER_LIST = [
    '1st',
    '2nd',
    '3rd',
]

def get_combined_format():
    indicator_format_braket = random.randint(0, len(FORMAT_BRACKET_LIST)-1)
    format_bracket = FORMAT_BRACKET_LIST[indicator_format_braket]
    indicator_format_text = random.randint(0, len(FORMAT_TEXT_LIST)-1)
    format_text = FORMAT_TEXT_LIST[indicator_format_text]
    combined_format = format_bracket.format(text=format_text[0]) + '{text}' + format_bracket.format(text=format_text[1])
    return combined_format

################################################
# DEFINE PUNCT
################################################

PUNCT_TO_REPLACE = [
    (',','commas'),
    ('.','periods'),
    'ALL',
]

PUNCT_REPLACE_WITH = [
    ';',
    '|',
    '_',
    '-',
    '@',
    '#',
    '$',
]

################################################
# FUNCTION: get_response_stastics
################################################

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

def get_pos_counts(text):
    # Process the text with spaCy
    doc = nlp(text)
    
    # Define dictionaries for each POS category
    adj_dict = {}
    noun_dict = {}
    verb_dict = {}
    
    # Categorize, lemmatize, and count the POS
    for token in doc:
        lemma = token.lemma_
        if token.pos_ == 'ADJ':
            if lemma in adj_dict:
                adj_dict[lemma] += 1
            else:
                adj_dict[lemma] = 1
        elif token.pos_ == 'NOUN':
            if lemma in noun_dict:
                noun_dict[lemma] += 1
            else:
                noun_dict[lemma] = 1
        elif token.pos_ == 'VERB':
            if lemma in verb_dict:
                verb_dict[lemma] += 1
            else:
                verb_dict[lemma] = 1
    
    return adj_dict, noun_dict, verb_dict

def get_text_statistics(text):
    doc = nlp(text)
    
    # Word count
    word_count = len([token for token in doc if not token.is_punct])
    
    # Sentence count
    sentence_count = len(list(doc.sents))
    
    # Paragraph count (assuming paragraphs are separated by two newlines)
    paragraphs = re.split(r'\n\s*\n', text.strip())
    paragraph_count = len(paragraphs)
    
    # Bullet points count (assuming bullet points start with -, *, or digits followed by .)
    bullet_points = re.findall(r'(^[\*\-\d]+\.)', text, re.MULTILINE)
    bullet_point_count = len(bullet_points)
    
    return word_count, sentence_count, paragraph_count, bullet_point_count

def get_response_stastics(text):

    adj_dict, noun_dict, verb_dict = get_pos_counts(text)
    word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(text)

    stastics_dict = {
        'adj_dict': adj_dict,
        'noun_dict': noun_dict,
        'verb_dict': verb_dict,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'paragraph_count': paragraph_count,
        'bullet_point_count': bullet_point_count,
    }

    return stastics_dict

def is_code_snippet(text):
    # Common patterns in multiple programming languages
    patterns = {
        'python': [
            r"def\s+\w+\s*\(.*\)\s*:",  # function definitions
            r"class\s+\w+\s*\(.*\)\s*:",  # class definitions
            r"import\s+\w+",  # import statements
            r"from\s+\w+\s+import\s+\w+",  # from ... import ... statements
            r"if\s+.*\s*:",  # if statements
            r"for\s+.*\s*in\s+.*\s*:",  # for loops
            r"while\s+.*\s*:",  # while loops
            r"try\s*:",  # try statements
            r"except\s+.*\s*:",  # except statements
            r"print\s*\(.*\)",  # print statements
            r"\w+\s*=\s*.*"  # variable assignments
        ],
        'javascript': [
            r"function\s+\w+\s*\(.*\)\s*{",  # function definitions
            r"var\s+\w+\s*=\s*.*;",  # variable declarations
            r"let\s+\w+\s*=\s*.*;",  # variable declarations
            r"const\s+\w+\s*=\s*.*;",  # constant declarations
            r"if\s*\(.*\)\s*{",  # if statements
            r"for\s*\(.*\)\s*{",  # for loops
            r"while\s*\(.*\)\s*{",  # while loops
            r"console\.log\s*\(.*\);",  # console.log statements
            r"require\s*\(.*\);",  # require statements
            r"import\s+.*\s+from\s+.*;",  # import statements
            r"export\s+.*\s*{",  # export statements
        ],
        'java': [
            r"public\s+class\s+\w+\s*{",  # class definitions
            r"public\s+static\s+void\s+main\s*\(.*\)\s*{",  # main method
            r"import\s+.*;",  # import statements
            r"if\s*\(.*\)\s*{",  # if statements
            r"for\s*\(.*\)\s*{",  # for loops
            r"while\s*\(.*\)\s*{",  # while loops
            r"try\s*{",  # try blocks
            r"catch\s*\(.*\)\s*{",  # catch blocks
            r"System\.out\.println\s*\(.*\);",  # print statements
            r"\w+\s+\w+\s*=\s*.*;"  # variable declarations
        ]
    }
    
    for language, lang_patterns in patterns.items():
        for pattern in lang_patterns:
            if re.search(pattern, text):
                return True
    return False

################################################
# FUNCTION: do_FREQUENCY_WORD
################################################

META_FREQUENCY_WORD = [
    'Ensure {meta_seg} in the response.',
    'Make sure {meta_seg} in the response.',
    'Guarantee {meta_seg} in the response.',
    'Be certain {meta_seg} within the response.',
    'Make certain that the response encompasses {meta_seg}.'
]

META_SEG_FREQUENCY_WORD_EQUAL = [
    'the word "{word}" appears {count} times',
    'the term "{word}" is mentioned {count} times',
    'the word "{word}" shows up {count} times',
    'the phrase "{word}" is used {count} times',
    'the word "{word}" appears a total of {count} times',
    'the entry "{word}" is counted {count} times',
    'the occurrence count of the word"{word}" is {count}',
    'the word "{word}" can be found {count} times',
    'the usage of the word "{word}" is {count} times',
]

META_SEG_FREQUENCY_WORD_LESS = [
    'the word "{word}" appears at most {count} times',
    'the word "{word}" is repeated at most {count} times',
    'the occurrence of "{word}" is at most {count} times',
    'the word "{word}" shows up at most {count} times',
    'the occurrences of the word "{word}" amount to at most {count} times',
    'the word "{word}" appears up to {count} times'
    'the maximum occurrence of the word "{word}" is {count} times'
    'the maximum number of appearances for the word "{word}" is {count}'
    'the use of the word "{word}" does not go beyond {count} times',
    'the frequency of the word "{word}" does not exceed {count} instances'
]

META_SEG_FREQUENCY_WORD_MORE = [
    'the word "{word}" appears at least {count} times',
    'the word "{word}" shows up at least {count} times',
    'the word "{word}" is used at least {count} times',
    'the occurrence of the word "{word}" is at least {count} times',
    'the word "{word}" appears a minimum of {count} times',
    'there are at least {count} appearances of the word "{word}"',
    'the word "{word}" occurs at a minimum {count} times',
    'the word "{word}" occurs no less than {count} times',
    'at least {count} mentions of the word "{word}" are present'
]

META_SEG_FREQUENCY_WORD_INCLUDE = [
    'the word "{word}" appears',
    'the word "{word}" is present',
    'the word "{word}" shows up',
    'the word "{word}" can be found appearing',
    'the appearance of the word "{word}" is observed',
    'the word "{word}" makes an appearance',
    'the word "{word}" is observed to appear',
    'the word "{word}" is detected',
    'the word "{word}" is identified'
]

def do_FREQUENCY_WORD(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    indicator_word_version = random.choice([1 ,2])
    indicator_count_version = random.choice(['EQUAL', 'LESS', 'MORE', 'INCLUDE'])

    stastics_dict = get_response_stastics(response)
    merged_dict = {**stastics_dict['adj_dict'], **stastics_dict['noun_dict'], **stastics_dict['verb_dict']}

    if indicator_word_version == 2:
        # Version 2: Choose the words that appear in the instruction
        stastics_dict_ins = get_response_stastics(instruction)
        merged_dict_ins = {**stastics_dict_ins['adj_dict'], **stastics_dict_ins['noun_dict'], **stastics_dict_ins['verb_dict']}
        overlapping_keys = {key for key in merged_dict_ins if key in merged_dict}

        if len(overlapping_keys) > 0:
            num_word = random.randint(1, min(MAX_COUNT,len(overlapping_keys)))
            sampled_keys = random.sample(overlapping_keys, num_word)
            sampled_pairs = [(key, merged_dict[key]) for key in sampled_keys]
        else:
            # Back to Version 1
            indicator_word_version = 1

    if indicator_word_version == 1:
        # Version 1: Randomly decide the number of words and the specific words
        pos_count = len(merged_dict.items())

        if pos_count == 0:
            return {'instruction': instruction, 'output': response, 'type': 'None'}

        num_word = random.randint(1, min(MAX_COUNT,pos_count))
        sampled_pairs = random.sample(merged_dict.items(), num_word)


    instruction_seg = ''
    if indicator_count_version == 'EQUAL':
        indicator_meta_seg = random.randint(0, len(META_SEG_FREQUENCY_WORD_EQUAL)-1)
        for word, count in sampled_pairs:
            instruction_seg += (META_SEG_FREQUENCY_WORD_EQUAL[indicator_meta_seg].format(word=word, count=count) + ', ')
    if indicator_count_version == 'INCLUDE':
        indicator_meta_seg = random.randint(0, len(META_SEG_FREQUENCY_WORD_INCLUDE)-1)
        for word, count in sampled_pairs:
            instruction_seg += (META_SEG_FREQUENCY_WORD_INCLUDE[indicator_meta_seg].format(word=word, count=count) + ', ')
    elif indicator_count_version == 'LESS':
        random_gap = random.randint(1, 3)
        indicator_meta_seg = random.randint(0, len(META_SEG_FREQUENCY_WORD_LESS)-1)
        for word, count in sampled_pairs:
            count += random_gap
            instruction_seg += (META_SEG_FREQUENCY_WORD_LESS[indicator_meta_seg].format(word=word, count=count) + ', ')
    elif indicator_count_version == 'MORE':
        random_gap = random.randint(1, 3)
        indicator_meta_seg = random.randint(0, len(META_SEG_FREQUENCY_WORD_MORE)-1)
        for word, count in sampled_pairs:
            count = count if count - random_gap < 1 else count - random_gap
            instruction_seg += (META_SEG_FREQUENCY_WORD_MORE[indicator_meta_seg].format(word=word, count=count) + ', ')


    indicator_meta = random.randint(0, len(META_FREQUENCY_WORD)-1)
    instruction_meta = META_FREQUENCY_WORD[indicator_meta].format(meta_seg=instruction_seg[:-2])

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'FREQUENCY_WORD'}


################################################
# FUNCTION: do_FREQUENCY_TYPE
################################################

META_FREQUENCY_TYPE_EQUAL = [
    'Ensure there are {count} {type} in the response.',
    'Make sure the response includes {count} {type}.',
    'The response should contain {count} {type}.',
    'Make certain that {count} {type} are in the response.',
    'Ensure the response comprises {count} {type}.',
    'Guarantee that there are {count} {type} in the response.',
    'Check that the response includes {count} {type}.',
    'Make sure there are {count} {type} within the response.',
    'Ensure {count} {type} appear in the response.',
    'Confirm that the response contains {count} {type}.'
]

META_FREQUENCY_TYPE_LESS = [
    'Ensure there are less than {count} {type} in the response.',
    'Confirm that there are less than {count} {type} present in the response.',
    'Check that the response includes fewer than {count} {type}.',
    'Make sure the response has under {count} {type}.',
    'Ascertain that there are fewer than {count} {type} in the response.',
    'Guarantee that the count of {type} in the response is less than {count}.',
    'Make sure there are less than {count} {type} in the response.',
    'Ensure the response holds less than {count} {type}.'
]

META_FREQUENCY_TYPE_MORE = [
    'Ensure there are more than {count} {type} in the response.',
    'Verify that the response contains more than {count} {type}.',
    'Confirm that there are at least {count} {type} in the response.',
    'Ensure the response has a minimum of {count} {type}.',
    'Check that the response includes more than {count} {type}.',
    'Guarantee there are above {count} {type} in the response.',
    'Make certain the response contains at least {count} {type}.',
    'Be sure the response exceeds {count} {type}.',
    'Confirm there are at least {count} {type} within the response.',
    'Validate that the response has more than {count} {type}.'
]

def count_non_whitespace_characters(text):
    # Use a generator expression to count non-whitespace characters
    return sum(1 for char in text if not char.isspace())

def count_letters(text):
    # Create a Counter object from the text
    counter = Counter(text)
    
    # Sum the counts of alphabetic characters only
    letter_count = sum(counter[char] for char in string.ascii_letters)
    
    return letter_count

def do_FREQUENCY_TYPE(data_item, given_type):

    instruction = data_item['instruction']
    response = data_item['output']

    indicator_count_version = random.choice(['EQUAL', 'LESS', 'MORE'])

    stastics_dict = get_response_stastics(response)
    adj_count = len(stastics_dict['adj_dict'])
    noun_count = len(stastics_dict['noun_dict'])
    verb_count = len(stastics_dict['verb_dict'])

    if given_type == 'ADJ':
        count = adj_count
        type_name = 'adjectives'
    elif given_type == 'NOUN':
        count = noun_count
        type_name = 'nouns'
    elif given_type == 'VERB':
        count = verb_count
        type_name = 'verbs'
    elif given_type == 'LETTER':
        count = count_letters(response)
        type_name = 'letters'
    elif given_type == 'CHAR':
        count = count_non_whitespace_characters(response)
        type_name = 'non-whitespace characters'

    if indicator_count_version == 'EQUAL':
        indicator_meta = random.randint(0, len(META_FREQUENCY_TYPE_EQUAL)-1)
        instruction_meta = META_FREQUENCY_TYPE_EQUAL[indicator_meta].format(count=count, type=type_name)
    elif indicator_count_version == 'LESS':
        random_gap = random.randint(0, int(count*0.5))
        indicator_meta = random.randint(0, len(META_FREQUENCY_TYPE_LESS)-1)
        instruction_meta = META_FREQUENCY_TYPE_LESS[indicator_meta].format(count=count + random_gap, type=type_name)
    elif indicator_count_version == 'MORE':
        random_gap = random.randint(0, int(count*0.5))
        indicator_meta = random.randint(0, len(META_FREQUENCY_TYPE_MORE)-1)
        instruction_meta = META_FREQUENCY_TYPE_MORE[indicator_meta].format(count=count - random_gap, type=type_name)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'FREQUENCY_' + given_type}

def do_FREQUENCY_ADJ(data_item):
    return do_FREQUENCY_TYPE(data_item, 'ADJ')

def do_FREQUENCY_NOUN(data_item):
    return do_FREQUENCY_TYPE(data_item, 'NOUN')

def do_FREQUENCY_VERB(data_item):
    return do_FREQUENCY_TYPE(data_item, 'VERB')

def do_FREQUENCY_LETTER(data_item):
    return do_FREQUENCY_TYPE(data_item, 'LETTER')

def do_FREQUENCY_CHAR(data_item):
    return do_FREQUENCY_TYPE(data_item, 'CHAR')

################################################
# FUNCTION: do_NUM_WORD
################################################

META_NUM_WORD = [
    'Ensure the response {meta_seg}.',
    'Make sure the response {meta_seg}.',
    'Confirm the response {meta_seg}.',
    'Guarantee the response {meta_seg}.',
    'Ascertain that the response {meta_seg}.',
    'Make certain the response {meta_seg}.',
    'Be sure the response {meta_seg}.',
    'Confirm there is a response {meta_seg}.',
    'Check to ensure the response {meta_seg}.'
]

META_SEG_NUM_WORD_EQUAL = [
    'has exactly {count} words',
    'contains exactly {count} words',
    'includes exactly {count} words',
    'comprises exactly {count} words',
    'has precisely {count} words',
    'holds exactly {count} words',
    'encompasses exactly {count} words',
    'possesses exactly {count} words',
    'amounts to exactly {count} words',
    'reaches exactly {count} words'
]

META_SEG_NUM_WORD_LESS = [
    'has less than {count} words',
    'contains fewer than {count} words',
    'includes less than {count} words',
    'has a word count below {count}',
    'uses less than {count} words',
    'keeps the word count under {count}',
    'remains below {count} words',
    'limits to fewer than {count} words',
    'comprises fewer than {count} words',
    'falls short of {count} words'
]

META_SEG_NUM_WORD_MORE = [
    'has more than {count} words',
    'includes over {count} words',
    'exceeds {count} words',
    'has a word count above {count}',
    'uses more than {count} words',
    'surpasses {count} words',
    'consists of more than {count} words',
    'comprises more than {count} words',
    'has over {count} words',
    'contains a word count exceeding {count}'
]

def do_NUM_WORD(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    indicator_count_version = random.choice(['EQUAL', 'LESS', 'MORE'])

    word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(response)

    instruction_seg = ''
    if indicator_count_version == 'EQUAL':
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_WORD_EQUAL)-1)
        instruction_seg = META_SEG_NUM_WORD_EQUAL[indicator_meta_seg].format(count=word_count)

    elif indicator_count_version == 'LESS':
        random_gap = random.randint(0, int(word_count*0.5))
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_WORD_LESS)-1)
        instruction_seg = META_SEG_NUM_WORD_LESS[indicator_meta_seg].format(count=word_count + random_gap)

    elif indicator_count_version == 'MORE':
        random_gap = random.randint(0, int(word_count*0.5))
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_WORD_MORE)-1)
        instruction_seg = META_SEG_NUM_WORD_MORE[indicator_meta_seg].format(count=word_count - random_gap)


    indicator_meta = random.randint(0, len(META_NUM_WORD)-1)
    instruction_meta = META_NUM_WORD[indicator_meta].format(meta_seg=instruction_seg)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'NUM_WORD'}


################################################
# FUNCTION: do_NUM_SENTENCE
################################################

META_NUM_SENTENCE = [
    'Ensure the response {meta_seg}.',
    'Make sure the response {meta_seg}.',
    'Confirm the response {meta_seg}.',
    'Guarantee the response {meta_seg}.',
    'Ascertain that the response {meta_seg}.',
    'Make certain the response {meta_seg}.',
    'Be sure the response {meta_seg}.',
    'Confirm there is a response {meta_seg}.',
    'Check to ensure the response {meta_seg}.'
]

META_SEG_NUM_SENTENCE_EQUAL = [
    'has exactly {count} sentences',
    'contains exactly {count} sentences',
    'includes exactly {count} sentences',
    'has precisely {count} sentences',
    'consists of exactly {count} sentences',
    'comprises exactly {count} sentences',
    'holds exactly {count} sentences',
    'encompasses exactly {count} sentences',
]

META_SEG_NUM_SENTENCE_LESS = [
    'has less than {count} sentences',
    'contains fewer than {count} sentences'
    'includes less than {count} sentences'
    'has fewer than {count} sentences'
    'keeps the sentence count under {count}'
    'remains below {count} sentences'
    'comprises fewer than {count} sentences'
    'falls short of {count} sentences'
    'limits to fewer than {count} sentences'
    'holds less than {count} sentences'
]

META_SEG_NUM_SENTENCE_MORE = [
    'has more than {count} sentences',
    'contains more than {count} sentences'
    'exceeds {count} sentences'
    'has a sentence count above {count}'
    'surpasses {count} sentences'
    'consists of more than {count} sentences'
    'comprises more than {count} sentences'
    'has over {count} sentences'
    'contains a sentence count exceeding {count}'
    'exceeds a count of {count} sentences'
]

def do_NUM_SENTENCE(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    indicator_count_version = random.choice(['EQUAL', 'LESS', 'MORE'])

    word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(response)

    instruction_seg = ''
    if indicator_count_version == 'EQUAL':
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_SENTENCE_EQUAL)-1)
        instruction_seg = META_SEG_NUM_SENTENCE_EQUAL[indicator_meta_seg].format(count=sentence_count)

    elif indicator_count_version == 'LESS':
        random_gap = random.randint(0, 3)
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_SENTENCE_LESS)-1)
        instruction_seg = META_SEG_NUM_SENTENCE_LESS[indicator_meta_seg].format(count=sentence_count + random_gap)

    elif indicator_count_version == 'MORE':
        random_gap = random.randint(0, 3)
        random_gap = random_gap if sentence_count - random_gap > 0 else 0
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_SENTENCE_MORE)-1)
        instruction_seg = META_SEG_NUM_SENTENCE_MORE[indicator_meta_seg].format(count=sentence_count - random_gap)


    indicator_meta = random.randint(0, len(META_NUM_SENTENCE)-1)
    instruction_meta = META_NUM_SENTENCE[indicator_meta].format(meta_seg=instruction_seg)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'NUM_SENTENCE'}

################################################
# FUNCTION: do_NUM_PARAGRAPH
################################################

META_NUM_PARAGRAPH = [
    'Ensure the response {meta_seg}.',
    'Make sure the response {meta_seg}.',
    'Confirm the response {meta_seg}.',
    'Guarantee the response {meta_seg}.',
    'Ascertain that the response {meta_seg}.',
    'Make certain the response {meta_seg}.',
    'Be sure the response {meta_seg}.',
    'Confirm there is a response {meta_seg}.',
    'Check to ensure the response {meta_seg}.'
]

META_SEG_NUM_PARAGRAPH_EQUAL = [
    'has exactly {count} paragraphs',
    'has precisely {count} paragraphs',
    'consists of exactly {count} paragraphs',
    'comprises exactly {count} paragraphs',
    'encompasses exactly {count} paragraphs',
    'holds exactly {count} paragraphs',
    'reaches exactly {count} paragraphs',
]

META_SEG_NUM_PARAGRAPH_LESS = [
    'has less than {count} paragraphs',
    'contains fewer than {count} paragraphs',
    'includes less than {count} paragraphs',
    'has fewer than {count} paragraphs',
    'remains below {count} paragraphs',
    'comprises fewer than {count} paragraphs',
    'falls short of {count} paragraphs',
    'contains a paragraph count below {count}',
    'holds less than {count} paragraphs'
]

META_SEG_NUM_PARAGRAPH_MORE = [
    'has more than {count} paragraphs',
    'includes over {count} paragraphs',
    'exceeds {count} paragraphs',
    'has a paragraph count above {count}',
    'uses more than {count} paragraphs',
    'surpasses {count} paragraphs',
    'consists of more than {count} paragraphs',
    'comprises more than {count} paragraphs',
    'contains a paragraph count exceeding {count}',
    'exceeds a count of {count} paragraphs'
]

def do_NUM_PARAGRAPH(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    indicator_count_version = random.choice(['EQUAL', 'LESS', 'MORE'])

    word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(response)

    instruction_seg = ''
    if indicator_count_version == 'EQUAL':
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_PARAGRAPH_EQUAL)-1)
        instruction_seg = META_SEG_NUM_PARAGRAPH_EQUAL[indicator_meta_seg].format(count=paragraph_count)

    elif indicator_count_version == 'LESS':
        random_gap = random.randint(0, 3)
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_PARAGRAPH_LESS)-1)
        instruction_seg = META_SEG_NUM_PARAGRAPH_LESS[indicator_meta_seg].format(count=paragraph_count + random_gap)

    elif indicator_count_version == 'MORE':
        random_gap = random.randint(0, 3)
        random_gap = random_gap if paragraph_count - random_gap > 0 else 0
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_PARAGRAPH_MORE)-1)
        instruction_seg = META_SEG_NUM_PARAGRAPH_MORE[indicator_meta_seg].format(count=paragraph_count - random_gap)


    indicator_meta = random.randint(0, len(META_NUM_PARAGRAPH)-1)
    instruction_meta = META_NUM_PARAGRAPH[indicator_meta].format(meta_seg=instruction_seg)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'NUM_PARAGRAPH'}

################################################
# FUNCTION: do_NUM_BULLET
################################################

META_NUM_BULLET = [
    'Ensure the response {meta_seg}.',
    'Make sure the response {meta_seg}.',
    'Confirm the response {meta_seg}.',
    'Guarantee the response {meta_seg}.',
    'Ascertain that the response {meta_seg}.',
    'Make certain the response {meta_seg}.',
    'Be sure the response {meta_seg}.',
    'Confirm there is a response {meta_seg}.',
    'Check to ensure the response {meta_seg}.'
]

META_SEG_NUM_BULLET_EQUAL = [
    'has exactly {count} bullet points',
    'contains exactly {count} bullet points',
    'includes exactly {count} bullet points',
    'comprises exactly {count} bullet points',
    'consists of exactly {count} bullet points',
    'encompasses exactly {count} bullet points',
    'holds exactly {count} bullet points',
    'numbers exactly {count} bullet points',
]

META_SEG_NUM_BULLET_LESS = [
    'has less than {count} bullet points',
    'exceeds no more than {count} bullet points',
    'keeps the bullet point count under {count}',
    'remains below {count} bullet points',
    'restricts to less than {count} bullet points',
    'comprises fewer than {count} bullet points',
    'falls short of {count} bullet points',
    'limits to fewer than {count} bullet points',
    'holds less than {count} bullet points',
    'numbers fewer than {count} bullet points'
]

META_SEG_NUM_BULLET_MORE = [
    'has more than {count} bullet points',
    'exceeds {count} bullet points',
    'has a bullet point count above {count}',
    'uses more than {count} bullet points',
    'surpasses {count} bullet points',
    'consists of more than {count} bullet points',
    'comprises more than {count} bullet points',
    'remains over {count} bullet points',
    'contains a bullet point count exceeding {count}',
    'exceeds a count of {count} bullet points'
]


def do_NUM_BULLET(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    indicator_count_version = random.choice(['EQUAL', 'LESS', 'MORE'])

    word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(response)

    if bullet_point_count == 0:
        return {'instruction': instruction, 'output': response, 'type': 'None'}
    
    instruction_seg = ''
    if indicator_count_version == 'EQUAL':
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_BULLET_EQUAL)-1)
        instruction_seg = META_SEG_NUM_BULLET_EQUAL[indicator_meta_seg].format(count=bullet_point_count)

    elif indicator_count_version == 'LESS':
        random_gap = random.randint(0, 3)
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_BULLET_LESS)-1)
        instruction_seg = META_SEG_NUM_BULLET_LESS[indicator_meta_seg].format(count=bullet_point_count + random_gap)

    elif indicator_count_version == 'MORE':
        random_gap = random.randint(0, 3)
        random_gap = random_gap if bullet_point_count - random_gap > 0 else 0
        indicator_meta_seg = random.randint(0, len(META_SEG_NUM_BULLET_MORE)-1)
        instruction_seg = META_SEG_NUM_BULLET_MORE[indicator_meta_seg].format(count=bullet_point_count - random_gap)


    indicator_meta = random.randint(0, len(META_NUM_BULLET)-1)
    instruction_meta = META_NUM_BULLET[indicator_meta].format(meta_seg=instruction_seg)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'NUM_BULLET'}

################################################
# FUNCTION: do_REPEAT_INSTRUCTION
################################################

META_REPEAT_INSTRUCTION = [
    'First repeat the instruction, then provide the response.',
    'Begin by restating the instruction, then give your response.',
    'Start by repeating the instruction, followed by your response.',
    'Restate the instruction first, then proceed with your response.',
    'Initially repeat the instruction, then offer your response.',
    'Commence with repeating the instruction, then respond.',
    'Reiterate the instruction at the start, then provide the response.',
    'Echo the instruction first, then deliver your response.',
    'Repeat the instruction initially, then give your answer.',
    'Start with repeating the instruction, then follow up with your response.'
]

def do_REPEAT_INSTRUCTION(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    response = instruction + '\n\n' + response

    indicator_meta = random.randint(0, len(META_REPEAT_INSTRUCTION)-1)
    instruction_meta = META_REPEAT_INSTRUCTION[indicator_meta]

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'REPEAT_INSTRUCTION'}


################################################
# FUNCTION: do_REPEAT_RESPONSE
################################################

META_REPEAT_RESPONSE = [
    'Repeat the same response {i} times.',
    'Provide the same response {i} times.',
    'Give the identical response {i} times.',
    'Repeat the response {i} times.',
    'Restate the response {i} times.',
    'Reiterate the response {i} times.',
    'Produce the same response {i} times.',
    'Repeat the identical response {i} times.',
    'Respond with the same answer {i} times.'
]

def do_REPEAT_RESPONSE(data_item):

    instruction = data_item['instruction']
    response = data_item['output']
    
    repeat_times = random.randint(2, 5)
    response = (response + '\n\n') * repeat_times
    response = response[:-2]

    indicator_meta = random.randint(0, len(META_REPEAT_RESPONSE)-1)
    instruction_meta = META_REPEAT_RESPONSE[indicator_meta].format(i=repeat_times)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'REPEAT_RESPONSE'}


################################################
# FUNCTION: do_CASE_LOW
################################################

META_CASE_LOW = [
    'Ensure the response is in lowercase.',
    'Confirm the response is in lowercase.',
    'Guarantee the response is in lowercase.',
    'Verify that the response is in lowercase.',
    'Make certain the response is in lowercase.',
    'Assure that the response is in lowercase.',
    'Check to ensure the response is in lowercase.',
    'Make sure the response is in lowercase.',
]

def do_CASE_LOW(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    response = response.lower()

    indicator_meta = random.randint(0, len(META_CASE_LOW)-1)
    instruction_meta = META_CASE_LOW[indicator_meta]

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'CASE_LOW'}


################################################
# FUNCTION: do_CASE_UP
################################################

META_CASE_UP = [
    'Ensure the response is in uppercase.',
    'Make sure the response is in uppercase.',
    'Confirm the response is in uppercase.',
    'Guarantee the response is in uppercase.',
    'Verify that the response is in uppercase.',
    'Make certain the response is in uppercase.',
    'See to it that the response is in uppercase.',
    'Assure that the response is in uppercase.',]

def do_CASE_UP(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    response = response.upper()

    indicator_meta = random.randint(0, len(META_CASE_UP)-1)
    instruction_meta = META_CASE_UP[indicator_meta]

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'CASE_UP'}


################################################
# FUNCTION: do_CASE_UP_LETTER
################################################

META_CASE_UP_LETTER = [
    'Ensure all the letters "{letter}" in the response is in uppercase.',
]

def do_CASE_UP_LETTER(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    random_letter = random.choice(string.ascii_lowercase)

    response = response.replace(random_letter, random_letter.upper())

    indicator_meta = random.randint(0, len(META_CASE_UP_LETTER)-1)
    instruction_meta = META_CASE_UP_LETTER[indicator_meta].format(letter=random_letter)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'CASE_UP_LETTER'}

################################################
# FUNCTION: do_CASE_UP_WORD
################################################

META_CASE_UP_WORD = [
    'Ensure {meta_seg} in the response if they appear.',
    'Include {meta_seg} in the response if they appear.',
    'Make sure {meta_seg} in the response if they show up.',
    'Guarantee {meta_seg} in the response if they exist.',
    'Make certain {meta_seg} if they are there.',
    'Keep {meta_seg} in the response if they appear.',
    'Verify {meta_seg} if they show up.',
    'Ensure that {meta_seg} in the response if they appear.',
    'Include {meta_seg} if they are in the response.'
]

META_SEG_CASE_UP_WORD = [
    'the word "{word}" is in uppercase',
]

def do_CASE_UP_WORD(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    indicator_word_version = random.choice([1 ,2])

    stastics_dict = get_response_stastics(response)
    merged_dict = {**stastics_dict['adj_dict'], **stastics_dict['noun_dict'], **stastics_dict['verb_dict']}

    if indicator_word_version == 2:
        # Version 2: Choose the words that appear in the instruction
        stastics_dict_ins = get_response_stastics(instruction)
        merged_dict_ins = {**stastics_dict_ins['adj_dict'], **stastics_dict_ins['noun_dict'], **stastics_dict_ins['verb_dict']}
        overlapping_keys = {key for key in merged_dict_ins if key in merged_dict}

        if len(overlapping_keys) > 0:
            num_word = random.randint(1, min(MAX_COUNT,len(overlapping_keys)))
            sampled_keys = random.sample(overlapping_keys, num_word)
            sampled_pairs = [(key, merged_dict[key]) for key in sampled_keys]
        else:
            # Back to Version 1
            indicator_word_version = 1

    if indicator_word_version == 1:
        # Version 1: Randomly decide the number of words and the specific words
        pos_count = len(merged_dict.items())

        if pos_count == 0:
            return {'instruction': instruction, 'output': response, 'type': 'None'}

        num_word = random.randint(1, min(MAX_COUNT,pos_count))
        sampled_pairs = random.sample(merged_dict.items(), num_word)

    instruction_seg = ''
    indicator_meta_seg = random.randint(0, len(META_SEG_CASE_UP_WORD)-1)
    for word, count in sampled_pairs:
        response = response.replace(word, word.upper())

        instruction_seg += META_SEG_CASE_UP_WORD[indicator_meta_seg].format(word=word) + ', '

    indicator_meta = random.randint(0, len(META_CASE_UP_WORD)-1)
    instruction_meta = META_CASE_UP_WORD[indicator_meta].format(meta_seg=instruction_seg[:-2])

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'CASE_UP_WORD'}


################################################
# FUNCTION: do_CASE_UP_SENTENCE
################################################

META_CASE_UP_SENTENCE = [
    'Ensure {meta_seg} in the response.',
    'Make sure {meta_seg} in the response.',
    'Ensure {meta_seg} in the response',
    'Guarantee {meta_seg} in the response.',
    'Ascertain {meta_seg}.',
    'Keep {meta_seg}in the response.',
    'Be certain {meta_seg} within the response.',
    'Make certain that {meta_seg} in the response.'
]

META_SEG_CASE_UP_SENTENCE = [
    'the {which} sentence is in uppercase',
]


def do_CASE_UP_SENTENCE(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(response)

    sample_count = min(MAX_COUNT, int(sentence_count*0.5))
    sampled_idx = random.sample(range(sentence_count), sample_count)
    sampled_idx = sorted(sampled_idx)

    instruction_seg = ''
    indicator_meta_seg = random.randint(0, len(META_SEG_CASE_UP_SENTENCE)-1)
    for idx in sampled_idx:
        if idx >= len(FORMAT_ORDER_LIST):
            which = str(idx+1) + 'th'
        else:
            which = FORMAT_ORDER_LIST[idx]
        instruction_seg += META_SEG_CASE_UP_SENTENCE[indicator_meta_seg].format(which=which) + ', '

    doc = nlp(response)
    for i, sent in enumerate(doc.sents):
        sentence_text = sent.text.strip()
        if i in sampled_idx:
            response = response.replace(sentence_text, sentence_text.upper())

    indicator_meta = random.randint(0, len(META_CASE_UP_SENTENCE)-1)
    instruction_meta = META_CASE_UP_SENTENCE[indicator_meta].format(meta_seg=instruction_seg[:-2])

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'CASE_UP_SENTENCE'}


################################################
# FUNCTION: do_CASE_UP_PARAGRAPH
################################################

META_CASE_UP_PARAGRAPH = [
    'Ensure {meta_seg} in the response.',
    'Make sure {meta_seg} in the response.',
    'Ensure {meta_seg} in the response',
    'Guarantee {meta_seg} in the response.',
    'Ascertain {meta_seg}.',
    'Keep {meta_seg}in the response.',
    'Be certain {meta_seg} within the response.',
    'Make certain that {meta_seg} in the response.'
]

META_SEG_CASE_UP_PARAGRAPH = [
    'the {which} paragraph is in uppercase',
]

def do_CASE_UP_PARAGRAPH(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(response)

    sample_count_min = 1 if int(paragraph_count*0.5) == 0 else int(paragraph_count*0.5)
    sample_count = min(MAX_COUNT, sample_count_min)
    sampled_idx = random.sample(range(paragraph_count), sample_count)
    sampled_idx = sorted(sampled_idx)

    instruction_seg = ''
    indicator_meta_seg = random.randint(0, len(META_SEG_CASE_UP_PARAGRAPH)-1)
    for idx in sampled_idx:
        if idx >= len(FORMAT_ORDER_LIST):
            which = str(idx+1) + 'th'
        else:
            which = FORMAT_ORDER_LIST[idx]
        instruction_seg += META_SEG_CASE_UP_PARAGRAPH[indicator_meta_seg].format(which=which) + ', '


    paragraphs = re.split(r'\n\s*\n', response.strip())
    for i, paragraph in enumerate(paragraphs):
        trimmed_paragraph = paragraph.strip()
        if i in sampled_idx:
            response = response.replace(trimmed_paragraph, trimmed_paragraph.upper())

    indicator_meta = random.randint(0, len(META_CASE_UP_PARAGRAPH)-1)
    instruction_meta = META_CASE_UP_PARAGRAPH[indicator_meta].format(meta_seg=instruction_seg[:-2])

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'CASE_UP_PARAGRAPH'}


################################################
# FUNCTION: do_PUNCTUATION_REPLACEMENT
################################################

META_PUNCTUATION_REPLACEMENT = [
    'In the respose, use "{punct_new}" to replace "{punct_ori}".',
    'In the response, change "{punct_ori}" to "{punct_new}".',
    'Replace "{punct_ori}" in the response with "{punct_new}".',
    'Switch "{punct_ori}" with "{punct_new}" in the response.',
    'In the response, use "{punct_new}" instead of "{punct_ori}".',
    'In the response, swap "{punct_ori}" for "{punct_new}".',
    'Exchange "{punct_ori}" for "{punct_new}" in the response.',
    'In the response, update "{punct_ori}" to "{punct_new}".',
    'In the response, convert "{punct_ori}" to "{punct_new}".',
    'In the response, alter "{punct_ori}" to "{punct_new}".'
]

META_PUNCTUATION_REPLACEMENT_ALL = [
    'In the respose, use "{punct_new}" to replace all the punctuations.',
    'Replace every punctuation in the response with "{punct_new}".',
    'In the response, substitute all punctuation marks with "{punct_new}".',
    'In the response, convert every punctuation mark to "{punct_new}".',
    'Replace each punctuation in the response with "{punct_new}".',
    'Update all punctuation in the response to "{punct_new}".',
    'In the response, exchange every punctuation for "{punct_new}".',
    'In the response, change every punctuation symbol to "{punct_new}".',
    'Alter all punctuation in the response to "{punct_new}".',
    'In the response, switch all punctuation marks to "{punct_new}".'
]

def do_PUNCTUATION_REPLACEMENT(data_item):

    instruction = data_item['instruction']
    response = data_item['output']
    
    punct_ori = random.choice(PUNCT_TO_REPLACE)
    punct_new = random.choice(PUNCT_REPLACE_WITH)

    if punct_ori == 'ALL':
        translation_table = str.maketrans(string.punctuation, punct_new * len(string.punctuation))
        response = response.translate(translation_table)
        indicator_meta = random.randint(0, len(META_PUNCTUATION_REPLACEMENT_ALL)-1)
        instruction_meta = META_PUNCTUATION_REPLACEMENT_ALL[indicator_meta].format(punct_new=punct_new)
    else:
        punct_form = random.choice([0, 1])
        punct_ori = punct_ori[punct_form]

        response = response.replace(punct_ori, punct_new)
        indicator_meta = random.randint(0, len(META_PUNCTUATION_REPLACEMENT)-1)
        instruction_meta = META_PUNCTUATION_REPLACEMENT[indicator_meta].format(punct_new=punct_new, punct_ori=punct_ori)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'PUNCTUATION_REPLACEMENT'}


################################################
# FUNCTION: do_PUNCTUATION_IGNORANCE
################################################

META_PUNCTUATION_IGNORANCE = [
    'In the respose, ignore all the "{punct_ori}".',
    'In the response, omit all occurrences of "{punct_ori}".',
    'In the response, disregard all "{punct_ori}" marks.',
    'Exclude all "{punct_ori}" from the response.',
    'Ignore each "{punct_ori}" in the response.',
    'In the response, leave out all "{punct_ori}".',
    'In the response, skip over all "{punct_ori}".',
    'In the response, remove all "{punct_ori}" symbols.',
    'Exclude each "{punct_ori}" mark from the response.',
    'In the response, eliminate all "{punct_ori}".'
]

META_PUNCTUATION_IGNORANCE_ALL = [
    'In the respose, ignore all the punctuations.',
    'In the response, omit all punctuation marks.',
    'In the response, disregard all punctuation.',
    'In the response, leave out all punctuation.',
    'Eliminate every punctuation mark in the response.',
    'In the response, skip over all punctuation marks.',
    'In the response, remove all punctuation symbols.',
    'Disregard each instance of punctuation in the response.',
    'Exclude each punctuation mark from the response.',
    'In the response, eliminate all punctuation.'
]

def do_PUNCTUATION_IGNORANCE(data_item):
    

    instruction = data_item['instruction']
    response = data_item['output']

    punct_ori = random.choice(PUNCT_TO_REPLACE)

    if punct_ori == 'ALL':
        response = response.translate(str.maketrans('', '', string.punctuation))
        indicator_meta = random.randint(0, len(META_PUNCTUATION_IGNORANCE_ALL)-1)
        instruction_meta = META_PUNCTUATION_IGNORANCE_ALL[indicator_meta]
    else:
        punct_form = random.choice([0, 1])
        punct_ori = punct_ori[punct_form]

        response = response.replace(punct_ori, '')
        indicator_meta = random.randint(0, len(META_PUNCTUATION_IGNORANCE)-1)
        instruction_meta = META_PUNCTUATION_IGNORANCE[indicator_meta].format(punct_ori=punct_ori)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'PUNCTUATION_IGNORANCE'}


################################################
# FUNCTION: do_FORMAT_WRAP_WORD
################################################

META_FORMAT_WRAP_WORD = [
    'Ensure {meta_seg} in the response if they appear.',
    'Include {meta_seg} in the response if they appear.',
    'Make sure {meta_seg} in the response if they show up.',
    'Guarantee {meta_seg} in the response if they exist.',
    'Make certain {meta_seg} if they are there.',
    'Keep {meta_seg} in the response if they appear.',
    'Verify {meta_seg} if they show up.',
    'Ensure that {meta_seg} in the response if they appear.',
    'Include {meta_seg} if they are in the response.'
]

META_SEG_FORMAT_WRAP_WORD = [
    'the word "{word}" is wrapped in "{format}"',
    'the word "{word}" is enclosed in "{format}"',
    'the word "{word}" is surrounded by "{format}"',
    'the word "{word}" is framed by "{format}"',
    'the word "{word}" is inside "{format}"',
    'the word "{word}" is encapsulated in "{format}"',
    'the word "{word}" is contained in "{format}"',
    'the word "{word}" is bounded by "{format}"',
    'the word "{word}" is enveloped in "{format}"',
    'the word "{word}" is wrapped inside "{format}"'
]

def get_lemmas_replace_dict(text, word_map):
    # Process the text with spacy
    doc = nlp(text)

    replace_dict = {}
    for token in doc:
        # Check if the lemma of the token is in the word_map
        if token.lemma_ in word_map:
            wrap_symbol = word_map[token.lemma_]
            replace_dict[token.text] = wrap_symbol.format(text=token.text)
    
    return replace_dict

def do_FORMAT_WRAP_WORD(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    indicator_word_version = random.choice([1 ,2])

    stastics_dict = get_response_stastics(response)
    merged_dict = {**stastics_dict['adj_dict'], **stastics_dict['noun_dict'], **stastics_dict['verb_dict']}

    if indicator_word_version == 2:
        # Version 2: Choose the words that appear in the instruction
        stastics_dict_ins = get_response_stastics(instruction)
        merged_dict_ins = {**stastics_dict_ins['adj_dict'], **stastics_dict_ins['noun_dict'], **stastics_dict_ins['verb_dict']}
        overlapping_keys = {key for key in merged_dict_ins if key in merged_dict}

        if len(overlapping_keys) > 0:
            num_word = random.randint(1, min(MAX_COUNT,len(overlapping_keys)))
            sampled_keys = random.sample(overlapping_keys, num_word)
            sampled_pairs = [(key, merged_dict[key]) for key in sampled_keys]
        else:
            # Back to Version 1
            indicator_word_version = 1

    if indicator_word_version == 1:
        # Version 1: Randomly decide the number of words and the specific words
        pos_count = len(merged_dict.items())

        if pos_count == 0:
            return {'instruction': instruction, 'output': response, 'type': 'None'}

        num_word = random.randint(1, min(MAX_COUNT,pos_count))
        sampled_pairs = random.sample(merged_dict.items(), num_word)

    instruction_seg = ''
    word_map = {}
    indicator_meta_seg = random.randint(0, len(META_SEG_FREQUENCY_WORD_EQUAL)-1)
    for word, count in sampled_pairs:
        indicator_bracket_format = random.randint(0, len(FORMAT_BRACKET_LIST)-1)
        bracket_format = FORMAT_BRACKET_LIST[indicator_bracket_format].format(text=' ')

        word_map[word] = FORMAT_BRACKET_LIST[indicator_bracket_format]
        instruction_seg += (META_SEG_FORMAT_WRAP_WORD[indicator_meta_seg].format(word=word, format=bracket_format) + ', ')
    
    replace_dict = get_lemmas_replace_dict(response, word_map)
    for key, value in replace_dict.items():
        response = response.replace(key, value)

    indicator_meta = random.randint(0, len(META_FORMAT_WRAP_WORD)-1)
    instruction_meta = META_FORMAT_WRAP_WORD[indicator_meta].format(meta_seg=instruction_seg[:-2])

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'FORMAT_WRAP_WORD'}


################################################
# FUNCTION: do_FORMAT_WRAP_SENTENCE
################################################

META_FORMAT_WRAP_SENTENCE = [
    'Ensure {meta_seg} in the response.',
    'Make sure {meta_seg} in the response.',
    'Ensure {meta_seg} in the response',
    'Guarantee {meta_seg} in the response.',
    'Ascertain {meta_seg}.',
    'Keep {meta_seg}in the response.',
    'Be certain {meta_seg} within the response.',
    'Make certain that {meta_seg} in the response.'
]

META_SEG_FORMAT_WRAP_SENTENCE = [
    'the {which} sentence is wrapped in "{format}"',
    'the {which} sentence is enclosed in "{format}"',
    'the {which} sentence is inside "{format}"',
    'the {which} sentence is encapsulated in "{format}"',
    'the {which} sentence is within "{format}"',
    'the {which} sentence is bordered by "{format}"',
    'the {which} sentence is wrapped within "{format}"',
    'the {which} sentence is contained in "{format}"',
    'the {which} sentence is enclosed within "{format}"',
    'the {which} sentence is enveloped in "{format}"'
]

def get_sentence_replace_dict(text, sentence_map):
    # Process the text with spacy
    doc = nlp(text)
    
    replace_dict = {}
    for i, sent in enumerate(doc.sents):
        sentence_text = sent.text.strip()
        if i in sentence_map.keys():
            wrap_symbol = sentence_map[i]
            replace_dict[sentence_text] = wrap_symbol.format(text=sentence_text)
    
    return replace_dict

def do_FORMAT_WRAP_SENTENCE(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(response)

    sample_count = min(MAX_COUNT, int(sentence_count*0.5))
    sampled_idx = random.sample(range(sentence_count), sample_count)
    sampled_idx = sorted(sampled_idx)

    instruction_seg = ''
    sentence_map = {}
    indicator_meta_seg = random.randint(0, len(META_SEG_FORMAT_WRAP_SENTENCE)-1)
    for idx in sampled_idx:
        indicator_bracket_format = random.randint(0, len(FORMAT_BRACKET_LIST)-1)
        bracket_format = FORMAT_BRACKET_LIST[indicator_bracket_format].format(text=' ')

        sentence_map[idx] = FORMAT_BRACKET_LIST[indicator_bracket_format]
        
        if idx >= len(FORMAT_ORDER_LIST):
            which = str(idx+1) + 'th'
        else:
            which = FORMAT_ORDER_LIST[idx]
        instruction_seg += (META_SEG_FORMAT_WRAP_SENTENCE[indicator_meta_seg].format(which=which, format=bracket_format) + ', ')

    replace_dict = get_sentence_replace_dict(response, sentence_map)
    for key, value in replace_dict.items():
        response = response.replace(key, value)
    
    indicator_meta = random.randint(0, len(META_FORMAT_WRAP_SENTENCE)-1)
    instruction_meta = META_FORMAT_WRAP_SENTENCE[indicator_meta].format(meta_seg=instruction_seg[:-2])

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'FORMAT_WRAP_SENTENCE'}


################################################
# FUNCTION: do_FORMAT_WRAP_BULLET
################################################

META_FORMAT_WRAP_BULLET = [
    'Ensure {meta_seg} in the response.',
    'Make sure {meta_seg} in the response.',
    'Ensure {meta_seg} in the response',
    'Guarantee {meta_seg} in the response.',
    'Ascertain {meta_seg}.',
    'Keep {meta_seg}in the response.',
    'Be certain {meta_seg} within the response.',
    'Make certain that {meta_seg} in the response.'
]

META_SEG_FORMAT_WRAP_BULLET = [
    'the {which} bullet point is wrapped in "{format}"',
    'the {which} bullet point is contained in "{format}"',
    'the {which} bullet point is surrounded by "{format}"',
    'the {which} bullet point is bordered by "{format}"',
    'the {which} bullet point is framed by "{format}"',
    'the {which} bullet point is encapsulated in "{format}"',
    'the {which} bullet point is enclosed within "{format}"',
    'the {which} bullet point is bounded by "{format}"',
    'the {which} bullet point is enveloped in "{format}"',
    'the {which} bullet point is wrapped inside "{format}"'
]

def wrap_bullet_points(text, bullet_point_map):
    
    bullet_points = re.findall(r'(^[\*\-\d]+\.)', text, re.MULTILINE)
    
    replace_dict = {}
    for i, line in enumerate(bullet_points):
        trimmed_line = line.strip()
        if i in bullet_point_map.keys():
            wrap_symbol = bullet_point_map[i]
            replace_dict[trimmed_line] = wrap_symbol.format(text=trimmed_line)
    
    return replace_dict

def do_FORMAT_WRAP_BULLET(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(response)

    if bullet_point_count == 0:
        return {'instruction': instruction, 'output': response, 'type': 'None'}

    sample_count_min = 1 if int(bullet_point_count*0.5) == 0 else int(bullet_point_count*0.5)
    sample_count = min(MAX_COUNT, sample_count_min)
    sampled_idx = random.sample(range(bullet_point_count), sample_count)
    sampled_idx = sorted(sampled_idx)

    instruction_seg = ''
    bullet_map = {}
    indicator_meta_seg = random.randint(0, len(META_SEG_FORMAT_WRAP_BULLET)-1)
    for idx in sampled_idx:
        indicator_bracket_format = random.randint(0, len(FORMAT_BRACKET_LIST)-1)
        bracket_format = FORMAT_BRACKET_LIST[indicator_bracket_format].format(text=' ')

        bullet_map[idx] = FORMAT_BRACKET_LIST[indicator_bracket_format]
        
        if idx >= len(FORMAT_ORDER_LIST):
            which = str(idx+1) + 'th'
        else:
            which = FORMAT_ORDER_LIST[idx]
        instruction_seg += (META_SEG_FORMAT_WRAP_BULLET[indicator_meta_seg].format(which=which, format=bracket_format) + ', ')

    replace_dict = wrap_bullet_points(response, bullet_map)
    for key, value in replace_dict.items():
        response = response.replace(key, value)
    
    indicator_meta = random.randint(0, len(META_FORMAT_WRAP_BULLET)-1)
    instruction_meta = META_FORMAT_WRAP_BULLET[indicator_meta].format(meta_seg=instruction_seg[:-2])

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'FORMAT_WRAP_BULLET'}


################################################
# FUNCTION: do_FORMAT_WRAP_PARAGRAPH
################################################

META_FORMAT_WRAP_PARAGRAPH = [
    'Ensure {meta_seg} in the response.',
    'Make sure {meta_seg} in the response.',
    'Ensure {meta_seg} in the response',
    'Guarantee {meta_seg} in the response.',
    'Ascertain {meta_seg}.',
    'Keep {meta_seg}in the response.',
    'Be certain {meta_seg} within the response.',
    'Make certain that {meta_seg} in the response.'
]

META_SEG_FORMAT_WRAP_PARAGRAPH = [
    'the {which} paragraph is wrapped in "{format}"',
    'the {which} paragraph is within "{format}"',
    'the {which} paragraph is wrapped within "{format}"',
    'the {which} paragraph is encapsulated in "{format}"',
    'the {which} paragraph is enclosed within "{format}"',
    'the {which} paragraph is bounded by "{format}"',
    'the {which} paragraph is surrounded within "{format}"',
    'the {which} paragraph is enveloped in "{format}"',
    'the {which} paragraph is wrapped inside "{format}"',
    'the {which} paragraph is enclosed in "{format}"'
]

def wrap_paragraphs(text, paragraph_map):
    # Split text into paragraphs
    paragraphs = re.split(r'\n\s*\n', text.strip())
    
    replace_dict = {}
    for i, paragraph in enumerate(paragraphs):
        trimmed_paragraph = paragraph.strip()
        if i in paragraph_map.keys():
            wrap_symbol = paragraph_map[i]
            replace_dict[trimmed_paragraph] = wrap_symbol.format(text=trimmed_paragraph)

    return replace_dict

def do_FORMAT_WRAP_PARAGRAPH(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(response)

    sample_count_min = 1 if int(paragraph_count*0.5) == 0 else int(paragraph_count*0.5)
    sample_count = min(MAX_COUNT, sample_count_min)
    sampled_idx = random.sample(range(paragraph_count), sample_count)
    sampled_idx = sorted(sampled_idx)

    indicator_use_combined_format = random.choice([0, 1])

    instruction_seg = ''
    paragraph_map = {}
    indicator_meta_seg = random.randint(0, len(META_SEG_FORMAT_WRAP_PARAGRAPH)-1)
    for idx in sampled_idx:
        if indicator_use_combined_format:
            combined_format = get_combined_format()
            bracket_format = combined_format.format(text=' ')
            paragraph_map[idx] = combined_format
        else:
            indicator_bracket_format = random.randint(0, len(FORMAT_BRACKET_LIST)-1)
            bracket_format = FORMAT_BRACKET_LIST[indicator_bracket_format].format(text=' ')
            paragraph_map[idx] = FORMAT_BRACKET_LIST[indicator_bracket_format]
        
        if idx >= len(FORMAT_ORDER_LIST):
            which = str(idx+1) + 'th'
        else:
            which = FORMAT_ORDER_LIST[idx]
        instruction_seg += (META_SEG_FORMAT_WRAP_PARAGRAPH[indicator_meta_seg].format(which=which, format=bracket_format) + ', ')

    replace_dict = wrap_paragraphs(response, paragraph_map)
    for key, value in replace_dict.items():
        response = response.replace(key, value)
    
    indicator_meta = random.randint(0, len(META_FORMAT_WRAP_PARAGRAPH)-1)
    instruction_meta = META_FORMAT_WRAP_PARAGRAPH[indicator_meta].format(meta_seg=instruction_seg[:-2])

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'FORMAT_WRAP_PARAGRAPH'}


################################################
# FUNCTION: do_FORMAT_WRAP_INSTRUCTION
################################################

META_FORMAT_WRAP_INSTRUCTION = [
    'First repeat the instruction wrapped in "{}", then provide the response.',
    "Start by reiterating the instruction enclosed in {}, then give your response.",
    "Please begin by repeating the directive within {}, followed by your response.",
    "Repeat the command inside {}, then offer your response.",
    "Begin by echoing the instruction within {}, and then respond.",
    "Reiterate the instruction enclosed in {}, then proceed with your response.",
    "Start by repeating the guideline inside {}, then give your response.",
    "Please first restate the command within {}, then provide your response.",
    "Begin by repeating the instruction enclosed in {}, followed by your response.",
    "Repeat the instruction enclosed in {}, then offer your response."
]

def do_FORMAT_WRAP_INSTRUCTION(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    indicator_use_combined_format = random.choice([0, 1])

    if indicator_use_combined_format:
        combined_format = get_combined_format()
        bracket_format = combined_format.format(text=' ')
        response = combined_format.format(text=instruction) + '\n\n' + response
    else:
        indicator_bracket_format = random.randint(0, len(FORMAT_BRACKET_LIST)-1)
        bracket_format = FORMAT_BRACKET_LIST[indicator_bracket_format].format(text=' ')
        response = FORMAT_BRACKET_LIST[indicator_bracket_format].format(text=instruction) + '\n\n' + response

    indicator_meta = random.randint(0, len(META_FORMAT_WRAP_INSTRUCTION)-1)
    instruction_meta = META_FORMAT_WRAP_INSTRUCTION[indicator_meta].format(bracket_format)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'FORMAT_WRAP_INSTRUCTION'}


################################################
# FUNCTION: do_FORMAT_WRAP_RESPONSE
################################################

META_FORMAT_WRAP_RESPONSE = [
    'Wrap the whole response in {}.',
    'Enclose the entire response within {}.',
    'Place the entire response inside {}.',
    'Encapsulate the whole response in {}.',
    'Frame the full response with {}.',
    'Wrap the entire response in {}.',
    'Bracket the whole response within {}.',
    'Frame the complete response with {}.',
    'Bracket the full response in {}.',
    'Wrap the complete response with {}.'
]

def do_FORMAT_WRAP_RESPONSE(data_item):

    instruction = data_item['instruction']
    response = data_item['output']

    indicator_use_combined_format = random.choice([0, 1])

    if indicator_use_combined_format:
        combined_format = get_combined_format()
        bracket_format = combined_format.format(text=' ')
        response = combined_format.format(text=response)
    else:
        indicator_bracket_format = random.randint(0, len(FORMAT_BRACKET_LIST)-1)
        bracket_format = FORMAT_BRACKET_LIST[indicator_bracket_format].format(text=' ')
        response = FORMAT_BRACKET_LIST[indicator_bracket_format].format(text=response)

    indicator_meta = random.randint(0, len(META_FORMAT_WRAP_RESPONSE)-1)
    instruction_meta = META_FORMAT_WRAP_RESPONSE[indicator_meta].format(bracket_format)

    indicator_overall = random.randint(0, len(OVERALL_INSTRUCTION_LIST)-1)
    instruction_overall = OVERALL_INSTRUCTION_LIST[indicator_overall].format(meta_instruction=instruction_meta, instruction_ori=instruction)

    return {'instruction': instruction_overall, 'output': response, 'type': 'FORMAT_WRAP_RESPONSE'}

