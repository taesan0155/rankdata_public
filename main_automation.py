# -*- coding: utf-8 -*-
import requests
import pandas as pd
import datetime as dt
import time
import base64
import hmac
import hashlib
import os
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

import json
import pathlib

CONFIG_PATH = pathlib.Path(__file__).parent / ".nshopping_config.json"
def load_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}
_local_cfg = load_config()

def get_secret(key, default=""):
    return os.getenv(key) or _local_cfg.get(key, default)

NAVER_CLIENT_ID    = get_secret("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET= get_secret("NAVER_CLIENT_SECRET")
NAVER_AD_API_KEY   = get_secret("NAVER_AD_API_KEY")
NAVER_AD_SECRET_KEY= get_secret("NAVER_AD_SECRET_KEY")
NAVER_CUSTOMER_ID  = get_secret("NAVER_CUSTOMER_ID")
APPS_SCRIPT_URL    = get_secret("APPS_SCRIPT_URL")
APPS_SCRIPT_TOKEN  = get_secret("APPS_SCRIPT_TOKEN")

# Load brands/competitors from env vars/config
T_DB   = [x.strip() for x in get_secret("MY_BRAND_1").split(',') if x.strip()]
T_BIT  = [x.strip() for x in get_secret("MY_BRAND_2").split(',') if x.strip()]
T_COMP = [x.strip() for x in get_secret("COMPETITORS").split(',') if x.strip()]


def load_keywords(file_path="keywords.txt"):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                kw_list = [line.strip() for line in f if line.strip()]
                if kw_list:
                    return kw_list
        except Exception as e:
            logging.error("keyword file read error: %s", e)
    return []


def get_vol(kw):
    if not (NAVER_AD_SECRET_KEY and NAVER_AD_API_KEY and NAVER_CUSTOMER_ID):
        return 0, 0, 0
    try:
        ts = str(int(time.time() * 1000))
        sig = base64.b64encode(
            hmac.new(NAVER_AD_SECRET_KEY.encode(),
                     ("%s.GET./keywordstool" % ts).encode(),
                     hashlib.sha256).digest()
        ).decode()
        headers = {
            "X-Timestamp": ts, "X-API-KEY": NAVER_AD_API_KEY,
            "X-Customer": NAVER_CUSTOMER_ID, "X-Signature": sig
        }
        res = requests.get(
            "https://api.naver.com/keywordstool?hintKeywords=%s&showDetail=1" % kw.replace(' ', ''),
            headers=headers, timeout=10
        )
        res.raise_for_status()
        for i in res.json().get('keywordList', []):
            if i.get('relKeyword', '').replace(" ", "") == kw.replace(" ", ""):
                v = (int(str(i.get('monthlyPcQcCnt', 0)).replace("<", "0")) +
                     int(str(i.get('monthlyMobileQcCnt', 0)).replace("<", "0")))
                c = (float(str(i.get('monthlyAvePcClkCnt', 0)).replace("<", "0")) +
                     float(str(i.get('monthlyAveMobileClkCnt', 0)).replace("<", "0")))
                return v, round(c, 1), round(c / v * 100, 2) if v else 0
    except Exception:
        pass
    return 0, 0, 0


def get_rank(kw):
    time.sleep(random.uniform(0.8, 1.8))
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        "User-Agent": "Mozilla/5.0"
    }
    try:
        res = requests.get(
            "https://openapi.naver.com/v1/search/shop.json",
            headers=headers,
            params={"query": kw, "display": 100, "sort": "sim"},
            timeout=10
        )
        res.raise_for_status()
        return res.json().get('items', [])
    except Exception as e:
        logging.warning("search error [%s]: %s", kw, e)
        return []


def send_naver_works_message(text):
    cid = get_secret("WORKS_CLIENT_ID")
    csec = get_secret("WORKS_CLIENT_SECRET")
    sa = get_secret("WORKS_SERVICE_ACCOUNT")
    pkey = get_secret("WORKS_PRIVATE_KEY")
    bot_id = get_secret("WORKS_BOT_ID")
    room_id = get_secret("WORKS_ROOM_ID")
    
    if not (cid and csec and sa and pkey and bot_id and room_id):
        return False, "네이버웍스 설정 정보가 누락되었습니다."
        
    try:
        import jwt
        now = int(time.time())
        private_key = pkey.strip().replace("\\n", "\n")
        
        payload = {
            "iss": cid,
            "sub": sa,
            "iat": now,
            "exp": now + 3600
        }
        
        headers = {
            "alg": "RS256",
            "typ": "JWT"
        }
        
        jwt_token = jwt.encode(payload, private_key, algorithm="RS256", headers=headers)
        
        auth_url = "https://auth.worksmobile.com/oauth2/v2.0/token"
        auth_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt_token,
            "client_id": cid,
            "client_secret": csec,
            "scope": "bot"
        }
        
        auth_res = requests.post(auth_url, data=auth_data, timeout=15)
        auth_res.raise_for_status()
        access_token = auth_res.json().get("access_token")
        
        if not access_token:
            return False, "Access Token 발급 실패"
            
        msg_url = f"https://www.worksapis.com/v1.0/bots/{bot_id}/messages"
        msg_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        
        msg_body = {
            "roomId": room_id,
            "content": {
                "type": "text",
                "text": text
            }
        }
        
        msg_res = requests.post(msg_url, json=msg_body, headers=msg_headers, timeout=15)
        msg_res.raise_for_status()
        return True, "성공"
    except Exception as e:
        return False, str(e)


