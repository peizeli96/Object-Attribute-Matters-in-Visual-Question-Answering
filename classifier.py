import torch
import numpy as np
import torch.nn as nn
from torch.nn.utils.weight_norm import weight_norm
import activation as act

class SimpleClassifier(nn.Module):
    def __init__(self, in_dim, hid_dim, out_dim, args, activation='swish',dropout=0.5):
        super(SimpleClassifier, self).__init__()
        activation_dict = {'relu': nn.ReLU(), 'swish': act.Swish()}
        try:
            activation_func = activation_dict[args.activation]
        except:
            raise AssertionError(activation + " is not supported yet!")
        layers = [
            weight_norm(nn.Linear(in_dim, hid_dim), dim=None),
            activation_func,
            nn.Dropout(dropout, inplace=True),
            weight_norm(nn.Linear(hid_dim, out_dim), dim=None)
        ]
        self.main = nn.Sequential(*layers)

    def forward(self, x):
        logits = self.main(x)
        return logits
