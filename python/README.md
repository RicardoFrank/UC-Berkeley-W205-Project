# Pre-conditions

1. `zookeeper` and `kafka` must be running.
2. The `SPARK_HOME` and `KAFKA_HOME` envariables must be set appropriately
3. python 2.7 must be installed

# To run

You'll need to have 4 windows open:

4. will run various command line utilities
1. will run the classifier
2. will run the spark job
3. will run the tweet injector

In each of them, do

    $ cd .../W205-Project/python

When starting the apps, all endpoints will default to *localhost:the-right-port*

## Setup

In the first window, you'll first do some installation and setup:

    $ sudo sh install		# installs various python modules via pip
    $ ./setup			# creates kafka topics

We'll return to this window later

## Run the classifier

    $ python classifer/server.py	# binds to localhost:6666

## Start the Spark streaming job in a window

If ZK and Kafka are running locally...

    $ ./run-spark

...or this if they are on remote systems

    $ ./run-spark --broker <kafka broker endpoint>

The demo assumes all systems/daemons are running locally.

## Run the tweet injector in the last window

    $ python frontends/tweet-sucker.py

Once the injector is running, you'll see output from all the other windows.

## To add an harasser's tweets to the model

From the first window

    $ python frontends/add-harasser.py BerkeleyData

This will add all of the datascience@berkeley tweets to the corpus of harassing tweets.
Once this corpus is loaded, tweets similar to it will be marked as harassing
and added to our block list.

# To test the model interactively

Stop both the tweet injector and the classifer via ctl-C.

Then, restart the classifier in the 

    $ python classifer/server.py

The classifier has no history across process invocations,
so this will erase its corpus.

Now, inject a single user's tweets into the tweet stream:

    $ python frontends/add-harasser.py closemindedjerk --topic tweets

Note the `--topic` switch.  That causes add-harasser to put @closemindedjerk's
tweets into the kafka use in which the Spark streaming jobs expects to
receive tweets to check for harassment.

Check the output in the 3rd window.  You'll see lines showing none of the tweets as being harassment.

Now, add @closemindedjerk's tweets as harassment:

    $ python frontends/add-harasser.py closemindedjerk

Then, re-check to see that @closemindedjerk's tweets are now considered harassment:

    $ python frontends/add-harasser.py closemindedjerk --topic tweets
