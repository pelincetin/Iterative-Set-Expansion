## Team Members:

- Pelin Cetin, pc2807
- Justin Andrew Zwick, jaz2130

## How to run our program: 

**install the necessary python packages**

pip3 install google-api-python-client
pip3 install stanfordnlp
pip3 install sortedcontainers
pip3 install beautifulsoup4
sudo apt-get update

** get stanfordnlp **

wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip
sudo apt-get install unzip
unzip stanford-corenlp-full-2018-10-05.zip

** Install Java 13 **

wget https://download.java.net/java/GA/jdk13.0.2/d4173c853231432d94f001e99d882ca7/8/GPL/openjdk-13.0.2_linux-x64_bin.tar.gz
tar -xvzf openjdk-13.0.2_linux-x64_bin.tar.gz

** Set PATH and JAVA_HOME variables so that the java command is recognized **

export PATH=/home/⟨your_UNI⟩/jdk-13.0.2/bin:$PATH
export JAVA_HOME=/home/⟨your_UNI⟩/jdk-13.0.2 

** set classpath for stanfordnlp **
export CORENLP_HOME=/home/⟨your_UNI⟩/stanford-corenlp-full-2018-10-05 

** finally, you can run the project. **
python3 project.py <Google API Key> <Google Search Engine ID> <relation> <confidence threshold> <seed query> <min number of tuples requested in output>


** Clear description of our program **

After having extracted the JSON API Key, Engine ID, the integer for the relation, extraction confidence threshold, seed query and the number of tuples from the command line argument, we created a while loop that will run as long as we don't reach k number of tuples, which we put in a set called X. 

As there are two pipelines, we set one of the endpoints to 9001 and the other to 9001. After getting the results back from the google API, we take the link and feed that to the extract method in the extract_plain_text.py file. We have decided to use bs4 for this part of the project. We get all the content of the HTML file and extract the text inside tags by using find_all(text=True). Then we loop over the text to exclude all other tags of the HTML file, which is in a list called black_list. If the number of characters is bigger than 20000, then we only get the first 20000 characters. Then we feed this output to the first pipeline and annotate. Afterwards, we call the select_sentences method, which takes the relation integer from the user and tries to find the tokens in accordance with the relation. For example, if relation == 1, then we're looking at schools_attended and we should try to find the ner's PERSON and ORGANIZATION. Afterwards we loop over the sentences in the selected_sentences list and feed that to the second pipeline and annotate. Then we have another two loops until we reach to the kbp_triple. For each relation if statement, we've created a tuple with the subject and the object of the kbp_triple if the confidence is higher than the threshold the user set. Here, we put all the subject.object tuples in X, which is the set of all extracted relations, and their confidence float number in conf, a dictionary to reduce the time for looking which tuple has a higher confidence to O(1). 

We noticed in the output provided by the professor, he had sentences such as "The same relation is already present but with a lower confidence. Just updating the confident value." Or "The same relation is already present with higher (or equal) confidence. Ignoring this." So, in order to be able to write these sentences to the output, we created a variable called status, which would allow us to know the status of the tuple, whether it has a higher confidence than another tuple or lower and so on. We send the tuple of a kbpTriple Relation, the sentence and the status to the print_relation method to take care of this. 

After we break from the for loop, we create a SortedSet called sorted_x, which we populate by looping through the conf dictionary, which only contains the tuples of higher confidence. Now that we''ve expected all sentences for all the URLs, we print all the relations at the end of the program. If we have at least k tuples, then we're done with the program. If not, we augment the seed query concatenating the attribute values together of tuple y, which we get from the sorted_x set. 


