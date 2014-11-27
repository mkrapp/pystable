Pystable
========
Pystable is a static blog engine written in Python. Edit your posts as Markdown files, add some information, and Pystable converts everything into a complete static web page.

Requirements
============

You need to install `markdown2` to use Pystable:

```
pip install markdown2
```

Configuration
=============
In your posts directory you need a configuration file named `site.config` with the following content:
```
# This is the configuration file for our website
[info]
title = Blog Title
subtitle = Blog Subtitle
author = the Author
aboutme = Something about the author
info = Put some information about this site here 
[config]
theme = simple
syntax = markdown
url = http://www.example.com
output = ./
```
Configure this file to suit your needs.

Usage
=====

After adding your individual posts as text files (`*.txt`) like in this example
```
date: 2014/11/25
title: My first post
tags: posts, first

First of all bla blubb.
```
you can run Pystable on your posts directory
```
python src/pystable.py my_posts
```
Now, you just need to upload the output directory as defined `site.config`to your web page.

How it works
============

Apart from `markdown2` all packages are pure Python libraries.
