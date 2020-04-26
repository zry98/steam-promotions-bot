#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
from typing import List, Union

STEAMDB_PROMOTIONS_URL: str = 'https://steamdb.info/upcoming/?free'


def get_steamdb_promotions_page_html() -> Union[BeautifulSoup, str]:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Cache-Control': 'no-cache'
    }
    resp = requests.get(STEAMDB_PROMOTIONS_URL, headers=headers)
    if resp.status_code == 403 and resp.text and 'Cloudflare' in resp.text:
        return '[ERROR] Request rejected by Cloudflare'
    elif resp.status_code == 200 and resp.text and 'Cloudflare' not in resp.text:
        return BeautifulSoup(resp.text, 'html.parser')
    else:
        return '[ERROR] Unknown error occurred requesting SteamDB.info Promotions page'


def get_steam_app_details_by_appid(appid: str) -> Union[dict, str]:
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Cache-Control': 'no-cache'
    }
    resp = requests.get('https://store.steampowered.com/api/appdetails/?appids=' + appid, headers=headers)
    if resp.status_code == 200 and resp.json():
        json = resp.json()
        if json[appid] and json[appid]['success'] == True and json[appid]['data']:
            return json[appid]['data']
    else:
        return '[ERROR] Unknown error occurred requesting Steam Store API'


def get_freebies_list() -> Union[List[dict], str]:
    page_html = get_steamdb_promotions_page_html()
    currently_live_promotions_table = page_html.find('div', {'id': 'live-promotions'}) \
        .find_next('table', {'class': 'table-products table-responsive-flex table-hover text-left table-sortable'})
    if not currently_live_promotions_table:
        return '[ERROR] Unknown HTML parsing error, can\'t find the Currently Live Promotions table'

    freebies = []
    for promotion in currently_live_promotions_table.find_all('tr', {'class': 'app'}):
        if infinity_svg := promotion.find('svg', {'class': 'octicon octicon-infinity'}):
            if type_text := infinity_svg.find_next_sibling('b'):
                if type_text.text == 'Keep':
                    # okay, this is a true keepable freebie
                    freebie = {
                        'appid': promotion.attrs['data-appid']
                    }
                    app_detail = get_steam_app_details_by_appid(freebie['appid'])
                    if isinstance(app_detail, str):
                        return app_detail

                    freebie['name'] = app_detail['name']
                    if is_dlc := app_detail['type'] == 'dlc':
                        freebie['is_dlc'] = is_dlc
                        freebie['fullgame_appid'] = app_detail['fullgame']['appid']
                        freebie['fullgame_name'] = app_detail['fullgame']['name']

                    freebies.append(freebie)

    return freebies


def main():
    freebies = get_freebies_list()
    if isinstance(freebies, str):
        return freebies

    for freebie in freebies:
        line = freebie['appid'] + ' '
        if 'is_dlc' in freebie and freebie['is_dlc']:
            line += '[DLC of {} ({})] '.format(freebie['fullgame_name'], freebie['fullgame_appid'])
        line += freebie['name']
        print(line)
        print('-' * 32)


if __name__ == '__main__':
    main()
