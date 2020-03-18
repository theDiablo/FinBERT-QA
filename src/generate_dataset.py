import argparse
from tqdm import tqdm
import random
import math

from utils import *

class get_data:
    def __init__(self, cands_path, qid_rel_path, cands_size):
        """
        qid_rel: dictionary
            Dictionary with question ids and list of relevant answer ids
        cands_path: string
            Path of candidate answers
        cand_size: int
            Candidate answers size
        """
        self.cands_path = cands_path
        self.qid_rel_path = qid_rel_path
        self.cands_size = cands_size

    def load_cands(self):
        """Returns a dictionary of candidate answers for each question.

        qid_ranked_docs: dictionary
            key - qid
            value - list of k ranked candidates
        """
        qid_ranked_docs = {}

        with open(self.cands_path,'r') as f:
            for line in f:
                # Extract data in the form [qid, doc_id, rank]
                line = line.strip().split('\t')
                qid = int(line[0])
                doc_id = int(line[1])
                rank = int(line[2])

                if qid not in qid_ranked_docs:
                    # Create a list for each query to store the candidates
                    candidates = [0]*self.cands_size
                    qid_ranked_docs[qid] = candidates
                qid_ranked_docs[qid][rank-1] = doc_id

        return qid_ranked_docs

    def get_train_valid_set(self, neg_ans_size):
        """Samples negative answers for each question and
        returns a nested list of train and validation data.

        data_set: list
            [[qid, positive ans id, negative ans id]]
        ----------
        neg_ans_size: int
            The number of negative answers to sample
        """
        # Dictionary of question id and list of positive answers
        qid_rel = load_pickle(self.qid_rel_path)
        # Dictionary of question id and list of candidate answers
        cands = self.load_cands()

        data_set = []

        for qid, pos_ans_lst in tqdm(qid_rel.items()):
            # Get the number of negative candidates to sample
            num_sample = math.floor(neg_ans_size/len(pos_ans_lst))
            for i, cand_lst in cands.items():
                # Get candidates that are not positive answers
                trimed_cand = [x for x in cand_lst if x not in pos_ans_lst]

            # If there is only 1 relevant answer
            if num_sample == neg_ans_size:
                for _ in range(neg_ans_size):
                    tmp = []
                    tmp.append(qid)
                    tmp.append(pos_ans_lst[0])
                    neg_doc = random.choice(trimed_cand)
                    tmp.append(neg_doc)
                    data_set.append(tmp)
            else:
                for _ in range(num_sample):
                    for j in range(len(pos_ans_lst)):
                        tmp = []
                        tmp.append(qid)
                        tmp.append(pos_ans_lst[j])
                        neg_doc = random.choice(trimed_cand)
                        tmp.append(neg_doc)
                        data_set.append(tmp)
                for k in range(neg_ans_size % len(pos_ans_lst)):
                    tmp = []
                    tmp.append(qid)
                    tmp.append(pos_ans_lst[k])
                    neg_doc = random.choice(trimed_cand)
                    tmp.append(neg_doc)
                    data_set.append(tmp)

        for row in data_set:
            assert len(row) == 3, "Train/Valid set length is incorrect!"

        assert len(data_set) == neg_ans_size*len(cands), "Dataset size is incorrect!"

        return data_set

    def get_test_set(self, full=False):
        """Returns a nested list of question id, list of positive ans id,
        and a list of sampled negative ans ids.

        test_set: list
            [[qid, [positive ans ids], [negative ans ids]]
        ----------
        full: boolean
            Rather to sample a test set with all positive answers or the
            use the candidates from the retriver
        """
        # Dictionary of question id and list of positive answers
        qid_rel = load_pickle(self.qid_rel_path)
        # Dictionary of question id and list of candidate answers
        cands = self.load_cands()

        test_set = []

        for qid, docid in tqdm(qid_rel.items()):
            for ques, cand in cands.items():
                # Create candidates with positive answers
                if not full:
                    trimed_cand = [x for x in cand if x not in docid]
                    # Sample the number of cands minus the number of positive ans
                    cand_ans = random.sample(trimed_cand, self.cands_size-len(docid))
                    cand_ans.extend(docid)
                else:
                    # Use candidates from retriver
                    cand_ans = cand

                if ques == qid:
                    tmp = []
                    tmp.append(qid)
                    tmp.append(docid)
                    tmp.append(cand_ans)
                    test_set.append(tmp)

        for row in test_set:
            assert len(row[2]) == self.cands_size, "Dataset size is incorrect!"

        return test_set


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # Required parameters
    parser.add_argument("--train_cands", default=None, type=str, required=True,
                        help="Path to the training candidates data in .tsv format. Each line should have three items "
                             "(questiod id, answer id, rank) separated by tab")
    parser.add_argument("--valid_cands", default=None, type=str, required=True,
                        help="Path to the validation candidates data in .tsv format. Each line should have three items "
                             "(questiod id, answer id, rank) separated by tab")
    parser.add_argument("--test_cands", default=None, type=str, required=True,
                        help="Path to the testing candidates data in .tsv format. Each line should have three items "
                             "(questiod id, answer id, rank) separated by tab")
    parser.add_argument("--train_label", default=None, type=str, required=False,
                        help="Path to the training label data in .pickle format.")
    parser.add_argument("--valid_label", default=None, type=str, required=False,
                        help="Path to the validation label data in .pickle format.")
    parser.add_argument("--test_label", default=None, type=str, required=False,
                        help="Path to the testing label data in .pickle format.")
    parser.add_argument("--output_dir", default=None, type=str, required=True,
                        help="The output directory where the generated data will be stored.")

    # Other parameters
    parser.add_argument("--cands_size", default=500, type=int,
                        help="Number of candidates per question.")
    parser.add_argument("--neg_ans_size", default=50, type=int,
                       help="Number of negative answers to sample.")

    args = parser.parse_args()

    train = get_data(args.train_cands, args.train_label, args.cands_size)
    print("\nCreating train set...\n")
    train_set = train.get_train_valid_set(args.neg_ans_size)
    print("\nTrain set created.\n")

    valid = get_data(args.valid_cands, args.valid_label, args.cands_size)
    print("\nCreating validation set...\n")
    valid_set = valid.get_train_valid_set(args.neg_ans_size)
    print("\nValidation set created.\n")

    test = get_data(args.test_cands, args.test_label, args.cands_size)
    print("\nCreating test set...\n")
    test_set = test.get_test_set()
    print("\nCreating full test set...\n")
    test_set_full = test.get_test_set(full=True)
    print("\nTest sets created.\n")

    neg_size = str(args.neg_ans_size)

    save_pickle(args.output_dir + "/train_set_" + neg_size + ".pickle", train_set)
    save_pickle(args.output_dir + "/valid_set_" + neg_size + ".pickle", valid_set)
    save_pickle(args.output_dir + "/test_set_" + neg_size + ".pickle", test_set)
    save_pickle(args.output_dir + "/test_set_full_" + neg_size + ".pickle", test_set_full)
