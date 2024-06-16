import random
import string

def generate_random_name(language='English'):
    # Language-specific configurations
    configurations = {
        'English': {
            'vowels': 'aeiou',
            'consonants': 'bcdfghjklmnpqrstvwxyz',
            'syllable_patterns': ['CVC', 'CV', 'VC', 'CVCV', 'VCV'],
            'weights': {
                'vowels': {v: 10 for v in 'aeiou'},
                'consonants': {c: 2 + (c in 'tnrsl') for c in 'bcdfghjklmnpqrstvwxyz'}
            }
        }
    }

    config = configurations.get(language, configurations['English'])

    # Weighted selection of vowels and consonants
    vowels = ''.join([v * config['weights']['vowels'][v] for v in config['vowels']])
    consonants = ''.join([c * config['weights']['consonants'][c] for c in config['consonants']])

    # Randomly select a syllable pattern
    pattern = random.choice(config['syllable_patterns'])
    name = []

    for char in pattern:
        if char == 'C':
            name.append(random.choice(consonants))
        elif char == 'V':
            name.append(random.choice(vowels))

    # Capitalize and assemble the name
    final_name = ''.join(name).capitalize()

    # Check name against rule-based filters
    if is_acceptable_name(final_name):
        return final_name
    else:
        # Recursively generate a new name if the first attempt fails filters
        return generate_random_name(language)

def is_acceptable_name(name):
    """ Rule-based filter to exclude certain combinations or sequences. """
    unacceptable_sequences = ['xx', 'qq', 'uu', 'xyz', 'vwx']
    for seq in unacceptable_sequences:
        if seq in name:
            return False
    return True

# Example usage
print(generate_random_name())
for _ in range(10):
    print(generate_random_name())
