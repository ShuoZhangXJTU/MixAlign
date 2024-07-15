import argparse


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name_eval', type=str, default='gpt-4', help='evaluation')
    parser.add_argument('--model_name', type=str, default='text-davinci-003', help='use for generation')
    parser.add_argument('--apikey', type=str, default='your key')
    return parser.parse_args()