#!/bin/bash

config_path=$1
train_output_path=$2
ckpt_name=$3

stage=0
stop_stage=1

if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
    echo 'speech synthesize !'
    FLAGS_allocator_strategy=naive_best_fit \
    FLAGS_fraction_of_gpu_memory_to_use=0.01 \
    python3 ${BIN_DIR}/synthesize_e2e.py \
        --task_name=synthesize \
        --wav_path=source/p243_313.wav \
        --old_str='For that reason cover should not be given' \
        --new_str='I love you very much do you love me' \
        --source_lang=en \
        --target_lang=en \
        --erniesat_config=${config_path} \
        --phones_dict=dump/phone_id_map.txt \
        --erniesat_ckpt=${train_output_path}/checkpoints/${ckpt_name} \
        --erniesat_stat=dump/train/speech_stats.npy \
        --voc=hifigan_vctk \
        --voc_config=hifigan_vctk_ckpt_0.2.0/default.yaml \
        --voc_ckpt=hifigan_vctk_ckpt_0.2.0/snapshot_iter_2500000.pdz \
        --voc_stat=hifigan_vctk_ckpt_0.2.0/feats_stats.npy \
        --output_name=exp/pred_gen.wav
fi

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    echo 'speech edit !'
    FLAGS_allocator_strategy=naive_best_fit \
    FLAGS_fraction_of_gpu_memory_to_use=0.01 \
    python3 ${BIN_DIR}/synthesize_e2e.py \
        --task_name=edit \
        --wav_path=source/p243_313.wav \
        --old_str='For that reason cover should not be given' \
        --new_str='For that reason cover is not impossible to be given.' \
        --source_lang=en \
        --target_lang=en \
        --erniesat_config=${config_path} \
        --phones_dict=dump/phone_id_map.txt \
        --erniesat_ckpt=${train_output_path}/checkpoints/${ckpt_name} \
        --erniesat_stat=dump/train/speech_stats.npy \
        --voc=hifigan_vctk \
        --voc_config=hifigan_vctk_ckpt_0.2.0/default.yaml \
        --voc_ckpt=hifigan_vctk_ckpt_0.2.0/snapshot_iter_2500000.pdz \
        --voc_stat=hifigan_vctk_ckpt_0.2.0/feats_stats.npy \
        --output_name=exp/pred_edit.wav
fi
