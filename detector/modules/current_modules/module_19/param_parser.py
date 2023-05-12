import argparse

def parameter_parser():
    parser = argparse.ArgumentParser(description="Run OpcodeExtraction.")
    
    parser.add_argument('--input-path','-i',
                        nargs='?',
                        default='',
                        help='Please input the binary file path.')
    parser.add_argument('--output-path','-o',
                        nargs='?',
                        default='Output')

    return parser.parse_args()