def run_automation():
    import datetime as dt
    today_iso = (dt.datetime.utcnow() + dt.timedelta(hours=9)).strftime("%Y-%m-%d")
    keywords = load_keywords("keywords.txt")

    t_db_clean   = [x.replace(" ", "").lower() for x in T_DB]
    t_bit_clean  = [x.replace(" ", "").lower() for x in T_BIT]
    t_comp_clean = [x.replace(" ", "").lower() for x in T_COMP]

    results = []

    for kw in keywords:
        vol, clk, ctr = get_vol(kw)
        items = get_rank(kw)
        if not items:
            continue

        for r, item in enumerate(items, 1):
            raw_mall = item.get('mallName', '')
            cm = raw_mall.replace(" ", "").lower()

            is_mine = any(x in cm for x in t_db_clean + t_bit_clean)
            is_comp = any(x in cm for x in t_comp_clean)

            if r > 3 and not is_mine and not is_comp:
                continue

            sm = raw_mall
            if any(x in cm for x in t_db_clean):
                sm = T_DB[0] if T_DB else raw_mall
            elif any(x in cm for x in t_bit_clean):
                sm = T_BIT[0] if T_BIT else raw_mall
            else:
                for comp in T_COMP:
                    if comp.replace(" ", "").lower() in cm:
                        sm = comp
                        break

            comp_flags = {
                ("is_comp_%d" % (i+1)): comp.replace(" ", "").lower() in cm
                for i, comp in enumerate(T_COMP)
            }

            row = {
                "date": today_iso, "keyword": kw,
                "vol": vol, "click": clk, "ctr": ctr,
                "rank": r, "mall": sm,
                "title": item.get('title', '').replace("<b>", "").replace("</b>", ""),
                "price": item.get('lprice', 0),
                "link":  item.get('link', ''),
                "is_db":  any(x in cm for x in t_db_clean),
                "is_bit": any(x in cm for x in t_bit_clean),
            }
            row.update(comp_flags)
            results.append(row)

    if results and APPS_SCRIPT_URL:
        import pandas as pd, io as _io
        df = pd.DataFrame(results)
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        try:
            requests.post(
                APPS_SCRIPT_URL,
                params={"token": APPS_SCRIPT_TOKEN, "type": "auto_daily"},
                data=csv_bytes,
                headers={"Content-Type": "text/plain; charset=utf-8"},
                timeout=30
            )
            logging.info("GAS upload complete")
        except Exception as e:
            logging.error("GAS upload failed: %s", e)

    # --- 네이버웍스 자동화 알림 발송 ---
    bot_id = get_secret("WORKS_BOT_ID")
    room_id = get_secret("WORKS_ROOM_ID")
    if results and bot_id and room_id:
        logging.info("Sending NAVER WORKS summary alert...")
        df = pd.DataFrame(results)
        
        today_kor = (dt.datetime.utcnow() + dt.timedelta(hours=9)).strftime("%Y년 %m월 %d일")
        
        summary_msg = f"[🛒 쇼핑 통합 관제 보고서 (자동)]\n수집일자: {today_kor}\n\n"
        summary_msg += f"- 전체 모니터링 키워드: {df['keyword'].nunique()}개\n"
        
        b1_val = get_secret("MY_BRAND_1")
        b2_val = get_secret("MY_BRAND_2")
        
        b1_pat = "|".join([x.strip() for x in b1_val.split(',') if x.strip()]) if b1_val else ""
        b2_pat = "|".join([x.strip() for x in b2_val.split(',') if x.strip()]) if b2_val else ""
        
        top_df = df[df['rank'] <= 3]
        total_db = top_df[top_df['mall'].str.contains(b1_pat, na=False)]['keyword'].nunique() if not top_df.empty and b1_pat else 0
        total_bit = top_df[top_df['mall'].str.contains(b2_pat, na=False)]['keyword'].nunique() if not top_df.empty and b2_pat else 0
        
        brand1_lbl = b1_val.split(',')[0].strip() if b1_val else "브랜드1"
        brand2_lbl = b2_val.split(',')[0].strip() if b2_val else "브랜드2"
        
        summary_msg += f"- {brand1_lbl} 1-3위 노출: {total_db}건\n"
        if b2_pat:
            summary_msg += f"- {brand2_lbl} 1-3위 노출: {total_bit}건\n"
            
        success, w_msg = send_naver_works_message(summary_msg)
        if success:
            logging.info("NAVER WORKS summary alert sent successfully.")
        else:
            logging.error("Failed to send NAVER WORKS alert: %s", w_msg)


if __name__ == "__main__":
    run_automation()
