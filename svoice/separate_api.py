# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

# Authors: Yossi Adi (adiyoss)

import os
import sys

import librosa
import torch
import tqdm

from .data.data import EvalDataLoader, EvalDataset
from . import distrib
from .utils import remove_pad

from .utils import bold, deserialize_model, LogProgress


out_dir = "exp/result"
mix_dir = None
mix_json = None

if torch.cuda.is_available():
    device ="cuda"
else:
    device = "cpu"

sample_rate = 8000
batch_size = 1

def save_wavs(estimate_source, mix_sig, lengths, filenames, out_dir, sr=16000):
    # Remove padding and flat
    flat_estimate = remove_pad(estimate_source, lengths)
    mix_sig = remove_pad(mix_sig, lengths)
    # Write result
    for i, filename in enumerate(filenames):
        filename = os.path.join(
            out_dir, os.path.basename(filename).strip(".wav"))
        write(mix_sig[i], filename + ".wav", sr=sr)
        C = flat_estimate[i].shape[0]
        # future support for wave playing
        for c in range(C):
            write(flat_estimate[i][c], filename + f"_s{c + 1}.wav")


def write(inputs, filename, sr=8000):
    librosa.output.write_wav(filename, inputs, sr, norm=True)


def separate(
    out_dir = None,
    mix_dir = None,
    mix_json = None,
    model_path = None,
    model=None,
    local_out_dir=None
):

    # Load model
    if not model:
        # model
        if torch.cuda.is_available():
            pkg = torch.load(model_path)
        else:
            pkg = torch.load(model_path, map_location=torch.device('cpu'))

        if 'model' in pkg:
            model = pkg['model']
        else:
            model = pkg
        model = deserialize_model(model)
    model.eval()
    model.to(device)
    if local_out_dir:
        out_dir = local_out_dir
    else:
        out_dir = out_dir

    # Load data
    eval_dataset = EvalDataset(
        mix_dir,
        mix_json,
        batch_size=batch_size,
        sample_rate=sample_rate,
    )
    eval_loader = distrib.loader(
        eval_dataset, batch_size=1, klass=EvalDataLoader)

    if distrib.rank == 0:
        os.makedirs(out_dir, exist_ok=True)
    distrib.barrier()

    with torch.no_grad():
        for i, data in enumerate(tqdm.tqdm(eval_loader, ncols=120)):
            # Get batch data
            mixture, lengths, filenames = data
            mixture = mixture.to(device)
            lengths = lengths.to(device)
            # Forward
            estimate_sources = model(mixture)[-1]
            # save wav files
            save_wavs(estimate_sources, mixture, lengths,
                      filenames, out_dir, sr = sample_rate)