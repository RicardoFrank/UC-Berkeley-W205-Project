# To install

$ sudo sh install		# installs various python modules via pip

# To run the first time

All endpoints will default to localhost:<the right port>

$ export SPARK_HOME=
$ export KAFKA_HOME=
$ <start kafka and zookeeper>
$ ./run --zookeeper <zk endpoint> --broker <kafka broker endpoint>

# To run subsequent times

$ ./run-spark <zk endpoint>

# To start pulling in tweets

$ python frontends/tweet-sucker.py --broker go-go-go.local:9092

# To add an harassers tweets to the model

$ python frontends/add-harasser.py --broker go-go-go.local:9092 closemindedjerk

# To test the model interactively

$ <kill tweet-sucker if it's running>
\# Make @closemindedjerk's tweets appear in tweet stream
$ python frontends/add-harasser.py --broker go-go-go.local:9092 closemindedjerk --topic tweets
# Add @closemindedjerk as an harasser
$ python frontends/add-harasser.py --broker go-go-go.local:9092 closemindedjerk
# Test again, this time expecting that tweets will be classified as harassment
$ python frontends/add-harasser.py --broker go-go-go.local:9092 closemindedjerk --topic tweets
