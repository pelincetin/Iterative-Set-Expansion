from googleapiclient.discovery import build
from extract_plain_text import extract
import sys
from sortedcontainers import SortedSet
from stanfordnlp.server import CoreNLPClient


def main():
    google_api_key = sys.argv[1]
    google_engine_id = sys.argv[2]

    # integer indicating the relation to extract
    # 1 is for Schools_Attended
    # 2 is for Work_For
    # 3 is for Live_In
    # 4 is for Top_Member_Employees
    r = int(sys.argv[3])
    # extraction confidence threshold
    t = float(sys.argv[4])
    # seed query
    q = sys.argv[5]
    # the number of tuples that we request in the output
    k = int(sys.argv[6])

    if r == 1:
        str_r = "per:schools_attended"
    elif r == 2:
        str_r = "per:employee_or_member_of"
    elif r == 3:
        str_r = "per:cities_of_residence"
    elif r == 4:
        str_r = "org:top_members_employees"

    print("____")
    print("Parameters")
    print("Client key      = " + google_api_key)
    print("Engine key      = " + google_engine_id)
    print("Relation        = " + str_r)
    print("Threshold       = " + str(t))
    print("Query           = " + q)
    print("# of Tuples     = " + str(k))
    print("Loading necessary libraries; This should take a minute or so ...")

    service = build("customsearch", "v1", developerKey=google_api_key)

    X = set()
    conf = dict()
    tuples_for_query_augment = set()
    iteration = 0

    while True:
        with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner'], timeout=300000, memory='4G',
                           endpoint="http://localhost:9000", be_quiet=True) as pipeline_ner:
            with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse', 'coref', 'kbp'],
                               timeout=300000, memory='4G', endpoint="http://localhost:9001",
                               be_quiet=True) as pipeline_kbp:

                # send query to gcse api and get results
                results = service.cse().list(q=q,
                                             cx=google_engine_id,
                                             ).execute()

                print("=========== Iteration: " + str(iteration) + " - Query: " + q + " ===========")
                URL_index = 1
                for item in results['items']:
                    print("URL (" + str(URL_index) + " / " + str(len(results['items'])) + "): " + item['link'])
                    extracted_text = extract(item['link'])
                    # first, annotate with NER to construct sentences
                    ann_ner = pipeline_ner.annotate(extracted_text)
                    # should not run depparse over sentences that do not contain named entities of the right type for the relation of interest
                    selected_sentences = select_sentences(r, ann_ner)
                    for sentence in selected_sentences:
                        sentence_ann_doc = pipeline_kbp.annotate(sentence)
                        for kbp_sentence in sentence_ann_doc.sentence:
                            for kbp_triple in kbp_sentence.kbpTriple:
                                status = "add"
                                if r == 1:
                                    if kbp_triple.relation == "per:schools_attended" and kbp_triple.confidence >= t:
                                        tup = (kbp_triple.subject, kbp_triple.object)
                                        if tup in X:
                                            if conf[tup] < kbp_triple.confidence:
                                                status = "update"
                                                conf[tup] = kbp_triple.confidence
                                            else:
                                                status = "higher"
                                        else:
                                            X.add(tup)
                                            conf[tup] = kbp_triple.confidence
                                        print_relation(kbp_triple, sentence, status)
                                    elif kbp_triple.relation == "per:schools_attended" and kbp_triple.confidence < t:
                                        status = "lower"
                                        print_relation(kbp_triple, sentence, status)
                                elif r == 2:
                                    if kbp_triple.relation == "per:employee_or_member_of" and kbp_triple.confidence >= t:
                                        tup = (kbp_triple.subject, kbp_triple.object)
                                        if tup in X:
                                            if conf[tup] < kbp_triple.confidence:
                                                status = "update"
                                                conf[tup] = kbp_triple.confidence
                                            else:
                                                status = "higher"
                                        else:
                                            X.add(tup)
                                            conf[tup] = kbp_triple.confidence
                                        print_relation(kbp_triple, sentence, status)
                                    elif kbp_triple.relation == "per:employee_or_member_of" and kbp_triple.confidence < t:
                                        status = "lower"
                                        print_relation(kbp_triple, sentence, status)
                                elif r == 3:
                                    if kbp_triple.relation == "per:cities_of_residence" and kbp_triple.confidence >= t:
                                        tup = (kbp_triple.subject, kbp_triple.object)
                                        if tup in X:
                                            if conf[tup] < kbp_triple.confidence:
                                                status = "update"
                                                conf[tup] = kbp_triple.confidence
                                            else:
                                                status = "higher"
                                        else:
                                            X.add(tup)
                                            conf[tup] = kbp_triple.confidence
                                        print_relation(kbp_triple, sentence, status)
                                    elif kbp_triple.relation == "per:cities_of_residence" and kbp_triple.confidence < t:
                                        status = "lower"
                                        print_relation(kbp_triple, sentence, status)
                                        # print(
                                        #   f"\t Confidence: {kbp_triple.confidence};\t Subject: {kbp_triple.subject};\t Relation: {kbp_triple.relation}; Object: {kbp_triple.object}")
                                elif r == 4:
                                    if kbp_triple.relation == "org:top_members_employees" and kbp_triple.confidence >= t:
                                        tup = (kbp_triple.subject, kbp_triple.object)
                                        if tup in X:
                                            if conf[tup] < kbp_triple.confidence:
                                                status = "update"
                                                conf[tup] = kbp_triple.confidence
                                            else:
                                                status = "higher"
                                        else:
                                            X.add(tup)
                                            conf[tup] = kbp_triple.confidence
                                        print_relation(kbp_triple, sentence, status)
                                    elif kbp_triple.relation == "org:top_members_employees" and kbp_triple.confidence < t:
                                        status = "lower"
                                        print_relation(kbp_triple, sentence, status)
                                        # print(
                                        #   f"\t Confidence: {kbp_triple.confidence};\t Subject: {kbp_triple.subject};\t Relation: {kbp_triple.relation}; Object: {kbp_triple.object}")

                    URL_index += 1
                iteration += 1

                sorted_x = SortedSet()
                for key, v in conf.items():
                    sorted_x.add((v,) + key)

                # the reference implementation prints the top relations at the end of every iteration
                print("================== ALL RELATIONS (" + str(len(sorted_x)) + ") =================")
                for i in range(len(sorted_x) - 1, -1, -1):
                    print("Confidence: {} 	 | Subject: {} 	 | Object: {}".format(sorted_x[i][0], sorted_x[i][1],
                                                                                       sorted_x[i][2]))

                # if there are at least k tuples,
                # then we're done!
                if len(X) >= k:
                    break
                # otherwise, select a tuple from X
                # 1. has not been used for querying yet
                # 2. as an extraction confidence that is highest among the tuples in X that have not yet been used for querying
                else:
                    for i in range(len(sorted_x) - 1, -1, -1):
                        if (sorted_x[i][1], sorted_x[i][2]) not in tuples_for_query_augment:
                            tuples_for_query_augment.add((sorted_x[i][1], sorted_x[i][2]))
                            q = sorted_x[i][1] + " " + sorted_x[i][2]


