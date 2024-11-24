import discord
from discord.ext import commands
import json
import os
import asyncio
from PIL import Image  # Pillow 라이브러리 import
import time  # 타임스탬프 생성을 위한 모듈

# JSON 파일 경로
data_file = 'shortcuts.json'
images_folder = 'images'  # 이미지 저장 폴더

# 이미지 폴더가 존재하지 않으면 생성
if not os.path.exists(images_folder):
    os.makedirs(images_folder)

# 단축어 데이터를 로드하는 함수
def load_shortcuts():
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 단축어 데이터를 저장하는 함수
def save_shortcuts(shortcuts):
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(shortcuts, f, ensure_ascii=False, indent=4)

# 이미지 리사이징 함수
def resize_image(image_path, output_path):
    with Image.open(image_path) as img:
        aspect_ratio = img.height / img.width
        new_width = 160  # 가로 160픽셀로 설정
        new_height = int(new_width * aspect_ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)  # 160픽셀로 리사이즈
        
        dpi = img.info.get('dpi', (72, 72))  # 기본 DPI를 72로 설정
        img.save(output_path, dpi=dpi)

        print(f"Saved resized image: {output_path} with size: {img.size} and DPI: {dpi}")

# setup 함수 추가
def setup(bot_instance):
    global bot
    bot = bot_instance

    @bot.command(name='단축어', aliases=['shortcut'])
    async def register_shortcut(ctx):
        await ctx.send('등록할 단축어 이름을 입력하세요:')
        
        def check_name(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            name_response = await bot.wait_for('message', check=check_name, timeout=30.0)
            shortcut_name = name_response.content.strip()

            await ctx.send('단축어 내용을 입력하세요:')
            content_response = await bot.wait_for('message', check=check_name, timeout=30.0)

            if content_response.attachments:
                image = content_response.attachments[0]
                timestamp = int(time.time())
                unique_image_filename = f'{timestamp}_{image.filename}'
                original_image_path = os.path.join(images_folder, unique_image_filename)
                await image.save(original_image_path)

                await ctx.send('리사이징을 하시겠습니까? (예/아니요)')
                resize_response = await bot.wait_for('message', check=check_name, timeout=30.0)

                if resize_response.content.strip().lower() in ['예', 'yes']:
                    resized_image_filename = f'resized_{unique_image_filename}'
                    resized_image_path = os.path.join(images_folder, resized_image_filename)
                    resize_image(original_image_path, resized_image_path)
                    shortcut_content = resized_image_filename
                else:
                    shortcut_content = unique_image_filename
            else:
                shortcut_content = content_response.content.strip()  # 텍스트 단축어 내용

            shortcuts = load_shortcuts()
            shortcuts[shortcut_name] = shortcut_content
            save_shortcuts(shortcuts)
            
            await ctx.send(f'단축어 **{shortcut_name}**이(가) 등록되었습니다.')

        except asyncio.TimeoutError:
            await ctx.send('시간이 초과되었습니다. 다시 시도하세요.')

    @bot.command(name='삭제')
    async def delete_shortcut(ctx):
        shortcuts = load_shortcuts()

        await ctx.send('삭제할 단축어 이름을 입력하세요:')
        
        def check_delete(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            delete_name_response = await bot.wait_for('message', check=check_delete, timeout=30.0)
            shortcut_name = delete_name_response.content.strip()

            if shortcut_name in shortcuts:
                shortcut_content = shortcuts[shortcut_name]

                if shortcut_content.startswith('resized_'):
                    image_path = os.path.join(images_folder, shortcut_content)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        print(f"Deleted image file: {image_path}")

                del shortcuts[shortcut_name]
                save_shortcuts(shortcuts)
                await ctx.send(f'단축어 **{shortcut_name}**이(가) 삭제되었습니다.')
            else:
                await ctx.send(f'단축어 **{shortcut_name}**이(가) 등록되어 있지 않습니다.')

        except asyncio.TimeoutError:
            await ctx.send('시간이 초과되었습니다. 다시 시도하세요.')

    @bot.command(name='조회')
    async def view_shortcuts(ctx):
        shortcuts = load_shortcuts()
        if not shortcuts:
            await ctx.send('등록된 단축어가 없습니다.')
            return

        shortcut_list = list(shortcuts.keys())
        items_per_line = 3  # 한 줄에 보여줄 단축어 개수
        total_lines = (len(shortcut_list) - 1) // items_per_line + 1  # 전체 줄 수
        lines_per_page = 15  # 한 페이지에 보여줄 줄 수
        total_pages = (total_lines - 1) // lines_per_page + 1  # 전체 페이지 수
        current_page = 0  # 현재 페이지

        def get_page_content(page):
            start_line = page * lines_per_page
            end_line = start_line + lines_per_page
            page_lines = []

            for i in range(start_line, min(end_line, total_lines)):
                start_item = i * items_per_line
                end_item = start_item + items_per_line
                line_items = shortcut_list[start_item:end_item]
                page_lines.append(', '.join(line_items))

            return f'**단축어 목록 (페이지 {page + 1}/{total_pages})**\n' + '\n'.join(page_lines)

        # 첫 페이지 출력
        message = await ctx.send(get_page_content(current_page))

        # 페이지 넘김을 위한 반응 추가
        if total_pages > 1:
            await message.add_reaction('⬅️')  # 이전 페이지
            await message.add_reaction('➡️')  # 다음 페이지

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ['⬅️', '➡️']

            while True:
                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                    if str(reaction.emoji) == '⬅️' and current_page > 0:
                        current_page -= 1
                    elif str(reaction.emoji) == '➡️' and current_page < total_pages - 1:
                        current_page += 1
                    else:
                        await message.remove_reaction(reaction, user)
                        continue

                    # 페이지 업데이트
                    await message.edit(content=get_page_content(current_page))
                    await message.remove_reaction(reaction, user)

                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    break

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        if message.content.startswith('?'):
            command = message.content[1:]  # '?' 제거
            ctx = await bot.get_context(message)  # ctx 가져오기

            if command == '단축어':
                await register_shortcut(ctx)
                return
            elif command == '삭제':
                await delete_shortcut(ctx)
                return
            elif command == '조회':
                await view_shortcuts(ctx)
                return
            else:
                shortcuts = load_shortcuts()
                if command in shortcuts:
                    content = shortcuts[command]
                    if os.path.exists(os.path.join(images_folder, content)):
                        await message.channel.send(file=discord.File(os.path.join(images_folder, content)))
                    else:
                        await message.channel.send(content)
                    return

        await bot.process_commands(message)  # 다른 커맨드 처리
