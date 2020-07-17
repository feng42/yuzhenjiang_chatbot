# _*_ coding:utf-8 _*_
'''
@author:   zhangfeng
@mail:  jiangchayanjiuyuan@163.com
@date:  2020/7/17 下午3:19
@file: ChatWorker.py
'''

import sys
import traceback

from config import config_model
from src.utils.logger import LOGGER

import torch
from transformers.modeling_gpt2 import GPT2LMHeadModel
from transformers import BertTokenizer


class ChatWorker(object):
    def __init__(self):
        try:
            self.device = 'cuda' if config_model.use_cuda else 'cpu'
            LOGGER.info('using device: {}'.format(self.device))
            self.tokenizer = BertTokenizer(config_model.vocab_path)

            # dialogue model
            self.dialogue_model = GPT2LMHeadModel.from_pretrained(config_model.dialogue_model_path)
            self.dialogue_model.to(self.device)
            self.dialogue_model.eval()

            # mmi model
            self.mmi_model = GPT2LMHeadModel.from_pretrained(config_model.mmi_model_path)
            self.mmi_model.to(self.device)
            self.dialogue_model.eval()

            self.max_sequence_len = config_model.max_len
            self.batch_size = config_model.batch_size
            self.repetition_penalty = config_model.repetition_penalty
            self.temperature = config_model.temperature
            self.debug = config_model.debug


        except Exception as e:
            LOGGER.error("FAIL INIT: {}".format(str(e)))
            traceback.print_exc()
            sys.exit(-1)


    def encode_to_ids(self, text):
        try:
            return self.tokenizer.encode(text)
        except Exception as e:
            LOGGER.error("FAIL INIT: {}".format(str(e)))
            traceback.print_exc()

    def generate(self, input_text,history):
        try:
            curr_input_tensors = torch.tensor(input_ids).long().to(self.device)
            candidate_responses = self._make_dialogue_response(curr_input_tensors)
            assert len(candidate_responses) >= 1
        except Exception as e:
            LOGGER.error("FAIL GEN: {}".format(str(e)))
            traceback.print_exc()
            return

    def _make_dialogue_response(self, input_tensors):
        try:
            generated = []
            finish_set = set()  # 标记是否所有response均已生成结束，若第i个response生成结束，即生成了sep_token_id，则将i放入finish_set
            # 最多生成max_len个token
            for _ in range(self.max_sequence_len):
                outputs = self.dialogue_model(input_ids=input_tensors)
                next_token_logits = outputs[0][:, -1, :]
                # 对于已生成的结果generated中的每个token添加一个重复惩罚项，降低其生成概率
                for index in range(self.batch_size):
                    for token_id in set([token_ids[index] for token_ids in generated]):
                        next_token_logits[index][token_id] /= self.repetition_penalty
                next_token_logits = next_token_logits / self.temperature
                # 对于[UNK]的概率设为无穷小，也就是说模型的预测结果不可能是[UNK]这个token
                for next_token_logit in next_token_logits:
                    next_token_logit[self.tokenizer.convert_tokens_to_ids('[UNK]')] = -float('Inf')
                filtered_logits = self._top_k_top_p_filtering(next_token_logits, top_k=self.topk, top_p=self.topp)
                # torch.multinomial表示从候选集合中无放回地进行抽取num_samples个元素，权重越高，抽到的几率越高，返回元素的下标
                next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1), num_samples=1)
                # 判断是否有response生成了[SEP],将已生成了[SEP]的resposne进行标记
                for index, token_id in enumerate(next_token[:, 0]):
                    if token_id == self.tokenizer.sep_token_id:
                        finish_set.add(index)
                # 检验是否所有的response均已生成[SEP]
                finish_flag = True  # 是否所有的response均已生成[SEP]的token
                for index in range(self.batch_size):
                    if index not in finish_set:  # response批量生成未完成
                        finish_flag = False
                        break
                if finish_flag:
                    break
                generated.append([token.item() for token in next_token[:, 0]])
                # 将新生成的token与原来的token进行拼接
                curr_input_tensors = torch.cat((input_tensors, next_token), dim=-1)
            candidate_responses = []  # 生成的所有候选response
            for batch_index in range(self.batch_size):
                response = []
                for token_index in range(len(generated)):
                    if generated[token_index][batch_index] != self.tokenizer.sep_token_id:
                        response.append(generated[token_index][batch_index])
                    else:
                        break
                candidate_responses.append(response)
            return candidate_responses
        except Exception as e:
            LOGGER.error("FAIL make response: {}".format(str(e)))
            traceback.print_exc()
            return []

    def _make_mmi_output(self, candidate_responses, history):
        if self.debug:
            print("candidate response:")
        # samples_file.write("candidate response:\n")
        min_loss = float('Inf')
        best_response = ""
        for response in candidate_responses:
            mmi_input_id = [self.tokenizer.cls_token_id]  # 每个input以[CLS]为开头
            mmi_input_id.extend(response)
            mmi_input_id.append(self.tokenizer.sep_token_id)
            for history_utr in reversed(history):
                mmi_input_id.extend(history_utr)
                mmi_input_id.append(self.tokenizer.sep_token_id)
            mmi_input_tensor = torch.tensor(mmi_input_id).long().to(self.device)
            out = self.mmi_model(input_ids=mmi_input_tensor, labels=mmi_input_tensor)
            loss = out[0].item()
            if self.debug:
                text = self.tokenizer.convert_ids_to_tokens(response)
                print("{} loss:{}".format("".join(text), loss))
            # samples_file.write("{} loss:{}\n".format("".join(text), loss))
            if loss < min_loss:
                best_response = response
                min_loss = loss
        history.append(best_response)

    def _top_k_top_p_filtering(self, logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
        """ Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
            Args:
                logits: logits distribution shape (vocabulary size)
                top_k > 0: keep only top k tokens with highest probability (top-k filtering).
                top_p > 0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
                    Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751)
        """
        assert logits.dim() == 2
        top_k = min(top_k, logits[0].size(-1))  # Safety check
        if top_k > 0:
            # Remove all tokens with a probability less than the last token of the top-k
            # torch.topk()返回最后一维最大的top_k个元素，返回值为二维(values,indices)
            # ...表示其他维度由计算机自行推断
            for logit in logits:
                indices_to_remove = logit < torch.topk(logit, top_k)[0][..., -1, None]
                logit[indices_to_remove] = filter_value  # 对于topk之外的其他元素的logits值设为负无穷

        if top_p > 0.0:
            sorted_logits, sorted_indices = torch.sort(logits, descending=True, dim=-1)  # 对logits进行递减排序
            cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

            # Remove tokens with cumulative probability above the threshold
            sorted_indices_to_remove = cumulative_probs > top_p
            # Shift the indices to the right to keep also the first token above the threshold
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0
            for index, logit in enumerate(logits):
                indices_to_remove = sorted_indices[index][sorted_indices_to_remove[index]]
                logit[indices_to_remove] = filter_value
        return logits