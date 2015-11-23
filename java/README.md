# java/scala-stream
Twitter-Kafka Data Pipeline

# Requirements :

Apache Kafka 0.8
Twitter Developer account ( for API Key, Secret etc.)
Apache Zookeeper ( required for Kafka)
Oracle JDK 1.7 (64 bit )

#Build Environment :
Eclipse / Intellij
Apache Maven 2/3

KAFKA_HOME environment variable is set and points to the kafka installation

# How to generate Twitter API Keys using Developer Account ?
1. Go to https://dev.twitter.com/apps/new and log in, if necessary
2. Enter your Application Name, Description and your website address. You can leave the callback URL empty.
3. Accept the TOS.
4. Submit the form by clicking the Create your Twitter Application
5. Copy the consumer key (API key) and consumer secret from the screen into your application.
6. After creating your Twitter Application, you have to give the access to your Twitter Account to use this Application. To do this, click the Create my Access Token.
7. Now you will have Consumer Key, Consumer Secret, Acess token, Access Token Secret to be used in streaming API calls.

# Steps to run

1. Start Zookeeper server in Kafka using following script in your kafka installation folder  –
   $KAFKA_HOME/bin/zookeeper-server-start.sh config/zookeeper.properties &
   
   verify if it is running on default port 2181 using
   netstat -anlp | grep 2181

2. Start Kafka server using following script
   $KAFKA_HOME/bin/kafka-server-start.sh config/server.properties  &
   and, verify if it is running on default port 9092
   netstat -anlp | grep 9092
   
3. Now, when we are all set with Kafka running ready to accept messages on any dynamically created topic ( default setting ), 
   we will create a Kafka Producer , which makes use of hbc client API to get twitter stream for tracking terms and puts on 
   topic named as “twitter-topic” .
   
4. Running TwitterKafkaProducer steps:
   i. cd java
   ii. mvn clean build
   iii. 

  
# Verify the Topic and Messages
 
1. Check if topic is there using –
   $KAFKA_HOME/bin/kafka-list-topic.sh --zookeeper localhost:2181
  
2. Consume messages on topic twitter-topic to verify the incoming message stream.
   $KAFKA_HOME/bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic test --from-beginning