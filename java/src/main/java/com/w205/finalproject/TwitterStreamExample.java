package com.w205.finalproject;

/**
 * Need to work on this class to implement interrupt cycle for twitter streaming limits.
 */

import com.amazonaws.AmazonClientException;
import com.amazonaws.AmazonServiceException;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Region;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3Client;
import com.amazonaws.services.s3.model.CreateBucketRequest;
import com.amazonaws.services.s3.model.GetBucketLocationRequest;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.twitter.hbc.ClientBuilder;
import com.twitter.hbc.core.Client;
import com.twitter.hbc.core.Constants;
import com.twitter.hbc.core.endpoint.StatusesFilterEndpoint;
import com.twitter.hbc.core.processor.StringDelimitedProcessor;
import com.twitter.hbc.httpclient.auth.Authentication;
import com.twitter.hbc.httpclient.auth.OAuth1;
import twitter4j.*;
import twitter4j.conf.ConfigurationBuilder;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class TwitterStreamExample {

	  public static void run(String consumerKey, String consumerSecret, String token, String secret) throws InterruptedException, JSONException, TwitterException, IOException {
        ArrayList<String> trendList = TwitterStreamExample.getTrends(consumerKey, consumerSecret,  token,  secret);
	    BlockingQueue<String> queue = new LinkedBlockingQueue<String>(10000);
	    StatusesFilterEndpoint endpoint = new StatusesFilterEndpoint();
	    // add some track terms
	    //endpoint.trackTerms(Lists.newArrayList("twitterapi","#Paris"));
          endpoint.trackTerms(trendList);

	    Authentication auth = new OAuth1(consumerKey, consumerSecret, token, secret);

	    // Create a new BasicClient. By default gzip is enabled.
	    Client client = new ClientBuilder()
	            .hosts(Constants.STREAM_HOST)
	            .endpoint(endpoint)
	            .authentication(auth)
	            .processor(new StringDelimitedProcessor(queue))
	            .build();

	    // Establish a connection
	    client.connect();
        FileOutputStream out = new FileOutputStream("twitterTexts");
        //optional : Upload the tweetFile to S3
        //uploadtoS3("twitterTexts");

	    for (int msgRead = 0; msgRead < 1000; msgRead++) {
	      String msg = queue.take();
          //System.out.println(msg);
          JSONObject jsonObject = new JSONObject(msg);

          if(jsonObject.getString("text") != null){
            out.write(jsonObject.getString("text").getBytes());
          }
	    }
        out.close();
	    client.stop();

	  }

      public static void uploadtoS3(String fileName){
          String bucketName     = "TweetBucket";
          String keyName = "W205.pem";
          AmazonS3 s3client = new AmazonS3Client(new ProfileCredentialsProvider());
          s3client.setRegion(Region.getRegion(Regions.US_WEST_1));

          try {
              if(!(s3client.doesBucketExist(bucketName)))
              {
                  // Note that CreateBucketRequest does not specify region. So bucket is
                  // created in the region specified in the client.
                  s3client.createBucket(new CreateBucketRequest(
                          bucketName));
              }
              // Get location.
              String bucketLocation = s3client.getBucketLocation(new GetBucketLocationRequest(bucketName));
              System.out.println("bucket location = " + bucketLocation);
              File file = new File(fileName);

              s3client.putObject(new PutObjectRequest(
                      bucketName, keyName, file));


          } catch (AmazonServiceException ase) {
              System.out.println("Caught an AmazonServiceException, which " +
                      "means your request made it " +
                      "to Amazon S3, but was rejected with an error response" +
                      " for some reason.");
              System.out.println("Error Message:    " + ase.getMessage());
              System.out.println("HTTP Status Code: " + ase.getStatusCode());
              System.out.println("AWS Error Code:   " + ase.getErrorCode());
              System.out.println("Error Type:       " + ase.getErrorType());
              System.out.println("Request ID:       " + ase.getRequestId());
          } catch (AmazonClientException ace) {
              System.out.println("Caught an AmazonClientException, which " +
                      "means the client encountered " +
                      "an internal error while trying to " +
                      "communicate with S3, " +
                      "such as not being able to access the network.");
              System.out.println("Error Message: " + ace.getMessage());
          }
      }

      public static ArrayList<String> getTrends(String consumerKey, String consumerSecret, String token, String secret) throws TwitterException {
          ConfigurationBuilder cb = new ConfigurationBuilder();
          cb.setDebugEnabled(true)
                  .setOAuthConsumerKey(consumerKey)
                  .setOAuthConsumerSecret(consumerSecret)
                  .setOAuthAccessToken(token)
                  .setOAuthAccessTokenSecret(secret);
          Twitter twitter = new TwitterFactory(cb.build()).getInstance();
          ResponseList<Location> locations;
          locations = twitter.getAvailableTrends();
		  Trends trends = null;
          HashSet<String> trendsSet = new HashSet<String>();
          // Just get the first location
          Location location = locations.get(0);
          Trend[] trendArray = twitter.getPlaceTrends(location.getWoeid()).getTrends();
          for(Trend trend : trendArray){
              trendsSet.add(trend.getName());
          }
          /*for (Location location : locations) {
              Trend[] trendArray = twitter.getPlaceTrends(location.getWoeid()).getTrends();
              for(Trend trend : trendArray){
                  trendsSet.add(trend.getName());
              }
          }*/
          ArrayList<String> retList = new ArrayList<String>(trendsSet.size());
          for(String trend : trendsSet){
              retList.add(trend);
          }
          return retList;
      }
	  public static void main(String[] args) {
	    try {
          //ArrayList<String> trendList = TwitterStreamExample.getTrends(args[0], args[1], args[2], args[3]);
          TwitterStreamExample.run(args[0], args[1], args[2], args[3]);
	    }
        catch (InterruptedException e) {
	      System.out.println(e);
	    }
        catch (JSONException e) {
            e.printStackTrace();
        }
        catch (TwitterException e){
              e.printStackTrace();
          } catch (IOException e) {
            e.printStackTrace();
        }
      }
	}