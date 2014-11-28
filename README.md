Pystable
========
Pystable is a static blog engine written in Python. Edit your posts as Markdown files, add some information, and Pystable converts everything into a complete static web page. An example web page can be found [here](https://www.liselotte.duckdns.org/pystable_test/)

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

The config file
---------------
To parse the configuration file we use `SafeConfigParser` provided by the `ConfigParser` package.
``` python
# Example
parser = SafeConfigParser()
parser.read('site.config')
site_title = parser.get("info","title")
```

The post file
-------------
In each text file that contains a post has the form
```
+------------------+
| meta information |
|                  | <- blank line
|     content      |
+------------------+
```
where the content is separated by a blank line from the meta information (title, date, and tags). Meta information is read into a Python dictionary:
``` python
meta_dict = { k.lower().strip():v.strip() for k, v in dict(s.split(':',1) for s in meta).iteritems()}
```
A post is then a Python dictionary with keys __meta__ and __content__. We furthermore parse for __tags__ and __date__ (__year__ and __month__) which we need later on for _archive_ and _tag cloud_, part of the web page's sidebar.

Component layout
----------------
For our layout we define some HTML construction blocks: `header.tmpl`, `post.tmpl`, `sidebar.tmpl`, and `footer.tmpl`. From these blocks we create the elements of the full web page using `main.html.tmpl` and the parsed content of the individual posts provided. For parsing we use `Template` from the `string` package like this:
``` python
header_tmpl = open(theme+'/header.tmpl','r')
lines = header_tmpl.readlines()
header = ""
title = '<a href="url/to/index.html">'+site_title+'</a>'
for l in lines:
    s = Template(l)
    header += s.safe_substitute(title=title, subtitle=site_subtitle)
header_tmpl.close()
```

Structure of a pystable-generate web page
--------------------------------------------
```
+---------------------------------------+\
|            main.html.tmpl             |                 +-----------+
| +-----------------------------------+ |  \              |           |
| |              header.tmpl          | |                 |  archive  |
| +-----------------------------------+ |    \       +----------+     |
| +------------------+ +--------------+ |            |          |     |
| | +-post 1-------+ | |              | |      \     |   tags   |     |-----+
| | |   post.tmpl  | | | sidebar.tmpl | |      +-----------+    |-----+     |
| | +--------------+ | |              | |      |           |    |  | post 1 |--+
| | +-post 2-------+ | |              | |      | main page |    |  |        |  |
| | |   post.tmpl  | | |              | |      |           |----+  |        |  |--+
| | +--------------+ | |              | |      |           |       |        |  |  |
| |    ...           | |              | |      |           |       +--------+  |  |
| | +-post N-------+ | |              | |      +-----------+           |       |  |
| | |   post.tmpl  | | |              | |      /                       +-------+  |
| | +--------------+ | |              | |                                |        |
| +------------------+ +--------------+ |    /                           +--------+
| +-----------------------------------+ |   
| |            footer.tmpl            | |  /
| +-----------------------------------+ | 
+---------------------------------------+/
```
