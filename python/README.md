Here's how to start and tinker with #douchetag.

*NB*: when you've completed this run-through,
the account tied to the twitter creds you
enter will have a newly blocked twitter
users.  You'll likely want to use either
a throw-away account, or you'll want
to immediately clean up that account's
block list.

# Pre-conditions

0. The project repo must be cloned.
1. `zookeeper` and `kafka` must be running.
2. The `SPARK_HOME` and `KAFKA_HOME` envariables must be set appropriately.
3. python 2.7 must be installed.
4. Twitter app credentials must be known.

# To run

You'll need to have 5 windows open:

4. will run various command line utilities and interactive frontends
2. will run the spark streaming job
1. will run the classifier
3. will run the tweet injector
5. will run the blocker

In each of them, do

    $ cd .../W205-Project/python
    $ export KAFKA_HOME=wherever-kafka-lives
    $ export SPARK_HOME=wherever-spark-lives

with the appropriate substitutions made.

When starting the apps, all endpoints will default to *localhost:the-right-port*

## Setup

In the first window, you'll first do some installation and setup:

    $ sudo sh install           # installs various python modules via pip
    $ ./setup                   # creates kafka topics
    $ cp creds.template creds.py
    $ vi creds.py               # put in the twitter API credentials
                                # NB: when you run the blocker,
                                # this user's block list will grow

We'll return to this window later.

## Start the Spark streaming job in a window

If Zookeeper and Kafka are running locally...

    $ ./run-spark

...or this if they are on remote systems

    $ ./run-spark --broker <kafka broker endpoint>

The rest of this doc assumes all systems/daemons are running locally.
All commands take some form of `--help` or `-h` to see arguments
to point them at remote endpoints.

## Start the tweet classifier

    $ python classifer/server.py        # binds to all interfaces on port 6666

## Start the tweet injector

    $ python frontends/tweet-sucker.py

Once the injector is running, you'll see interesting output in all the other windows.

## Finally, start the blocker

    $ python backends/block.py

## To add an harasser's tweets to the model

From the first window

    $ python frontends/add-harasser.py BerkeleyData

This will add all of the datascience@berkeley tweets to the corpus of harassing tweets.
Once this corpus is loaded, tweets similar to it will be marked as harassing
and added to the `creds.py` user's block list.

# To test the model interactively

Stop the classifer via ctl-C, then restart it:

    $ python classifer/server.py

The classifier has no history across process invocations,
so restarting it will erase its corpus.

Now, inject a single user's tweets into the tweet stream:

    $ python frontends/add-harasser.py closemindedjerk --topic tweets

Note the `--topic` switch.  That causes `add-harasser` to put @closemindedjerk's
tweets into the kafka topic from which the Spark streaming job expects to
receive tweets to check for harassment.

Check the output in the 2nd window. 
You'll see that none of closemindedjerk's tweets were
judged to be harassing.

Now, add @closemindedjerk's tweets as harassment.
In the first window, do:

    $ python frontends/add-harasser.py closemindedjerk

Then, re-check to see that @closemindedjerk's tweets are now considered harassment:

    $ python frontends/add-harasser.py closemindedjerk --topic tweets

Finally, go check the `creds.py` user's twitter account.
@closemindedjerk should now be blocked.
