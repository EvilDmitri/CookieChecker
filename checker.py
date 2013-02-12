# -*- coding: utf-8 -*-

from grab.spider import Spider, Task
from grab import Grab

import logging
from grab.tools.logs import default_logging
default_logging(level=logging.ERROR)

THREADS = 1
URLS_FILE = 'urls.txt'
FOUND_FILE = 'found.txt'
NOT_FOUND_FILE = 'not_found.txt'

class CookieSpider(Spider):

    errors = []

    def task_generator(self):
        self.errors = prepare_errors()

        with open(URLS_FILE) as f:
            for url in f:
                if url.strip():
                    grab = Grab()
                    grab.setup(url=url)
                    print "Start checking the - ", url
                    yield Task('initial', url=url, grab=grab)


    def task_initial(self, grab, task):
        cookies = grab.response.cookies

        for cookie in cookies.iterkeys():
            new_cookies = cookies.copy()
            new_cookies[cookie] += "'"
            grab = Grab()
            grab.setup(cookies=new_cookies)
            grab.setup(url=task.url)
            self.print_changed_values(task.url, cookies, new_cookies)   # working statics
            self.add_task(Task('check', url=task.url, grab=grab, old_cookies=cookies, new_cookies=new_cookies))


    def task_check(self, grab, task):
        not_found = ""
        raw_text = grab.response.body      #grab.xpath_text('//*').lower()
        for error in self.errors:
            if error in raw_text:
                self.write_file(FOUND_FILE, task.url+'-'+task.new_cookies + error)
            else:
               not_found = task.url
        if not_found:
            self.write_file(NOT_FOUND_FILE, task.url)

    def write_file(self, file, url):
        with open(file, 'a') as f:
            f.write(url+'\n')


    def print_changed_values(self, url, cookies, new_cookies):
        print '-------------'
        print url
        print 'Old cookies:'
        print cookies
        print 'New cookies:'
        print new_cookies


def prepare_errors():
    errors = []
    with open('errors.txt') as f:
        for error in f:
            errors.append(error)
    return errors


def main():

    bot = CookieSpider(thread_number=THREADS,network_try_limit=10)

    try:
        bot.run()
    except KeyboardInterrupt:
        pass

    print 'All done'
    print bot.render_stats()

if __name__ == '__main__':
    print 'Start working'
    main()
