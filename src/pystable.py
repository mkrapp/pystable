from ConfigParser import SafeConfigParser
import sys, os
from string import Template
import markdown2
import shutil
import glob
from dateutil.parser import parse
import calendar


def parse_config(posts_directory):
    global site_title, site_subtitle, site_author, \
           site_aboutme, site_info, site_syntax, \
	   site_url, site_output, site_theme, style_file
    parser = SafeConfigParser()
    config_file = posts_directory+'/site.config'
    parser.read(config_file)
    
    site_title    = parser.get("info","title")
    site_subtitle = parser.get("info","subtitle")
    site_author   = parser.get("info","author")
    site_aboutme  = parser.get("info","aboutme")
    site_info     = parser.get("info","info")
    site_syntax   = parser.get("config","syntax")
    site_url      = parser.get("config","url")
    site_output   = parser.get("config","output")
    site_theme    = parser.get("config","theme")
    style_file    = site_url+'/'+site_output+'/styles.css'

def parse_posts(posts_directory):
    files = glob.glob(posts_directory+'/*.txt')
    posts = []
    for p in files:
    	post = {}
        meta = []
	content = ""
	is_content = False
        f = open(p,'r')
	lines = f.readlines()
	for l in lines:
	    if is_content == False and l.strip():
	        meta.append(l.strip())
	    else:
	        is_content = True
	    if is_content:
	        content += l
	f.close()
	meta_dict = { k.lower().strip():v.strip() for k, v in dict(s.split(':',1) for s in meta).iteritems()}
	post["meta"] = meta_dict
	post["content"] = content[1:]
	# parse tags from meta
        post["tags"] = [tag.strip() for tag in meta_dict["tags"].split(',')]
	# parse date into year, month from meta
        date = parse(post['meta']['date'])
        post["year"] = date.year 
        post["month"] = date.month 
        post["date"] = date 
	posts.append(post)
    return posts

def parse_dates(posts):
    # parse dates of posts according to years and months
    date_list = [parse(p['meta']['date']) for p in posts]
    years = [parse(p['meta']['date']).year for p in posts]
    years = list(set(years))
    dates = []
    for year in years:
        d = {}
        d["year"] = year
	d["months"] = []
	for date in date_list:
	    if date.year == year: d["months"].append(date.month)
	dates.append(d)
    return dates

def parse_tags(posts):
    # parse tags
    tags = [p["tags"] for p in posts]
    all_tags = [item for sublist in tags for item in sublist]
    tags = list(set(all_tags))
    tags = [(tag,all_tags.count(tag)) for tag in tags]
    return tags

def generate_footer(theme):
    footer_tmpl = open(theme+'/footer.tmpl','r')
    lines = footer_tmpl.readlines()
    footer = ""
    disclaimer = 'Created by <a href="https://github.com/mkrapp/pystable">Pystable</a> \
                  (&copy; Mario Krapp, 2014)'
    for l in lines:
        s = Template(l)
	footer += s.safe_substitute(disclaimer=disclaimer)
    footer_tmpl.close()
    return footer

def generate_header(theme):
    header_tmpl = open(theme+'/header.tmpl','r')
    lines = header_tmpl.readlines()
    header = ""
    title = '<a href="'+site_url+'/'+site_output+'/'+'index.html">'+site_title+'</a>'
    for l in lines:
        s = Template(l)
	header += s.safe_substitute(title=title, subtitle=site_subtitle)
    header_tmpl.close()
    return header

def generate_sidebar(dates,tags,theme):
    sidebar_tmpl = open(theme+'/sidebar.tmpl','r')
    lines = sidebar_tmpl.readlines()
    # archive
    archive = "<ul>"
    for date in dates:
       archive += "<li>%.4d</li>" % date["year"]
       archive += "<ul>"
       for month in list(set(date["months"])):
           k = date["months"].count(month)
	   n = ""
	   if k>1: n = ' ('+str(k)+')'
           link = site_url+'/'+site_output+'/archive/%.4d/%.2d/index.html' % (date["year"],month)
           archive += '<li><a href="'+link+'">' + calendar.month_name[month] + n + '</a></li>'
       archive += "</ul>"
    archive += "</ul>"
    # tagcloud
    tagcloud = ""
    for tag in sorted(tags):
        tag_dir = site_output+'/tag/'+tag[0]
	tag_dir = tag_dir.replace(' ','%20')
	size = 40-25/tag[1]
        tagcloud += '<span style="font-size: %.2dpx"><a href=' % size +site_url+'/'+tag_dir+'/index.html>'+tag[0]+'</a></span>, '
    sidebar = ""
    for l in lines:
        s = Template(l)
	sidebar += s.safe_substitute(author=site_author, aboutme=site_aboutme, info=site_info,
	                             archive=archive, tagcloud=tagcloud[:-2])
    sidebar_tmpl.close()
    return sidebar

def process_content(content,syntax):
    if syntax == 'markdown':
        processed_content = markdown2.markdown(content,extras=["tables","fenced-code-blocks"])
    if syntax == 'text':
        processed_content = content 
    return processed_content.encode('utf-8')

