# -*- coding: utf-8 -*-

import re

from grab.spider import Spider, Task
from grab import Grab

import logging
logging.basicConfig(level=logging.DEBUG)

threads = 1
urls_file = 'urls.txt'
found_file = 'found.txt'
not_found_file = 'not_found.txt'

class CookieSpider(Spider):

    errors = []

    def task_generator(self):
        self.errors = prepare_errors()

        with open(urls_file) as f:
            for url in f:
                if url:
                    grab = Grab()
                    grab.setup(url=str(url).rstrip('\n'))
                    print "Test in progress for the - ", url
                    yield Task('initial', url=str(url), grab=grab)


    def task_initial(self, grab, task):
        cookies = grab.response.cookies

        for cookie in cookies.iterkeys():
            new_cookies = cookies.copy()
            new_cookies[cookie] += "'"
            grab = Grab()
            grab.setup(cookies=new_cookies)
            grab.setup(url=task.url)
            print cookies, new_cookies
            self.add_task(Task('check', url=task.url, grab=grab, old_cookies=cookies, new_cookies=new_cookies))


    def task_check(self, grab, task):
        not_found = False
        raw_text = grab.xpath_text('//*')
        for error in self.errors:
            if re.findall(error, raw_text):
                self.write_file(found_file, task.url+'-'+task.new_cookies)
            else:
                if not_found:
                    pass
                else:
                    not_found = task.url
        if not_found:
            self.write_file(not_found_file, task.url)

    def write_file(self, file, url):
        with open(file, 'a') as f:
            f.write(url+'\n')


def prepare_errors():
    errors = []
    with open('errors.txt') as f:
        for error in f:
            errors.append(re.compile(error))
    return errors


def main():

    bot = CookieSpider(thread_number=threads,network_try_limit=10)

    try: bot.run()
    except KeyboardInterrupt: pass

    print 'All done'
    print bot.render_stats()

if __name__ == '__main__':
    print 'Start working'
    main()