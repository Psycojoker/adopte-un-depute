# Introduction [![Build Status](https://secure.travis-ci.org/Psycojoker/adopte-un-depute.png?branch=master)](http://travis-ci.org/Psycojoker/adopte-un-depute)

Prototype of web that aim to encourage ppl to adopt a french deputy and to educate him on Internet and Free Software related subjects.

# Installation

You'll need to be able to build some C dependacies, on debian you'll need the packages:

    libxml2-dev libxslt1-dev python-dev

You need mongodb, python and virtualenv

    virtualenv --no-site-packages --distribute ve
    source ve/bin/activate # here you enter the virtualenv
    pip install -r requirements.txt
    python update_db.py

And to run the server:

    python main.py

To quit a virtualenv:

    deactivate