def generate_main_page(posts,theme):
    # create the full main web page
    index_tmpl = open(theme+'/main.html.tmpl','r')
    lines = index_tmpl.readlines()
    index_html = open(site_output+'/index.html','w')
    main = ""
    for p in posts:
        post = generate_post_page(p,'themes/simple')
    	main += post["html_content"]
    for l in lines:
        s = Template(l)
	index_html.write(s.safe_substitute(style_file=style_file, title=site_title, header=header,
			                   sidebar=sidebar, footer=footer, main=main))
    index_html.close()
    index_tmpl.close()

def generate_tags_page(posts,tags,theme):
    # create a full web page for each tag
    for tag in tags:
        print 'create index.html for tag ' +tag[0]
        index_tmpl = open(theme+'/main.html.tmpl','r')
        lines = index_tmpl.readlines()
        index_html = open(site_output+'/tag/'+tag[0]+'/index.html','w')
        main = ""
        for p in posts:
	    if tag[0] in p["tags"]:
	        main += p["html_content"]
	        shutil.copy2(site_output+'/'+p["html_file"],site_output+'/tag/'+tag[0]+'/'+p["html_file"])
        for l in lines:
            s = Template(l)
            index_html.write(s.safe_substitute(style_file=style_file, header=header,title=site_title,
				               sidebar=sidebar, footer=footer, main=main))
        index_html.close()
        index_tmpl.close()

def generate_post(post,theme):
    # read meta and content of post
    meta = post["meta"]
    content = process_content(post["content"],site_syntax)
    # open post template
    post_tmpl = open(theme+'/post.tmpl','r')
    lines = post_tmpl.readlines()
    post_content = ""
    post_file = meta["title"].replace(" ","_")+'.html'
    tags = ""
    # create tags directory according to tag
    for t in post["tags"]:
        tag_dir = site_output+'/tag/'+t
        if not os.path.exists(tag_dir):
            os.makedirs(tag_dir)
        tags += '<a href='+site_url+'/'+tag_dir+'/index.html>'+t+'</a>, '
    # create archive directory according to year and month
    date_dir = site_output+'/archive/%.4d/%.2d' % (post["year"],post["month"])
    if not os.path.exists(date_dir):
        os.makedirs(date_dir)
    # create post content
    for l in lines:
        s = Template(l)
	post_content += s.safe_substitute(title=meta["title"], date=meta["date"],
					  content=content, url='./'+post_file,
					  tags=tags[:-2])
    post_tmpl.close()
    # append html file name and html-processed content to post
    post["html_content"] = post_content
    post["html_file"] = post_file
    return post

def generate_post_page(post,theme):
    # create a full web page for a single post
    post_tmpl = open(theme+'/main.html.tmpl','r')
    lines = post_tmpl.readlines()
    new_post = generate_post(post,theme)
    post_file = new_post["html_file"]
    html_content = new_post["html_content"]
    post_html = open(site_output+'/'+post_file,'w')
    for l in lines:
        s = Template(l)
	post_html.write(s.safe_substitute(style_file=style_file, title=site_title,
			                  header=header, sidebar=sidebar,
			                  footer=footer, main=html_content))

    post_html.close()
    post_tmpl.close()
    return new_post

def generate_archives_page(posts,dates,theme):
    # create a full web page for each month of each year (if posts are available for that date)
    for date in dates:
        months = list(set(date["months"]))
        for month in months:
            print 'create index.html for '+calendar.month_name[month]+' %.4d' % date["year"]
            index_tmpl = open(theme+'/main.html.tmpl','r')
            lines = index_tmpl.readlines()
            index_html = open(site_output+'/archive/%.4d/%.2d/index.html' % (date["year"],month),'w')
            main = ""
            for p in posts:
                if month == p["month"]:
                    main += p["html_content"]
                    shutil.copy2(site_output+'/'+p["html_file"],
		                 site_output+'/archive/%.4d/%.2d/' % (date["year"],month)+p["html_file"])
            for l in lines:
                s = Template(l)
                index_html.write(s.safe_substitute(style_file=style_file, header=header, sidebar=sidebar,
            			                   title=site_title, footer=footer, main=main))
            index_html.close()
            index_tmpl.close()

def create_blog(posts_dir):
    global sidebar, footer, header
    parse_config(posts_dir)
    theme = 'themes/'+site_theme
    if not os.path.exists(site_output):
        os.makedirs(site_output)
    # copy style.css
    shutil.copy2(theme+'/styles.css',site_output+'/styles.css')
    posts = parse_posts(posts_dir)
    # sort list of posts in descending order of their date 
    decorated_posts = [(dict_["date"], dict_) for dict_ in posts]
    decorated_posts.sort(reverse=True)
    posts = [dict_ for (key, dict_) in decorated_posts]
    tags = parse_tags(posts)
    dates = parse_dates(posts)
    header  = generate_header(theme)
    sidebar = generate_sidebar(dates,tags,theme)
    footer  = generate_footer(theme)
    generate_main_page(posts,theme)
    generate_tags_page(posts,tags,theme)
    generate_archives_page(posts,dates,theme)

create_blog(sys.argv[1])
