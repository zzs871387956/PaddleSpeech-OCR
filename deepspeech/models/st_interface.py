"""ST Interface module."""


import argparse
from deepspeech.utils.dynamic_import import dynamic_import
from .asr_interface import ASRInterface

class STInterface(ASRInterface):
    """ST Interface model implementation.

    NOTE: This class is inherited from ASRInterface to enable joint translation
    and recognition when performing multi-task learning with the ASR task.

    """

    def translate(self, x, trans_args, char_list=None, rnnlm=None, ensemble_models=[]):
        """Recognize x for evaluation.

        :param ndarray x: input acouctic feature (B, T, D) or (T, D)
        :param namespace trans_args: argment namespace contraining options
        :param list char_list: list of characters
        :param paddle.nn.Layer rnnlm: language model module
        :return: N-best decoding results
        :rtype: list
        """
        raise NotImplementedError("translate method is not implemented")

    def translate_batch(self, x, trans_args, char_list=None, rnnlm=None):
        """Beam search implementation for batch.

        :param paddle.Tensor x: encoder hidden state sequences (B, Tmax, Henc)
        :param namespace trans_args: argument namespace containing options
        :param list char_list: list of characters
        :param paddle.nn.Layer rnnlm: language model module
        :return: N-best decoding results
        :rtype: list
        """
        raise NotImplementedError("Batch decoding is not supported yet.")


predefined_st = {
    "transformer": "deepspeech.models.u2_st:U2STModel",
}

def dynamic_import_st(module):
    """Import ST models dynamically.

    Args:
        module (str): module_name:class_name or alias in `predefined_st`

    Returns:
        type: ST class

    """
    model_class = dynamic_import(module, predefined_st)
    assert issubclass(
        model_class, STInterface
    ), f"{module} does not implement STInterface"
    return model_class
