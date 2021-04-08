# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Build vocabulary from manifest files.
Each item in vocabulary file is a character.
"""

import argparse
import functools
import json
from collections import Counter
import os
import copy
import tempfile

from deepspeech.frontend.utility import read_manifest
from deepspeech.frontend.utility import UNK
from deepspeech.frontend.utility import BLANK
from deepspeech.frontend.utility import SOS
from deepspeech.utils.utility import add_arguments
from deepspeech.utils.utility import print_arguments
from deepspeech.frontend.featurizer.text_featurizer import TextFeaturizer

parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
# yapf: disable
add_arg('unit_type', str, "char", "Unit type, e.g. char, word, spm")
add_arg('count_threshold',  int,    0,  "Truncation threshold for char/word/spm counts.")
add_arg('vocab_path',       str,
        'examples/librispeech/data/vocab.txt',
        "Filepath to write the vocabulary.")
add_arg('manifest_paths',   str,
        None,
        "Filepaths of manifests for building vocabulary. "
        "You can provide multiple manifest files.",
        nargs='+',
        required=True)
# bpe
add_arg('spm_mode', str, 'unigram',
    "spm model type, e.g. unigram, spm, char, word. only need when `unit_type` is spm")
add_arg('spm_model_prefix', str, "spm_model_%(spm_mode)_%(count_threshold)",
    "spm model prefix, only need when `unit_type` is spm")
# yapf: disable
args = parser.parse_args()


def count_manifest(counter, manifest_path):
    manifest_jsons = read_manifest(manifest_path)
    for line_json in manifest_jsons:
        if args.unit_type == 'char':
            for char in line_json['text']:
                counter.update(char)
        elif args.unit_type == 'word':
            for word in line_json['text'].split():
                counter.update(word)

def read_text_manifest(fileobj, manifest_path):
    manifest_jsons = read_manifest(manifest_path)
    for line_json in manifest_jsons:
        fileobj.write(line_json['text'] + "\n")

def main():
    print_arguments(args)

    fout = open(args.vocab_path, 'w', encoding='utf-8')
    fout.write(BLANK + "\n") # 0 will be used for "blank" in CTC
    fout.write(UNK + '\n')   # <unk> must be 1

    if args.unit_type != 'spm':
        counter = Counter()
        for manifest_path in args.manifest_paths:
            count_manifest(counter, manifest_path)

        count_sorted = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        for char, count in count_sorted:
            if count < args.count_threshold: break
            fout.write(char + '\n')
    else:
        # tools/spm_train --input=$wave_data/lang_char/input.txt 
        # --vocab_size=${nbpe} --model_type=${bpemode} 
        # --model_prefix=${bpemodel} --input_sentence_size=100000000
        import sentencepiece as spm

        fp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        for manifest_path in args.manifest_paths:
            read_text_manifest(fp, manifest_path)
        fp.close()
        # train
        spm.SentencePieceTrainer.Train(
            input=fp.name,
            vocab_size=args.count_threshold,
            model_type=args.spm_mode,
            model_prefix=args.spm_model_prefix,
            input_sentence_size=100000000,
            character_coverage=0.9995)
        os.unlink(fp.name)

        # encode
        text_feature = TextFeaturizer(args.unit_type, args.vocab_path, args.spm_model_prefix)

        vocabs = set()
        for manifest_path in args.manifest_paths:
            manifest_jsons = read_manifest(manifest_path)
            for line_json in manifest_jsons:
                line = line_json['text']
                enc_line = text_feature.spm_tokenize(line)
                for code in enc_line:
                    vocabs.add(code)
                #print(" ".join(enc_line))
        vocabs_sorted = sorted(vocabs)
        for unit in vocabs_sorted:
            fout.write(unit + "\n")

        print(f"spm vocab size: {len(vocabs_sorted)}")

    fout.write(SOS + "\n") # <sos/eos>
    fout.close()


if __name__ == '__main__':
    main()
