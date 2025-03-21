import torch.nn as nn
import torch 
import math
BertLayerNorm = torch.nn.LayerNorm

class BertAttention(nn.Module):
    def __init__(self, attention_probs_dropout_prob,num_attention_heads, hidden_size, ctx_dim):
        super().__init__()

        self.num_attention_heads = num_attention_heads
        self.attention_head_size = int(hidden_size / self.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size

        # visual_dim = 2048
        # if ctx_dim is None:
        #     ctx_dim =512
        self.query = nn.Linear(hidden_size, self.all_head_size)
        self.key = nn.Linear(ctx_dim, self.all_head_size)
        self.value = nn.Linear(ctx_dim, self.all_head_size)

        self.dropout = nn.Dropout(attention_probs_dropout_prob)

    def transpose_for_scores(self, x):
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(*new_x_shape)
        return x.permute(0, 2, 1, 3)

    def forward(self, hidden_states, context, attention_mask=None):
        mixed_query_layer = self.query(hidden_states)
        mixed_key_layer = self.key(context)
        mixed_value_layer = self.value(context)

        query_layer = self.transpose_for_scores(mixed_query_layer)
        key_layer = self.transpose_for_scores(mixed_key_layer)
        value_layer = self.transpose_for_scores(mixed_value_layer)

        # Take the dot product between "query" and "key" to get the raw attention scores.
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        # Apply the attention mask is (precomputed for all layers in BertModel forward() function)
        # if attention_mask is not None:
        #     attention_scores = attention_scores + attention_mask

        # Normalize the attention scores to probabilities.
        attention_probs = nn.Softmax(dim=-1)(attention_scores)

        # This is actually dropping out entire tokens to attend to, which might
        # seem a bit unusual, but is taken from the original Transformer paper.
        attention_probs = self.dropout(attention_probs)

        context_layer = torch.matmul(attention_probs, value_layer)
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(*new_context_layer_shape)
        return context_layer


class BertAttOutput(nn.Module):
    def __init__(self,hidden_size,hidden_dropout_prob):
        super(BertAttOutput, self).__init__()
        self.dense = nn.Linear(hidden_size, hidden_size)
        self.LayerNorm = BertLayerNorm(hidden_size, eps=1e-12)
        self.dropout = nn.Dropout(hidden_dropout_prob)

    def forward(self, hidden_states, input_tensor):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states


class CrossattLayer(nn.Module):
    def __init__(self, attention_probs_dropout_prob=0.1,num_attention_heads=8, hidden_size=512,hidden_dropout_prob=0.1):
        super().__init__()
        self.att = BertAttention(attention_probs_dropout_prob=0.1,num_attention_heads=8, hidden_size=512, ctx_dim=512)
        self.output = BertAttOutput(hidden_size,hidden_dropout_prob=0.1)

    def forward(self, input_tensor, ctx_tensor, ctx_att_mask=None):
        output = self.att(input_tensor, ctx_tensor, ctx_att_mask)
        attention_output = self.output(output, input_tensor)
        return attention_output



class BertselfattLayer(nn.Module):
    def __init__(self, attention_probs_dropout_prob=0.1,num_attention_heads=8, hidden_size=512,hidden_dropout_prob=0.1):
        super(BertselfattLayer, self).__init__()
        self.att = BertAttention(attention_probs_dropout_prob=0.1,num_attention_heads=8, hidden_size=512, ctx_dim=512)
        self.output = BertAttOutput(hidden_size,hidden_dropout_prob=0.1)

    def forward(self, input_tensor, ctx_tensor, attention_mask=None):
        # Self attention attends to itself, thus keys and querys are the same (input_tensor).
        self_output = self.att(input_tensor, ctx_tensor, attention_mask)
        attention_output = self.output(self_output, input_tensor)
        return attention_output


class BertCrossattLayer(nn.Module):
    def __init__(self, attention_probs_dropout_prob=0.1,num_attention_heads=8, hidden_size=256,hidden_dropout_prob=0.1):
        super().__init__()
        self.att = BertAttention(attention_probs_dropout_prob=0.1,num_attention_heads=8, hidden_size=256, ctx_dim=256)
        self.output = BertAttOutput(hidden_size,hidden_dropout_prob=0.1)

    def forward(self, input_tensor, ctx_tensor, ctx_att_mask=None):
        output = self.att(input_tensor, ctx_tensor, ctx_att_mask)
        attention_output = self.output(output, input_tensor)
        return attention_outp






