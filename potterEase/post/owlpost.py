import json
import os

# JSON 파일 경로
data_file = '../potterEase/recipients.json'

# 수신자 데이터 초기화
recipients = {
    "1288390532812242990": "알리샤",
    "1285946172652916737": "키릴",
    "1280800462827950123": "이든",
    "1280029844809453613": "에이셔",
    "1286244341425246269": "헬리오스",
    "1286208758338424874": "트윌리",
    "1302940254076141641": "세라피아스",
    "435410215681130507": "라난시"
}

# JSON 파일이 없으면 생성하고 데이터 저장
if not os.path.exists(data_file):
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(recipients, f, ensure_ascii=False, indent=4)
    print(f"{data_file}에 수신자 데이터가 저장되었습니다.")
else:
    print(f"{data_file} 파일 시스템에 정상 로그인 되었습니다.")
