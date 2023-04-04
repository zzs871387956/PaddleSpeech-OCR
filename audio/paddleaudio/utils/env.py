# Copyright (c) 2021  PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
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
'''
This module is used to store environmental variables in PaddleAudio.
PPAUDIO_HOME     -->  the root directory for storing PaddleAudio related data. Default to ~/.paddleaudio. Users can change the
├                            default value through the PPAUDIO_HOME environment variable.
├─ MODEL_HOME    -->  Store model files.
└─ DATA_HOME     -->  Store automatically downloaded datasets.
'''
import os

__all__ = [
    'USER_HOME',
    'PPAUDIO_HOME',
    'MODEL_HOME',
    'DATA_HOME',
]


def _get_user_home():
    return os.path.expanduser('~')


def _get_ppaudio_home():
    if 'PPAUDIO_HOME' in os.environ:
        home_path = os.environ['PPAUDIO_HOME']
        if os.path.exists(home_path):
            if os.path.isdir(home_path):
                return home_path
            else:
                raise RuntimeError(
                    'The environment variable PPAUDIO_HOME {} is not a directory.'
                    .format(home_path))
        else:
            return home_path
    return os.path.join(_get_user_home(), '.paddleaudio')


def _get_sub_home(directory):
    home = os.path.join(_get_ppaudio_home(), directory)
    if not os.path.exists(home):
        os.makedirs(home)
    return home


USER_HOME = _get_user_home()
PPAUDIO_HOME = _get_ppaudio_home()
MODEL_HOME = _get_sub_home('models')
DATA_HOME = _get_sub_home('datasets')
