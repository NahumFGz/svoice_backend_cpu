import os
import sys
import argparse
import logging

def main(args):
    model    = args.model
    mix_path = args.mix_path
    out_path = args.out_path

    #command = 'python -m svoice.separate H:/svoice_backend/demo/checkpoint.th H:/svoice_backend/demo/out --mix_dir=H:/svoice_backend/demo/mix'
    command = 'python -m svoice.separate ./demo/checkpoint.th ./demo/out --mix_dir=./demo/mix'

    os.system(command)


if __name__ == "__main__":
    ## TRAIN PARAMETERS
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='./demo/checkpoint.th',
                        help='Ruta del modelo')
    parser.add_argument('--mix_path', type=str, default='./demo/mix',
                        help='Ruta de mix')
    parser.add_argument('--out_path', type=str, default='./demo/out',
                        help='Ruta de resultados')
    args = parser.parse_args()

    main(args)
