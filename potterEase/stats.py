import json
import random

# 능력치 초기화
initial_stats = {
    "공격": 30,
    "방어": 30,
    "민첩": 30,
    "지능": 30,
    "이성": 30,
    "운": 30
}

# JSON 파일 경로
data_file = 'user_stats.json'

def 나(ctx):
    user_id = str(ctx.author.id)
    user_nickname = ctx.author.display_name  # 유저의 현재 닉네임 가져오기

    # JSON 파일 읽기
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # 유저 데이터가 없는 경우 초기화
    if user_id not in data:
        # 새로운 유저 데이터 생성
        data[user_id] = {
            "닉네임": user_nickname,  # 닉네임 추가
            "능력치": initial_stats    # 능력치를 별도의 딕셔너리로 추가
        }
        save_user_data(data)  # 데이터 저장
        return f'새로운 캐릭터 데이터가 등록되었습니다: {initial_stats}'
    else:
        # 기존 유저 데이터가 있는 경우 닉네임 업데이트
        data[user_id]["닉네임"] = user_nickname  # 닉네임 업데이트
        save_user_data(data)  # 데이터 저장 (닉네임만 업데이트)

        user_stats = data[user_id]["능력치"]
        stats_message = ' | '.join([
            f'**{key}**: {user_stats[key]}' for key in ["공격", "방어", "민첩", "지능", "이성", "운"]
        ])
        return f'### [{user_nickname}]\n{stats_message}'

def save_user_data(data):
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def handle_나_command(bot, message):
    ctx = await bot.get_context(message)
    response = 나(ctx)
    await ctx.send(response)

async def handle_능력치_command(bot, message, 능력치):
    ctx = await bot.get_context(message)
    user_id = str(ctx.author.id)

    # JSON 파일 읽기
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    if user_id in data:
        user_stats = data[user_id]["능력치"]
        능력치_value = user_stats.get(능력치)

        if 능력치_value is None:
            return  # 잘못된 능력치 메시지를 없애기 위해 아무것도 하지 않음

        # 1부터 100까지 랜덤 숫자 생성
        random_value = random.randint(1, 100)

        # 결과 비교
        if random_value == 100:
            result = '끔찍한 실패!'
        elif random_value > 능력치_value:
            result = '실패'
        elif random_value <= 능력치_value / 4:
            result = '엄청난 성공!'
        elif random_value <= 능력치_value / 2:
            result = '능숙한 성공'
        else:
            result = '보통 성공'

        # 결과 포맷을 수정하여 출력
        await ctx.send(f'**{random_value}**  <  {능력치} {능력치_value}\n\n***{result}***')
    else:
        await ctx.send('유저 데이터를 찾을 수 없습니다.')
