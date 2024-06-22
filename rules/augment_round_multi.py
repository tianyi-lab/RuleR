import json
import random
import argparse
from tqdm import tqdm

from augment_rules import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default='xxx.json')
    parser.add_argument("--save_path", type=str, default='xxx_augmented.json')
    parser.add_argument("--augment_rate", type=float, default=0.9)
    parser.add_argument("--epo_num", type=int, default=2)
    parser.add_argument("--concate_layer", type=int, default=3)
    args = parser.parse_args()
    return args


def main():

    args = parse_args()
    print(args)

    # Load the original data from the file
    with open(args.data_path, 'r') as file:
        original_data = json.load(file)

    all_shuffled_data = []  # Master list to hold all shuffled data

    for epo in tqdm(range(args.epo_num)):

        shuffled_data = original_data.copy()  # Create a copy of the original data for each shuffle
        random.shuffle(shuffled_data)

        id_count = 0
        for item_i in tqdm(shuffled_data):
            conversations = item_i['conversations']

            if conversations[0]['from'] == 'human' and conversations[1]['from'] == 'gpt':

                conversations_new_list = []
                for i in range(0, len(conversations), 2):
                    if i+1 == len(conversations):
                        break

                    assert conversations[i]['from'] == 'human'
                    assert conversations[i+1]['from'] == 'gpt'

                    item = {}
                    item['instruction'] = conversations[i]['value']
                    item['output'] = conversations[i+1]['value']

                    indicator_is_code = is_code_snippet(item['output'])
                    if indicator_is_code:
                        indicator_do_augment = random.random() < args.augment_rate
                        if indicator_do_augment:
                            indicator_rule_code = random.randint(0, len(RULE_TYPES_CODE)-1)
                            rule_function = 'do_' + RULE_TYPES_CODE[indicator_rule_code] + '(item)'
                        else:
                            rule_function = 'do_NONE(item)'
                    else:
                        indicator_do_augment = random.random() < args.augment_rate

                        word_count, sentence_count, paragraph_count, bullet_point_count = get_text_statistics(item['output'])
                        if indicator_do_augment:
                            if bullet_point_count >= 3:
                                indicator_use_bullet = random.choice([0, 1])
                                if args.concate_layer == 1:
                                    if indicator_use_bullet:
                                        indicator_rule_bullet = random.randint(0, len(RULE_TYPES_BULLET)-1)
                                        rule_function = 'do_' + RULE_TYPES_BULLET[indicator_rule_bullet] + '(item)'
                                    else:
                                        indicator_rule_no_bullet = random.randint(0, len(RULE_TYPES_NO_BULLET)-1)
                                        rule_function = 'do_' + RULE_TYPES_NO_BULLET[indicator_rule_no_bullet] + '(item)'
                                else:
                                    layer_to_use = random.choice([i for i in range(1, args.concate_layer+1)])
                                    rules_to_use = random.sample(RULE_TYPES_BULLET + RULE_TYPES_NO_BULLET, layer_to_use)
                                    for rule in rules_to_use:
                                        rule_function = 'do_' + rule + '(item)'
                                        item = eval(rule_function)
                            else:
                                if args.concate_layer == 1:
                                    indicator_rule_no_bullet = random.randint(0, len(RULE_TYPES_NO_BULLET)-1)
                                    rule_function = 'do_' + RULE_TYPES_NO_BULLET[indicator_rule_no_bullet] + '(item)'
                                else:
                                    layer_to_use = random.choice([i for i in range(1, args.concate_layer+1)])
                                    rules_to_use = random.sample(RULE_TYPES_NO_BULLET, layer_to_use)
                                    for rule in rules_to_use:
                                        rule_function = 'do_' + rule + '(item)'
                                        item = eval(rule_function)
                        else:
                            rule_function = 'do_NONE(item)'

                    if args.concate_layer == 1:
                        formated_data_temp = eval(rule_function)
                    else:
                        formated_data_temp = item

                    conversations_new_list.append({'from':'human','value':formated_data_temp['instruction']})    
                    conversations_new_list.append({'from':'gpt','value':formated_data_temp['output']})

                dict_fake = {}
                dict_fake['id'] = id_count
                dict_fake['conversations'] = conversations_new_list
                dict_fake['source'] = 'ShareGPT'
                dict_fake['Tag'] = 'Fake'

                if formated_data_temp != {}:
                    all_shuffled_data.append(dict_fake)
                    id_count += 1
            else:

                item_i['id'] = id_count
                all_shuffled_data.append(item_i)
                id_count += 1

    # Store all concatenated groups in a new JSON file
    with open(args.save_path, 'w') as outfile:
        json.dump(all_shuffled_data, outfile, indent=2)


if __name__ == "__main__":
    main()
