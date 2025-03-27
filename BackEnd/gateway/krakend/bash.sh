#!/bin/bash


krakend run \
  -c aggregator.json \
  -c krakend_authentication.json \
  -c krakend_events.json \
  -c krakend_forum_posts.json \
  -c krakend_forum_QA.json \
  -c krakend_news.json \
  -c krakend_profiles.json \
  -c krakend_search.json


