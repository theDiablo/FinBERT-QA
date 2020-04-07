import argparse
import sys

from helper.utils import *
from qa_lstm import *
from finbert_qa import *

def main():
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument("--model_type", default=None, type=str, required=True,
    help="Specify model type as 'qa-lstm' or 'bert'")

    # Optional arguments
    parser.add_argument("--use_default_config", default=False, \
                        action="store_true", help="Use default configuration")
    parser.add_argument("--train_pickle", default=None, type=str, required=False,\
                        help="Path to training data in .pickle format")
    parser.add_argument("--valid_pickle", default=None, type=str, required=False,\
                        help="Path to validation data in .pickle format")
    parser.add_argument("--device", default='gpu', type=str, required=False,
    help="Specify 'gpu' or 'cpu'")
    parser.add_argument("--max_seq_len", default=512, type=int, required=False,
    help="Maximum sequence length for a given input.")
    parser.add_argument("--batch_size", default=16, type=int, required=False,
    help="Batch size.")
    parser.add_argument("--n_epochs", default=3, type=int, required=False,
    help="Number of epochs.")
    parser.add_argument("--lr", default=3e-6, type=float, required=False,
    help="Number of epochs.")

    # Optional arguments when model_type is 'qa-lstm'
    parser.add_argument("--emb_dim", default=100, type=int, required=False,
    help="Embedding dimension. Specify only if model_type is 'qa-lstm'")
    parser.add_argument("--hidden_size", default=256, type=int, required=False,
    help="Hidden size. Specify only if model_type is 'qa-lstm'")
    parser.add_argument("--dropout", default=0.2, type=float, required=False,
    help="Dropout rate. Specify only if model_type is 'qa-lstm'")

    # Optional arguments when model_type is 'bert'
    parser.add_argument("--bert_model_name", default="bert-qa", type=str, required=False, \
    help="Specify BERT model name to use from 'bert-base', 'finbert-domain', 'finbert-task', 'bert-qa'")
    parser.add_argument("--learning_approach", default="pointwise", type=str, \
                        required=False, help="Learning approach. Specify 'pointwise' or 'pairwise' only if model_type is 'bert'.")
    parser.add_argument("--margin", default=0.2, type=float, required=False,
    help="Margin for pairwise loss. Specify only if model type is 'qa_lstm' or if 'learning_approach' is pairwise")
    parser.add_argument("--weight_decay", default=0.01, type=float, required=False,
    help="Weight decay. Specify only if model type is 'bert'")
    parser.add_argument("--num_warmup_steps", default=10000, type=int, required=False,
    help="Number of warmup steps. Specify only if model type is 'bert'")

    args = parser.parse_args()

    config = {'model_type': args.model_type,
              'use_default_config': args.use_default_config,
              'train_set': args.train_pickle,
              'valid_set': args.valid_pickle,
              'device': args.device,
              'max_seq_len': args.max_seq_len,
              'batch_size': args.batch_size,
              'n_epochs': args.n_epochs,
              'lr': args.lr,
              'emb_dim': args.emb_dim,
              'hidden_size': args.hidden_size,
              'dropout': args.dropout,
              'bert_model_name': args.bert_model_name,
              'learning_approach': args.learning_approach,
              'margin': args.margin,
              'weight_decay': args.weight_decay,
              'num_warmup_steps': args.num_warmup_steps}

    # TO-DO: Catch error for invalid datasets

    if config['model_type'] == 'qa-lstm':
        train_qa_lstm_model(config)
    elif config['model_type'] == 'bert':
        train_bert_model(config)
    else:
        print("Please specify 'qa-lstm' or 'bert' for model_type")
        sys.exit()

if __name__ == "__main__":
    main()
