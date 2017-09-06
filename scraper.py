#!/usr/bin/python3

from splinter import Browser
import json
import sys

def login(browser, username, password):
    browser.visit('https://nya.boplats.se/login/')
    browser.find_by_id('username').fill(username)
    browser.fill('password', password)
    button = browser.find_by_name('login_button').click()

def extract_table_info(browser, link_item):
    url = link_item['href']
    raw_value = link_item.value
    parts = raw_value.split('\n')

    raw_html = link_item.outer_html
    has_applied = False
    if raw_html.find('alt="Du har ansökt"') > -1:
        has_applied = True

    apparment = dict(
        url=url,
        rent=parts[0],
        area=parts[1],
        address=parts[2],
        level=parts[3],
        size=parts[4],
        nbr_rooms=parts[5],
        access=dict(date=parts[6], year=parts[7]),
        added=dict(date=parts[8], year=parts[9]),
        has_applied=has_applied,
        extra=(','.join(parts[9:]))
    )

    return apparment

def add_details(browser, apparment):
        browser.visit(apparment['url'])
        google_maps_urls = browser.find_link_by_partial_href('http://maps.google.com/maps')
        if google_maps_urls:
            apparment['google_maps_url'] = google_maps_urls[0]['href']

        can_apply = False
        can_apply_button = browser.find_by_id('apply')

        if can_apply_button:
            o = can_apply_button[0]
            if o.outer_html.find('disabled=""') == -1:
                can_apply = True

        can_revoke_application = browser.find_by_id('revokeapplication')

        apply_status = "Cannot"
        if can_apply:
            apply_status = "Can"
        elif can_revoke_application:
            apply_status = "Applied"

        apparment['apply_status'] = apply_status

        return apparment


if __name__ == '__main__':
    appartments = []

    browser = Browser('chrome', headless=True)
    login(browser, sys.argv[1], sys.argv[2])

    browser.click_link_by_text('Lgh')
    links = browser.find_link_by_partial_href('https://nya.boplats.se/objekt/1hand/')

    for l in links:
        appartments.append(extract_table_info(browser, l))

    for a in appartments:
        add_details(browser, a)

    print(json.dumps(appartments))
