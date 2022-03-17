# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
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
import base64
import traceback
from typing import Union
import random
import numpy as np
import json

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from starlette.websockets import WebSocketState as WebSocketState

from paddlespeech.ws.engine.asr.online.asr_engine import ASREngine
from paddlespeech.ws.engine.engine_pool import get_engine_pool

router = APIRouter()


@router.websocket('/ws/asr')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # careful here, changed the source code from starlette.websockets
            assert websocket.application_state == WebSocketState.CONNECTED
            message = await websocket.receive()
            websocket._raise_on_disconnect(message)
            if "text" in message:
                message = json.loads(message["text"])
                if 'signal' not in message:
                    resp = {
                            "status": "ok",
                            "message": "no valid json data"
                            }
                    await websocket.send_json(resp)

                if message['signal'] == 'start':
                    resp = {
                            "status": "ok",
                            "signal": "server_ready"
                            }
                    # do something at begining here
                    await websocket.send_json(resp)
                elif message['signal'] == 'end':
                    engine_pool = get_engine_pool()
                    asr_engine = engine_pool['asr']
                    # reset single  engine for an new connection
                    asr_engine.reset()
                    resp = {
                            "status": "ok",
                            "signal": "finished"
                            }
                    await websocket.send_json(resp)
                    break
                else:
                    resp = {
                            "status": "ok",
                            "message": "no valid json data"
                            }
                    await websocket.send_json(resp)
            elif "bytes" in message:
                message = message["bytes"]

                # run engine here
                engine_pool = get_engine_pool()
                asr_engine = engine_pool['asr']
                # float 32 
                samples = np.frombuffer(message, dtype=np.float32)
                sample_rate = asr_engine.config.sample_rate

                x_chunk, x_chunk_lens = asr_engine.preprocess(samples, sample_rate)
                asr_engine.run(x_chunk, x_chunk_lens)
                asr_results = asr_engine.postprocess()
                resp = {'asr_results': asr_results}

                await websocket.send_json(resp)
    except WebSocketDisconnect:
        pass
