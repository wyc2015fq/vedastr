# modify from clovaai

import torch

from .registry import CONVERTERS
from .base_convert import BaseConverter


@CONVERTERS.register_module
class SATRNConverter(BaseConverter):
    def __init__(self, character, batch_max_length, go_last=False):
        list_character = list(character)
        self.batch_max_length = batch_max_length + 1
        if go_last:
            list_token = ['[s]', '[GO]']
            character = list_character + list_token
        else:
            list_token = ['[GO]', '[s]']
            character = list_token + list_character
        super(SATRNConverter, self).__init__(character=character)
        self.ignore_id = self.dict['[GO]']

    def train_encode(self, text):
        length = [len(s) + 1 for s in text]
        batch_text = torch.LongTensor(len(text), self.batch_max_length + 1).fill_(self.ignore_id)
        for idx, t in enumerate(text):
            text = list(t)
            text.append('[s]')
            text = [self.dict[char] for char in text]
            batch_text[idx][1:1 + len(text)] = torch.LongTensor(text)
        batch_text_input = batch_text[:, :-1]
        batch_text_target = batch_text[:, 1:]

        return batch_text_input, torch.IntTensor(length), batch_text_target

    def test_encode(self, text):
        batch_text = torch.LongTensor(len(text), 1).fill_(self.ignore_id)
        length = [1 for _ in range(len(text))]

        return batch_text, torch.IntTensor(length), batch_text

    def decode(self, text_index):
        texts = []
        batch_size = text_index.shape[0]
        for index in range(batch_size):
            text = ''.join([self.character[i] for i in text_index[index, :]])
            text = text[:text.find('[s]')]
            texts.append(text)

        return texts