def select_sentences(relation, doc):
    selected_sentences = []  # list of sentences which contain the entities needed
    for sentence in doc.sentence:
        if relation == 1:
            if any(men.ner == 'PERSON' for men in sentence.token) and any(
                    men.ner == 'ORGANIZATION' for men in sentence.token):
                selected_sentences.append(' '.join([t.word for t in sentence.token]))
        elif relation == 2:
            if any(men.ner == 'PERSON' for men in sentence.token) and any(
                    men.ner == 'ORGANIZATION' for men in sentence.token):
                selected_sentences.append(' '.join([t.word for t in sentence.token]))
        elif relation == 3:
            if any(men.ner == 'PERSON' for men in sentence.token) and (
                    any(men.ner == 'LOCATION' for men in sentence.token) or
                    any(men.ner == 'CITY' for men in sentence.token) or
                    any(men.ner == 'STATE_OR_PROVINCE' for men in sentence.token) or
                    any(men.ner == 'COUNTRY' for men in sentence.token)
            ):
                selected_sentences.append(' '.join([t.word for t in sentence.tokens]))

        elif relation == 4:
            if any(men.ner == 'PERSON' for men in sentence.token) and any(
                    men.ner == 'ORGANIZATION' for men in sentence.token):
                selected_sentences.append(' '.join([t.word for t in sentence.tokens]))
    return selected_sentences


def print_relation(kbp_triple, sentence, status):
    print("=== Extracted Relation ===")
    transcript = ""
    transcript += "Sentence: "
    transcript += sentence  # sentence
    transcript += "\n"
    transcript += "Confidence: "
    transcript += str(kbp_triple.confidence)
    transcript += ";"
    transcript += "Subject: "
    transcript += kbp_triple.subject
    transcript += ";"
    transcript += "Object: "
    transcript += kbp_triple.object
    transcript += ";\n"
    if status == "add":
        transcript += "Adding to set of extracted relations"
    elif status == "update":
        transcript += "The same relation is already present but with a lower confidence. Just updating the confident value."
    elif status == "higher":
        transcript += "The same relation is already present with higher (or equal) confidence. Ignoring this."
    elif status == "lower":
        transcript += "Confidence is lower than threshold confidence. Ignoring this."
    transcript += "\n=========="
    print(transcript)


if __name__ == '__main__':
    main()
