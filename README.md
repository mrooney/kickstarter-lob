kickstarter-lob
===============

easily send physical postcards to your Kickstarter backers with Lob.com

Usage
=====

1. Sign up for an account at lob.com.
1. `pip install -r requirements.txt`
1. `cp config_example.json config.json`
1. Fill in your details in config.json, using the test or production API key from lob as desired.
1. `python kslob.py your-kickstarter-backer-report.csv`

You can safely run kslob.py multiple times with updated exports; it will only send one
postcard per address (per Lob.com API key).

How It Works
============

kickstarter-lob uses Lob.com to verify addresses and send physical
postcards.

Given a CSV export from Kickstarter, running kslob.py will:

1. Verify all addresses of backers, letting you know which ones failed
   verification.
1. Get a list of any addresses that were already mailed postcards.
1. Let you know how many addresses have and have not received postcards.
1. Ask if you'd like to send postcards to any verified backers who have
   not yet been sent them.
