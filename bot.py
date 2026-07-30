import asyncio
import json
import os
import re
import time
import uuid
import traceback
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class RoleInfo:
    label: str
    role_id: int
    emoji: str
    count_only: bool = False

ROLE_ORDER = [
    RoleInfo('Owner', 1531246359729016972, ''),
    RoleInfo('Deputy Owner', 1531246359729016969, ''),
    RoleInfo('High Rank', 1531246359729016968, ''),
    RoleInfo('Medium Rank', 1531246359729016966, ''),
    RoleInfo('CENT', 1532160160330551478, ''),
]

RECRUIT_ROLE_ID = 1531246359712370817
THUMBNAIL_URL = 'https://media.discordapp.net/attachments/1509878666782445678/1517471349679849603/file_00000000f4a8722fafeb213d214c0763_4.png?ex=6a443e93&is=6a42ed13&hm=0c9589eead2a223a954137051b31fb35949d7c69dc49cbb934419c963c55cc66&=&format=webp&quality=lossless&width=864&height=864'
MAIN_IMAGE_URL = 'https://cdn.discordapp.com/attachments/1346126083363307651/1346128287000297563/YOUNGHILL-03-03-2025.gif?ex=6a43d3a9&is=6a428229&hm=8f89a624939d58b8ac6505a6bb4c5ee1b3430fae2e9b99e5bd0333a54ccf306c&'
WELCOME_IMAGE_URL = 'https://cdn.discordapp.com/attachments/1342073128112623666/1520871241353793608/welcome.png?ex=6a456838&is=6a4416b8&hm=07c5a8cf2126711faa146c83bdf3e11e7abf207939280eeb6ec9f9b743721301&'
STATE_FILE = Path(__file__).with_name('board-state.json')
IMAGE_STATE_FILE = Path(__file__).with_name('bot-image-state.json')
CENT_IMAGE_FILE = Path(__file__).parent / 'assets' / 'cent.png'
RECRUIT_STATE_FILE = Path(__file__).with_name('recruit-state.json')
REPORT_BUTTON_STATE_FILE = Path(__file__).with_name('report-button-state.json')
BIRTHDAY_STATE_FILE = Path(__file__).with_name('birthday-state.json')

APP_STATE_FILE = Path(__file__).with_name('app-state.json')
RECRUIT_APP_STATE_FILE = Path(__file__).with_name('recruit-app-state.json')
STATS_STATE_FILE = Path(__file__).with_name('stats-state.json')
REMINDERS_STATE_FILE = Path(__file__).with_name('reminders-state.json')
VERIFICATION_STATE_FILE = Path(__file__).with_name('verification-state.json')
try:
    BOT_IMAGE_URL = json.loads(IMAGE_STATE_FILE.read_text(encoding='utf-8')).get('url')
except (OSError, ValueError, AttributeError):
    BOT_IMAGE_URL = None

THUMBNAIL_URL = BOT_IMAGE_URL
MAIN_IMAGE_URL = BOT_IMAGE_URL
WELCOME_IMAGE_URL = BOT_IMAGE_URL
ADMIN_PANEL_CHANNEL_ID = int(os.getenv('ADMIN_PANEL_CHANNEL_ID', '1523819460538925086'))
MEETING_ROLE_ID = int(os.getenv('MEETING_ROLE_ID', '0'))
MEETING_VOICE_CHANNEL_ID = int(os.getenv('MEETING_VOICE_CHANNEL_ID', '1342078486419869762'))
AUTO_REFRESH_SECONDS = 5 * 60
REFRESH_BUTTON_ID = 'family_refresh'
RECRUIT_REFRESH_BUTTON_ID = 'recruit_refresh'
CREATE_RECRUIT_INVITE_BUTTON_ID = 'recruit_create_invite'
REFRESH_RECRUIT_BOARD_BUTTON_ID = 'recruit_refresh_board'
REPORT_RECRUIT_INVITE_BUTTON_ID = 'recruit_report_invite'
BIRTHDAY_SUBMIT_BUTTON_ID = 'birthday_submit'
RECRUIT_APP_BUTTON_ID = 'recruit_app_submit'
ADMIN_MEETING_BUTTON_ID = 'admin_meeting_button'
ADMIN_MEETING_SMS_BUTTON_ID = 'admin_meeting_sms'
ADMIN_REMIND_1H_BUTTON_ID = 'admin_remind_1h'
ANNOUNCEMENT_BUTTON_ID = 'admin_announcement'
LEADERBOARD_PREV_BUTTON_ID = 'leaderboard_prev'
LEADERBOARD_NEXT_BUTTON_ID = 'leaderboard_next'
BLACKLIST_BUTTON_ID = 'blacklist_add'

BOT_TOKEN = os.getenv('BOT_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
GUILD_ID = os.getenv('GUILD_ID')
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID', '1532171920659841204'))
RECRUIT_BOARD_CHANNEL_ID = int(os.getenv('RECRUIT_BOARD_CHANNEL_ID', '1531246362274955369'))
INVITE_CHANNEL_ID = int(os.getenv('INVITE_CHANNEL_ID', str(TARGET_CHANNEL_ID)))
RECRUIT_REPORT_CHANNEL_ID = int(os.getenv('RECRUIT_REPORT_CHANNEL_ID', '1531246362274955371'))
BIRTHDAY_BOARD_CHANNEL_ID = int(os.getenv('BIRTHDAY_BOARD_CHANNEL_ID', '0'))
BIRTHDAY_GREETING_CHANNEL_ID = int(os.getenv('BIRTHDAY_GREETING_CHANNEL_ID', '0'))
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', '0'))
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID', '1342073128112623666'))

APP_CREATE_CHANNEL_ID = int(os.getenv('APP_CREATE_CHANNEL_ID', '0'))
APP_LOG_CHANNEL_ID = int(os.getenv('APP_LOG_CHANNEL_ID', '1531246362274955368'))
APP_CATEGORY_ID = int(os.getenv('APP_CATEGORY_ID', '0'))
RECRUIT_APP_BANNER_CHANNEL_ID = int(os.getenv('RECRUIT_APP_BANNER_CHANNEL_ID', '0'))
RECRUIT_APP_LIST_CHANNEL_ID = int(os.getenv('RECRUIT_APP_LIST_CHANNEL_ID', '0'))
VERIFICATION_ROLE_ID = int(os.getenv('VERIFICATION_ROLE_ID', '1531246359674487039'))
VERIFICATION_EMOJI = os.getenv('VERIFICATION_EMOJI', '✅')

BLACKLIST_CHANNEL_ID = int(os.getenv('BLACKLIST_CHANNEL_ID', '1531246362274955373'))
BLACKLIST_STATE_FILE = Path(__file__).with_name('blacklist-state.json')

NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY')
NVIDIA_API_URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
NVIDIA_MODEL = 'nvidia/ising-calibration-1.5-31b'

if not BOT_TOKEN:
    raise SystemExit('Please set BOT_TOKEN in your .env file.')

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.voice_states = True
intents.reactions = True

class RefreshView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label='Обновить', style=discord.ButtonStyle.primary, emoji='🔄', custom_id=REFRESH_BUTTON_ID)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            return
        asyncio.create_task(refresh_board_safely())
        try:
            await interaction.followup.send('Обновляю баннер...', ephemeral=True)
        except Exception:
            pass


class RecruitRefreshView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label='Обновить', style=discord.ButtonStyle.primary, emoji='🔄', custom_id=RECRUIT_REFRESH_BUTTON_ID)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            return
        asyncio.create_task(refresh_recruit_board_safely())
        try:
            await interaction.followup.send('Обновляю баннер...', ephemeral=True)
        except Exception:
            pass



class RecruitReportModal(discord.ui.Modal, title='Отписать приглашённого'):
    full_name = discord.ui.TextInput(
        label='Имя Фамилия',
        placeholder='Например: Иван Иванов',
        max_length=80,
    )
    passport_number = discord.ui.TextInput(
        label='Номер паспорта',
        placeholder='Например: 123456',
        max_length=40,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not isinstance(interaction.user, discord.Member) or not has_recruit_role(interaction.user):
            await interaction.response.send_message('Эта форма доступна только рекрутам.', ephemeral=True)
            return

        channel = await get_text_channel(RECRUIT_REPORT_CHANNEL_ID)
        embed = discord.Embed(
            title='📝 Новый отчёт рекрута',
            color=0x38BDF8,
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name='Рекрут', value=format_member(interaction.user), inline=False)
        embed.add_field(name='Имя Фамилия', value=str(self.full_name), inline=True)
        embed.add_field(name='Номер паспорта', value=str(self.passport_number), inline=True)
        embed.set_thumbnail(url=THUMBNAIL_URL)

        await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
        await interaction.response.send_message('Отчёт отправлен.', ephemeral=True)
        asyncio.create_task(send_log(
            '📝 Новый отчёт рекрута',
            f'{interaction.user.mention} отправил отчёт\n'
            f'**Имя Фамилия:** {self.full_name}\n'
            f'**Паспорт:** {self.passport_number}',
            color=0x38BDF8, user=interaction.user,
        ))


class BirthdayModal(discord.ui.Modal, title='Добавить день рождения'):
    birthday_date = discord.ui.TextInput(
        label='Дата рождения',
        placeholder='01.01.2007 или 01.01',
        max_length=20,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message('Эта форма работает только на сервере.', ephemeral=True)
            return

        parsed = parse_birthday_text(str(self.birthday_date))
        if parsed is None:
            await interaction.response.send_message('Не понял дату. Используй формат DD.MM.YYYY или DD.MM.', ephemeral=True)
            return

        async with bot.birthday_lock:
            state = read_birthday_state()
            state['entries'][str(interaction.user.id)] = {
                'day': parsed['day'],
                'month': parsed['month'],
                'year': parsed.get('year'),
                'text': parsed['text'],
                'updated_at': discord.utils.utcnow().isoformat(),
            }
            write_birthday_state(state)

        await refresh_birthday_board_safely()
        await interaction.response.send_message('Дата сохранена.', ephemeral=True)
        asyncio.create_task(send_log(
            '🎂 День рождения добавлен',
            f'{interaction.user.mention} установил дату: **{parsed["text"]}**',
            color=0xF97316, user=interaction.user,
        ))


class BirthdayButtonView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label='Добавить дату', style=discord.ButtonStyle.primary, emoji='🎂', custom_id=BIRTHDAY_SUBMIT_BUTTON_ID)
    async def add_birthday_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(BirthdayModal())


class BlacklistSearchModal(discord.ui.Modal, title='Поиск участника'):
    query = discord.ui.TextInput(
        label='Введите имя или ник',
        placeholder='Часть имени для поиска...',
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        q = str(self.query).lower().strip()
        guild = interaction.guild
        if not guild:
            return
        members = [m for m in guild.members if not m.bot and q in m.display_name.lower()]
        members.sort(key=lambda m: m.display_name.lower())
        if not members:
            await interaction.response.send_message('Участники не найдены.', ephemeral=True)
            return
        await interaction.response.send_message(
            f'Найдено {len(members)}:',
            view=BlacklistMemberView(members),
            ephemeral=True,
        )


class BlacklistMemberSelect(discord.ui.Select):
    def __init__(self, members: list[discord.Member]) -> None:
        options = [
            discord.SelectOption(label=m.display_name, value=str(m.id), description=f'ID: {m.id}')
            for m in members[:25]
        ]
        super().__init__(placeholder='Выберите участника...', options=options, custom_id='blacklist_member_select')

    async def callback(self, interaction: discord.Interaction) -> None:
        member_id = int(self.values[0])
        member = interaction.guild.get_member(member_id) or await interaction.guild.fetch_member(member_id)
        await interaction.response.send_modal(BlacklistReasonModal(member))


class BlacklistMemberView(discord.ui.View):
    def __init__(self, members: list[discord.Member]) -> None:
        super().__init__(timeout=60)
        self.add_item(BlacklistMemberSelect(members))


class BlacklistReasonModal(discord.ui.Modal, title='Чёрный список — причина'):
    member_id: int = 0
    member_name: str = ''

    reason = discord.ui.TextInput(
        label='Причина',
        placeholder='Укажите причину добавления',
        style=discord.TextStyle.paragraph,
        max_length=500,
    )

    def __init__(self, member: discord.Member) -> None:
        super().__init__()
        self.member_id = member.id
        self.member_name = member.display_name

    async def on_submit(self, interaction: discord.Interaction) -> None:
        channel = await get_text_channel(BLACKLIST_CHANNEL_ID)
        embed = discord.Embed(
            title='🚫 Чёрный список + БАН',
            color=0xEF4444,
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name='Участник', value=f'<@{self.member_id}>', inline=True)
        embed.add_field(name='Причина', value=str(self.reason), inline=False)
        embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=f'Добавлено: {interaction.user.display_name}', icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)

        await channel.send(embed=embed)

        member = interaction.guild.get_member(self.member_id)
        ban_status = ''
        if member:
            try:
                await member.ban(reason=str(self.reason), delete_message_days=0)
                ban_status = ' и забанен'
            except Exception:
                ban_status = ' (бан не удался)'
        else:
            ban_status = ' (участник не на сервере)'

        await interaction.response.send_message(f'<@{self.member_id}> добавлен в чёрный список{ban_status}.', ephemeral=True)
        asyncio.create_task(send_log(
            '🚫 Добавлен в чёрный список + БАН',
            fields=[
                ('Участник', f'<@{self.member_id}>', True),
                ('Причина', str(self.reason), False),
                ('Добавил', _log_user_field(interaction.user), True),
            ],
            color=0xEF4444, user=interaction.user,
        ))


class BlacklistView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label='Добавить в чёрный список', style=discord.ButtonStyle.danger, emoji='🚫', custom_id='blacklist_add')
    async def blacklist_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(BlacklistSearchModal())


class RecruitReportButtonView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label='Отписать приглашённого', style=discord.ButtonStyle.primary, emoji='📝', custom_id=REPORT_RECRUIT_INVITE_BUTTON_ID)
    async def report_invite_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not isinstance(interaction.user, discord.Member) or not has_recruit_role(interaction.user):
            try:
                await interaction.response.send_message('Эта кнопка доступна только рекрутам.', ephemeral=True)
            except discord.HTTPException as exc:
                if 'already been acknowledged' in str(exc):
                    try:
                        await interaction.followup.send('Эта кнопка доступна только рекрутам.', ephemeral=True)
                    except Exception:
                        return
                else:
                    return
            return
        try:
            await interaction.response.send_modal(RecruitReportModal())
        except discord.NotFound:
            return
        except discord.HTTPException as exc:
            if 'already been acknowledged' in str(exc):
                try:
                    await interaction.followup.send('Не удалось открыть форму, попробуйте снова.', ephemeral=True)
                except Exception:
                    pass
            else:
                raise

class RecruitView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label='Создать ссылку', style=discord.ButtonStyle.success, emoji='🔗', custom_id=CREATE_RECRUIT_INVITE_BUTTON_ID)
    async def create_invite_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message('Эта кнопка работает только на сервере.', ephemeral=True)
            return
        if not has_recruit_role(interaction.user):
            await interaction.response.send_message('Эта кнопка доступна только рекрутам.', ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            record = await create_or_get_recruit_invite(interaction.user)
            await refresh_recruit_board_safely()
            await interaction.followup.send(
                f'Твоя личная ссылка уже закреплена за тобой:\n{record["invite_url"]}',
                ephemeral=True,
            )
            asyncio.create_task(send_log(
                '🔗 Ссылка рекрута',
                f'{interaction.user.mention} получил ссылку (кнопка)\n{record["invite_url"]}',
                color=0x22C55E, user=interaction.user,
            ))
        except Exception as exc:
            await interaction.followup.send(f'Не смог создать ссылку: {exc}', ephemeral=True)
            asyncio.create_task(send_log(
                '❌ Ошибка создания ссылки',
                f'{interaction.user.mention} — не удалось создать ссылку\n```{exc}```',
                color=0xEF4444, user=interaction.user,
            ))

    @discord.ui.button(label='Обновить', style=discord.ButtonStyle.secondary, emoji='🔄', custom_id=REFRESH_RECRUIT_BOARD_BUTTON_ID)
    async def refresh_recruit_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            return
        asyncio.create_task(refresh_recruit_board_safely())
        try:
            await interaction.followup.send('Обновляю плашку рекрутов...', ephemeral=True)
        except Exception:
            pass

# --------------- Заявка в семью (тикеты + кнопки решения) ---------------

FRIEND_ROLE_ID = 1531246359674487040
CENT_ROLE_ID = 1532160160330551478

# Хранилище собранных данных заявки по user_id
family_applications: dict[int, dict] = {}


class FamilyAppDecisionView(discord.ui.View):
    """Кнопки Принять/Отклонить на финальной заявке (как у рекрутов)."""
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    def _is_recruit_or_above(self, member: discord.Member) -> bool:
        recruit_role = member.guild.get_role(RECRUIT_ROLE_ID)
        if recruit_role is None:
            return False
        return member.top_role.position >= recruit_role.position

    @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success, emoji='✅', custom_id='family_app_accept')
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member) or not self._is_recruit_or_above(interaction.user):
            await interaction.response.send_message('У тебя нет прав принимать заявки.', ephemeral=True)
            return

        await interaction.response.defer()

        guild = interaction.guild
        applicant = guild.get_member(self.applicant_id)
        cent_role = guild.get_role(CENT_ROLE_ID)
        if applicant and cent_role:
            try:
                await applicant.add_roles(cent_role, reason=f'Заявка принята {interaction.user}')
            except Exception:
                pass

        if applicant:
            try:
                await applicant.send('Ваша заявка была рассмотрена, Вас приняли в **семью**.\nПоздравляем! 🎉')
            except Exception:
                pass

        embed = interaction.message.embeds[0] if interaction.message.embeds else None
        if embed:
            new_embed = embed.copy()
            new_embed.color = 0x10B981
            new_embed.set_footer(text=f'✅ Принята — {interaction.user.display_name}')
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(embed=new_embed, view=self)

        asyncio.create_task(send_log(
            '✅ Заявка в семью принята',
            fields=[
                ('Участник', f'<@{self.applicant_id}> (`{self.applicant_id}`)', True),
                ('Рассмотрел', _log_user_field(interaction.user), True),
            ],
            color=0x10B981, user=interaction.user,
        ))

    @discord.ui.button(label='❌ Отклонить', style=discord.ButtonStyle.danger, emoji='❌', custom_id='family_app_reject')
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member) or not self._is_recruit_or_above(interaction.user):
            await interaction.response.send_message('У тебя нет прав отклонять заявки.', ephemeral=True)
            return

        await interaction.response.defer()

        applicant = interaction.guild.get_member(self.applicant_id)
        if applicant:
            try:
                await applicant.send('Ваша заявка была рассмотрена, **Отказано**.')
            except Exception:
                pass

        embed = interaction.message.embeds[0] if interaction.message.embeds else None
        if embed:
            new_embed = embed.copy()
            new_embed.color = 0xEF4444
            new_embed.set_footer(text=f'❌ Отклонена — {interaction.user.display_name}')
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(embed=new_embed, view=self)

        asyncio.create_task(send_log(
            '❌ Заявка в семью отклонена',
            fields=[
                ('Участник', f'<@{self.applicant_id}> (`{self.applicant_id}`)', True),
                ('Рассмотрел', _log_user_field(interaction.user), True),
            ],
            color=0xEF4444, user=interaction.user,
        ))

    @discord.ui.button(label='📞 Вызвать на связь', style=discord.ButtonStyle.primary, emoji='📞', custom_id='family_app_call')
    async def call(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member) or not self._is_recruit_or_above(interaction.user):
            await interaction.response.send_message('У тебя нет прав вызывать на связь.', ephemeral=True)
            return

        await interaction.response.defer()

        applicant = interaction.guild.get_member(self.applicant_id)
        if applicant:
            try:
                await applicant.send(
                    'Ваша заявка была рассмотрена, ждём вас в войсе для собеседования.\nЖдём вас. 🎙️'
                )
                await interaction.followup.send(f'Сообщение отправлено {applicant.mention}', ephemeral=True)
            except Exception:
                await interaction.followup.send('Не удалось отправить сообщение (возможно, закрыты ЛС).', ephemeral=True)
        else:
            await interaction.followup.send('Участник не найден на сервере.', ephemeral=True)

        asyncio.create_task(send_log(
            '📞 Вызов на собеседование',
            fields=[
                ('Участник', f'<@{self.applicant_id}> (`{self.applicant_id}`)', True),
                ('Вызвал', _log_user_field(interaction.user), True),
            ],
            color=0x3B82F6, user=interaction.user,
        ))


# TicketAdminView оставлен как заглушка для совместимости с Discord custom_id кэшем
class TicketAdminView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Закрыть тикет', style=discord.ButtonStyle.danger, custom_id='app_close_ticket', emoji='🔒')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Эта функция больше не используется.', ephemeral=True)


# TicketFinalStageView оставлен как заглушка для совместимости с Discord custom_id кэшем
class TicketFinalStageView(discord.ui.View):
    def __init__(self, applicant_id: int = 0):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label='Завершить заявку', style=discord.ButtonStyle.success, custom_id='app_stage_final', emoji='✅')
    async def finish_app(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Эта функция больше не используется.', ephemeral=True)




class AppModalPartTwo(discord.ui.Modal, title='Заявка: Часть 2'):
    q1 = discord.ui.TextInput(label='Готовы сменить фамилию на CENT?', placeholder='Да/Нет', style=discord.TextStyle.short)
    q2 = discord.ui.TextInput(label='Готовы соблюдать правила семьи?', placeholder='Да/Нет', style=discord.TextStyle.short)
    q3 = discord.ui.TextInput(label='Прайм тайм (1. вечер, 2. день, 3. всегда)', placeholder='Например: 1', style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        # Сохраняем ответы
        family_applications.setdefault(interaction.user.id, {})
        family_applications[interaction.user.id].update({
            'surname': self.q1.value,
            'rules': self.q2.value,
            'prime': self.q3.value,
        })

        data = family_applications.get(interaction.user.id, {})
        app_type = data.get('type', 'Ticket')

        # Формируем итоговую заявку для администрации
        admin_embed = discord.Embed(
            title=f'📋 Новая заявка в семью CENT ({app_type})',
            color=0x3B82F6,
            timestamp=discord.utils.utcnow(),
        )
        admin_embed.set_author(
            name=f'{interaction.user.display_name} ({interaction.user.name})',
            icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None,
        )
        admin_embed.add_field(name='Участник', value=interaction.user.mention, inline=True)
        admin_embed.add_field(name='Тип заявки', value=f'**{app_type}**', inline=True)
        admin_embed.add_field(name='Имя Фамилия (IC)', value=data.get('name', '—'), inline=True)
        admin_embed.add_field(name='Уровень в игре', value=data.get('level', '—'), inline=True)
        admin_embed.add_field(name='Возраст (OOC)', value=data.get('age', '—'), inline=True)
        admin_embed.add_field(name='Знания РП', value=data.get('rp', '—'), inline=True)
        admin_embed.add_field(name='Почему к нам', value=data.get('why', '—'), inline=False)
        admin_embed.add_field(name='Смена фамилии', value=data.get('surname', '—'), inline=True)
        admin_embed.add_field(name='Соблюдение правил', value=data.get('rules', '—'), inline=True)
        admin_embed.add_field(name='Прайм тайм', value=data.get('prime', '—'), inline=True)
        admin_embed.set_footer(text=f'ID: {interaction.user.id}')

        # Отправляем в канал заявок администрации
        target_channel_id = APP_LOG_CHANNEL_ID or RECRUIT_APP_LIST_CHANNEL_ID or LOG_CHANNEL_ID
        if target_channel_id:
            try:
                log_chan = bot.get_channel(target_channel_id)
                if log_chan is None:
                    log_chan = await bot.fetch_channel(target_channel_id)
                if isinstance(log_chan, discord.TextChannel):
                    await log_chan.send(embed=admin_embed, view=FamilyAppDecisionView(interaction.user.id))
            except Exception as exc:
                print(f'[APP LOG ERROR] {exc}')

        asyncio.create_task(send_log(
            '📋 Заявка в семью подана',
            fields=[
                ('Участник', _log_user_field(interaction.user), True),
                ('Тип заявки', app_type, True),
            ],
            color=0x22C55E, user=interaction.user,
        ))

        # Финальная карточка подтверждения пользователю
        final_embed = discord.Embed(
            title='✅ Заявка отправлена!',
            description='Ваша заявка успешно заполнена и передана администрации семьи **CENT**.\nОжидайте ответа!',
            color=0x22C55E,
        )
        final_embed.set_footer(text='Форма заявки')
        await interaction.response.send_message(embed=final_embed, ephemeral=True)


class TicketStageTwoView(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label='Шаг 2 — продолжить', style=discord.ButtonStyle.success, emoji='➡️', custom_id='app_stage_two')
    async def next_stage(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AppModalPartTwo())


class AppModalPartOne(discord.ui.Modal, title='Заявка: Часть 1'):
    q1 = discord.ui.TextInput(label='Имя Фамилия (IC)', placeholder='Иван Иванов', style=discord.TextStyle.short)
    q2 = discord.ui.TextInput(label='Уровень в игре', placeholder='Например: 15', style=discord.TextStyle.short)
    q3 = discord.ui.TextInput(label='Ваш реальный возраст (ООС)', placeholder='Например: 20', style=discord.TextStyle.short)
    q4 = discord.ui.TextInput(label='Как узнали о семье и почему к нам?', placeholder='Ваш ответ...', style=discord.TextStyle.paragraph)
    q5 = discord.ui.TextInput(label='Знания РП (от 0 до 10)', placeholder='Например: 8', style=discord.TextStyle.short)

    def __init__(self, app_type: str = 'Ticket'):
        super().__init__()
        self.app_type = app_type

    async def on_submit(self, interaction: discord.Interaction):
        # Сохраняем ответы
        family_applications[interaction.user.id] = {
            'type': self.app_type,
            'name': self.q1.value,
            'level': self.q2.value,
            'age': self.q3.value,
            'why': self.q4.value,
            'rp': self.q5.value,
        }

        step2_embed = discord.Embed(
            title='✅ Шаг 1 сохранён',
            description='Нажми на кнопку ниже, чтобы перейти к заполнению **шага 2**.',
            color=0xE67E22,
        )
        step2_embed.set_footer(text='Форма заявки')

        view = TicketStageTwoView(interaction.user.id)
        await interaction.response.send_message(embed=step2_embed, view=view, ephemeral=True)


class ApplicationCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Ticket', style=discord.ButtonStyle.primary, emoji='🤝', custom_id='app_create_ticket')
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(AppModalPartOne(app_type='Ticket'))
        except discord.NotFound:
            # Interaction expired
            return
        except discord.HTTPException as exc:
            if 'already been acknowledged' in str(exc):
                try:
                    await interaction.followup.send('Не удалось открыть форму, попробуйте снова.', ephemeral=True)
                except Exception:
                    pass
            else:
                raise

    @discord.ui.button(label='VZP', style=discord.ButtonStyle.secondary, emoji='🔫', custom_id='app_create_vzp')
    async def create_vzp_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(AppModalPartOne(app_type='VZP'))
        except discord.NotFound:
            return
        except discord.HTTPException as exc:
            if 'already been acknowledged' in str(exc):
                try:
                    await interaction.followup.send('Не удалось открыть форму, попробуйте снова.', ephemeral=True)
                except Exception:
                    pass
            else:
                raise

# --------------- Заявки в рекруты удалены ---------------

# Заглушки для совместимости с Discord custom_id кэшем
class RecruitAppDecisionView(discord.ui.View):
    def __init__(self, applicant_id: int = 0):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success, emoji='✅', custom_id='recruit_app_accept')
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Эта функция больше не используется.', ephemeral=True)

    @discord.ui.button(label='❌ Отклонить', style=discord.ButtonStyle.danger, emoji='❌', custom_id='recruit_app_reject')
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Эта функция больше не используется.', ephemeral=True)


class RecruitAppBannerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Подать заявку в рекруты', style=discord.ButtonStyle.success, emoji='🪖', custom_id=RECRUIT_APP_BUTTON_ID)
    async def apply(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Система заявок в рекруты отключена.', ephemeral=True)

class AdminPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='На собрание', style=discord.ButtonStyle.danger, emoji='📢', custom_id=ADMIN_MEETING_BUTTON_ID)
    async def meeting_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message('Эта кнопка работает только на сервере.', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message('У тебя нет прав для использования этой кнопки.', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return

        meeting_role = guild.get_role(MEETING_ROLE_ID)
        target_channel = guild.get_channel(MEETING_VOICE_CHANNEL_ID)

        if not meeting_role or not isinstance(target_channel, discord.VoiceChannel):
            await interaction.followup.send('Ошибка: не удалось найти роль или голосовой канал.', ephemeral=True)
            return

        moved = 0
        failed = 0
        for member in meeting_role.members:
            if member.voice and member.voice.channel:
                if member.voice.channel.id != MEETING_VOICE_CHANNEL_ID:
                    try:
                        await member.move_to(target_channel, reason='Собрание')
                        moved += 1
                    except (discord.Forbidden, discord.HTTPException):
                        failed += 1

        desc = f'Перемещено: **{moved}**'
        if failed:
            desc += f'\nНе удалось: **{failed}**'
        if moved == 0:
            desc = 'Нет участников с ролью в голосовых каналах.'

        await interaction.followup.send(desc, ephemeral=True)

        asyncio.create_task(send_log(
            '📢 На собрание',
            description=desc,
            fields=[
                ('Инициатор', _log_user_field(interaction.user), True),
                ('Целевой канал', _log_channel_field(target_channel), True),
            ],
            color=0xEF4444, user=interaction.user,
        ))

    @discord.ui.button(label='1 час до Собрания', style=discord.ButtonStyle.primary, emoji='⏰', custom_id=ADMIN_REMIND_1H_BUTTON_ID)
    async def remind_1h_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message('Эта кнопка работает только на сервере.', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message('У тебя нет прав для использования этой кнопки.', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return

        meeting_role = guild.get_role(MEETING_ROLE_ID)
        if not meeting_role:
            await interaction.followup.send('Ошибка: не удалось найти роль собрания.', ephemeral=True)
            return

        dm_embed = discord.Embed(
            title='📢 Внимание — Собрание через час!',
            description=(
                'Здравствуй!\n\n'
                'Через **1 час** начинается наше **Собрание**.\n'
                'Пожалуйста, будь в голосовом канале — ждём тебя!\n\n'
                '🎙️ До встречи!'
            ),
            color=0xF59E0B,
            timestamp=discord.utils.utcnow(),
        )
        dm_embed.set_thumbnail(url=THUMBNAIL_URL)
        dm_embed.set_footer(text='CENT — Собрание')

        sent = 0
        failed = 0
        for member in meeting_role.members:
            try:
                await member.send(embed=dm_embed)
                sent += 1
            except (discord.Forbidden, discord.HTTPException):
                failed += 1

        desc = f'Уведомления отправлены: **{sent}**'
        if failed:
            desc += f'\nНе удалось (ЛС закрыты): **{failed}**'
        if sent == 0:
            desc = 'Нет участников с ролью для отправки уведомлений.'

        await interaction.followup.send(desc, ephemeral=True)

        asyncio.create_task(send_log(
            '⏰ Напоминание: Собрание через час',
            description=desc,
            fields=[
                ('Инициатор', _log_user_field(interaction.user), True),
                ('Роль', f'<@&{MEETING_ROLE_ID}>', True),
            ],
            color=0xF59E0B, user=interaction.user,
        ))

    @discord.ui.button(label='На собрание (СМС)', style=discord.ButtonStyle.success, emoji='💬', custom_id=ADMIN_MEETING_SMS_BUTTON_ID)
    async def meeting_sms_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message('Эта кнопка работает только на сервере.', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message('У тебя нет прав для использования этой кнопки.', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return

        meeting_role = guild.get_role(MEETING_ROLE_ID)
        if not meeting_role:
            await interaction.followup.send('Ошибка: не удалось найти роль собрания.', ephemeral=True)
            return

        sms_embed = discord.Embed(
            title='📢 Собрание началось!',
            description=(
                '**Переходите в канал собрания!**\n\n'
                'Все участники с ролью приглашаются присоединиться.\n'
                '🎙️ Ждём вас!'
            ),
            color=0xEF4444,
            timestamp=discord.utils.utcnow(),
        )
        sms_embed.set_thumbnail(url=THUMBNAIL_URL)
        sms_embed.set_footer(text='CENT — Собрание')

        sent = 0
        failed = 0
        for member in meeting_role.members:
            if member.bot:
                continue
            try:
                await member.send(embed=sms_embed)
                sent += 1
            except (discord.Forbidden, discord.HTTPException):
                failed += 1

        desc = f'ЛС отправлено: **{sent}**'
        if failed:
            desc += f'\nНе удалось (ЛС закрыты): **{failed}**'
        if sent == 0:
            desc = 'Нет участников для отправки.'

        await interaction.followup.send(desc, ephemeral=True)

        asyncio.create_task(send_log(
            '💬 На собрание (СМС)',
            description=desc,
            fields=[
                ('Инициатор', _log_user_field(interaction.user), True),
                ('Роль', f'<@&{MEETING_ROLE_ID}>', True),
            ],
            color=0x10B981, user=interaction.user,
        ))

    @discord.ui.button(label='Объявление', style=discord.ButtonStyle.primary, emoji='📣', custom_id=ANNOUNCEMENT_BUTTON_ID, row=1)
    async def announcement_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message('У тебя нет прав.', ephemeral=True)
            return
        await interaction.response.send_modal(AnnouncementModal())

class LeaderboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.page = 0
        self.category = 'messages'

    def build_embed(self, guild: discord.Guild) -> discord.Embed:
        state = read_stats_state()
        category_labels = {
            'messages': '📝 Сообщения',
            'voice': '🔊 Голосовое время',
            'commands': '⚡ Команды',
        }
        stat_data = state.get(self.category, {})
        sorted_users = sorted(stat_data.items(), key=lambda x: int(x[1]), reverse=True)[:10]

        lines = []
        medals = ['🥇', '🥈', '🥉']
        for i, (user_id_str, value) in enumerate(sorted_users):
            member = guild.get_member(int(user_id_str))
            name = member.display_name if member else f'ID: {user_id_str}'
            medal = medals[i] if i < 3 else f'**{i+1}.**'
            if self.category == 'voice':
                val_str = format_voice_time(int(value))
            else:
                val_str = f'{int(value):,}'
            lines.append(f'{medal} {name} — {val_str}')

        description = '\n'.join(lines) if lines else '*Пока нет данных*'
        embed = discord.Embed(
            title=f'🏆 Таблица лидеров — {category_labels.get(self.category, self.category)}',
            description=description,
            color=0xF59E0B,
        )
        embed.set_footer(text=f'Страница {self.page + 1}')
        return embed

    @discord.ui.select(
        placeholder='Выбери категорию',
        options=[
            discord.SelectOption(label='Сообщения', value='messages', emoji='📝'),
            discord.SelectOption(label='Голос', value='voice', emoji='🔊'),
            discord.SelectOption(label='Команды', value='commands', emoji='⚡'),
        ],
        custom_id='leaderboard_category',
    )
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.category = select.values[0]
        self.page = 0
        embed = self.build_embed(interaction.guild)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='◄', style=discord.ButtonStyle.secondary, custom_id=LEADERBOARD_PREV_BUTTON_ID)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
        embed = self.build_embed(interaction.guild)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='►', style=discord.ButtonStyle.secondary, custom_id=LEADERBOARD_NEXT_BUTTON_ID)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        embed = self.build_embed(interaction.guild)
        await interaction.response.edit_message(embed=embed, view=self)

class FamilyBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix='!', intents=intents)
        self.refresh_lock = asyncio.Lock()
        self.recruit_lock = asyncio.Lock()
        self.birthday_lock = asyncio.Lock()

        self.recruit_app_lock = asyncio.Lock()
        self.invite_cache: dict[int, dict[str, int]] = {}

        self.stats_voice_sessions: dict[int, float] = {}

    async def setup_hook(self) -> None:
        self.add_view(RefreshView())
        self.add_view(RecruitView())
        self.add_view(RecruitReportButtonView())
        self.add_view(BirthdayButtonView())
        self.add_view(BlacklistView())
        self.add_view(ApplicationCreateView())
        self.add_view(TicketAdminView())
        self.add_view(RecruitAppBannerView())
        self.add_view(AdminPanelView())
        self.add_view(LeaderboardView())

bot = FamilyBot()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}

def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def read_verification_state() -> dict:
    env_msg = os.getenv('VERIFICATION_MESSAGE_ID', '')
    env_ch = os.getenv('VERIFICATION_CHANNEL_ID', '')
    env_guild = os.getenv('VERIFICATION_GUILD_ID', '')
    if env_msg and env_ch and env_guild:
        return {
            'guild_id': int(env_guild),
            'channel_id': int(env_ch),
            'message_id': int(env_msg),
        }
    return read_json(VERIFICATION_STATE_FILE)

def write_verification_state(data: dict) -> None:
    write_json(VERIFICATION_STATE_FILE, data)

def read_state() -> dict:
    return read_json(STATE_FILE)

def write_state(data: dict) -> None:
    write_json(STATE_FILE, data)

def read_recruit_state() -> dict:
    state = read_json(RECRUIT_STATE_FILE)
    state.setdefault('recruits', {})
    state.setdefault('accepted_members', {})
    return state

def write_recruit_state(data: dict) -> None:
    write_json(RECRUIT_STATE_FILE, data)

def read_birthday_state() -> dict:
    state = read_json(BIRTHDAY_STATE_FILE)
    state.setdefault('entries', {})
    return state

def write_birthday_state(data: dict) -> None:
    write_json(BIRTHDAY_STATE_FILE, data)



def read_app_state() -> dict:
    state = read_json(APP_STATE_FILE)
    state.setdefault('message_id', None)
    return state

def write_app_state(data: dict) -> None:
    write_json(APP_STATE_FILE, data)

def read_recruit_app_state() -> dict:
    state = read_json(RECRUIT_APP_STATE_FILE)
    state.setdefault('banner_message_id', None)
    state.setdefault('applications', {})
    return state

def write_recruit_app_state(data: dict) -> None:
    write_json(RECRUIT_APP_STATE_FILE, data)

def read_stats_state() -> dict:
    state = read_json(STATS_STATE_FILE)
    state.setdefault('messages', {})
    state.setdefault('voice', {})
    state.setdefault('voice_sessions', {})
    state.setdefault('commands', {})
    return state

def write_stats_state(data: dict) -> None:
    write_json(STATS_STATE_FILE, data)

def read_reminders_state() -> dict:
    state = read_json(REMINDERS_STATE_FILE)
    state.setdefault('reminders', [])
    return state

def write_reminders_state(data: dict) -> None:
    write_json(REMINDERS_STATE_FILE, data)

def parse_birthday_text(raw: str) -> Optional[dict]:
    text = raw.strip().replace('/', '.').replace('-', '.')
    parts = [p.strip() for p in text.split('.') if p.strip()]
    if len(parts) not in (2, 3):
        return None
    if not all(part.isdigit() for part in parts):
        return None
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2]) if len(parts) == 3 else None
    if not 1 <= day <= 31 or not 1 <= month <= 12:
        return None
    if year is not None and not 1900 <= year <= 2100:
        return None
    text = f'{day:02d}.{month:02d}' + (f'.{year:04d}' if year is not None else '')
    result = {'day': day, 'month': month, 'text': text}
    if year is not None:
        result['year'] = year
    return result

def calculate_age(year: Optional[int], month: int, day: int) -> Optional[int]:
    if year is None:
        return None
    today = discord.utils.utcnow().date()
    age = today.year - int(year)
    if (today.month, today.day) < (month, day):
        age -= 1
    return age

def age_suffix(age: int) -> str:
    if age % 10 == 1 and age % 100 != 11:
        return 'год'
    if age % 10 in (2, 3, 4) and age % 100 not in (12, 13, 14):
        return 'года'
    return 'лет'

def parse_relative_time(text: str) -> Optional[timedelta]:
    """Парсит относительное время: 30m, 2h, 1d, 1w, 30мин, 2часа, 1день."""
    text = text.strip().lower()
    patterns = [
        (r'^(\d+)\s*(?:m|min|мин|минут)$', 'm'),
        (r'^(\d+)\s*(?:h|hr|ч|час(?:а|ов)?)$', 'h'),
        (r'^(\d+)\s*(?:d|д|день|дня|дней)$', 'd'),
        (r'^(\d+)\s*(?:w|н|недел[яьи]|недель)$', 'w'),
    ]
    for pattern, unit in patterns:
        match = re.match(pattern, text)
        if match:
            value = int(match.group(1))
            if unit == 'm':
                return timedelta(minutes=value)
            elif unit == 'h':
                return timedelta(hours=value)
            elif unit == 'd':
                return timedelta(days=value)
            elif unit == 'w':
                return timedelta(weeks=value)
    return None

def format_voice_time(seconds: int) -> str:
    """Форматирует секунды в читаемый вид: '2ч 15м', '45м', '1ч 02м'."""
    if seconds < 60:
        return f'{seconds}с'
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f'{hours}ч {minutes:02d}м'
    return f'{minutes}м'

def format_birthday_line(member: discord.Member | None, user_id: int, entry: dict) -> str:
    display = f'<@{user_id}>' if member is None else format_member(member)
    month = int(entry.get('month', 0) or 0)
    day = int(entry.get('day', 0) or 0)
    year = int(entry['year']) if entry.get('year') is not None else None
    age = calculate_age(year, month, day) if month and day else None
    line = f'{display} — {entry.get("text", "??.??")}'
    if age is not None:
        line += f' ({age} {age_suffix(age)})'
    return line

def birthday_sort_key(item: tuple[int, dict], guild: discord.Guild) -> tuple[int, int, int, str]:
    user_id, entry = item
    member = guild.get_member(user_id)
    month = int(entry.get('month', 0) or 0)
    day = int(entry.get('day', 0) or 0)
    year = int(entry['year']) if entry.get('year') is not None else 0
    name = member.display_name.casefold() if member else str(user_id)
    return (month, day, year, name)

def format_member(member: discord.Member) -> str:
    return f'<@{member.id}>'

def sort_members(members):
    return sorted(members, key=lambda m: m.display_name.casefold())

def has_recruit_role(member: discord.Member) -> bool:
    """Allow anyone with the recruit role or any role above it in ROLE_ORDER."""
    role_ids_in_order = [r.role_id for r in ROLE_ORDER]
    try:
        recruit_index = role_ids_in_order.index(RECRUIT_ROLE_ID)
    except ValueError:
        return any(role.id == RECRUIT_ROLE_ID for role in member.roles)

    member_role_ids = {role.id for role in member.roles}
    # Check if member has the recruit role OR any role higher in ROLE_ORDER
    for idx, rid in enumerate(role_ids_in_order):
        if idx <= recruit_index and rid in member_role_ids:
            return True
    return False


async def get_text_channel(channel_id: int) -> discord.TextChannel:
    channel = bot.get_channel(channel_id)
    if channel is None:
        channel = await bot.fetch_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        raise RuntimeError('Target channel is not a text channel or was not found.')
    return channel


# --------------- Логирование (компактный единый стиль) ---------------

def _format_log_time(dt: datetime | None = None) -> str:
    """Формат времени как на картинке: «Сегодня, в 21:23» / «Вчера, в ...» / «05.07.2026, в ...»."""
    dt = dt or discord.utils.utcnow()
    today = discord.utils.utcnow().date()
    if dt.date() == today:
        day = 'Сегодня'
    elif (today - dt.date()).days == 1:
        day = 'Вчера'
    else:
        day = dt.strftime('%d.%m.%Y')
    return f'{day}, в {dt.strftime("%H:%M")}'


async def send_log(
    title: str,
    description: str | None = None,
    *,
    color: int = 0x6366F1,
    user: discord.Member | discord.User | None = None,
    fields: list[tuple[str, str, bool]] | None = None,
    thumbnail: str | None = None,
) -> None:
    """
    Компактный лог в едином стиле.
    - title:     заголовок-событие (например «🔊 Подключился к голосовому»)
    - fields:    список (название, значение, inline) — например Участник / Канал
    - user:      участник (аватар сбоку + ID в футере)
    - thumbnail: маленькая картинка сбоку
    """
    if not LOG_CHANNEL_ID:
        return
    try:
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel is None:
            channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        if not isinstance(channel, discord.TextChannel):
            return

        embed = discord.Embed(title=title, color=color)
        if description:
            embed.description = description

        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

        # Футер: время + ID (как на картинке)
        footer_parts = [_format_log_time()]
        if user is not None:
            footer_parts.append(f'ID: {user.id}')
        embed.set_footer(text=' • '.join(footer_parts))

        # Аватар сбоку
        if user is not None and user.display_avatar:
            embed.set_thumbnail(url=user.display_avatar.url)
        elif thumbnail:
            embed.set_thumbnail(url=thumbnail)

        await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
    except Exception as exc:
        print(f'[LOG ERROR] Could not send log: {exc}')


def _log_user_field(user: discord.Member | discord.User) -> str:
    """Поле «Участник» в формате: @упоминание (ID)."""
    return f'{user.mention} (`{user.id}`)'


def _log_channel_field(channel: discord.abc.GuildChannel | None) -> str | None:
    """Поле «Канал» в формате: #имя (ID). Если канала нет — None."""
    if channel is None:
        return None
    return f'{channel.mention} (`{channel.id}`)'

async def fetch_invites(guild: discord.Guild) -> dict[str, discord.Invite]:
    invites = await guild.invites()
    return {invite.code: invite for invite in invites}

async def update_invite_cache(guild: discord.Guild) -> dict[str, discord.Invite]:
    invites = await fetch_invites(guild)
    bot.invite_cache[guild.id] = {code: invite.uses or 0 for code, invite in invites.items()}
    return invites

async def fetch_guild_members(guild: discord.Guild) -> list[discord.Member]:
    try:
        await asyncio.sleep(2)
        return [m async for m in guild.fetch_members(limit=None)]
    except Exception as exc:
        print(f'fetch_members error: {exc}')
        return []


def filter_members_by_role(members: list[discord.Member], role_id: int) -> list[discord.Member]:
    return [m for m in members if any(r.id == role_id for r in m.roles)]


async def build_payload(guild: discord.Guild) -> tuple[discord.Embed, discord.ui.View]:
    all_members = await fetch_guild_members(guild)
    seen: set[int] = set()
    sections = []
    for role_info in ROLE_ORDER:
        all_with_role = filter_members_by_role(all_members, role_info.role_id)
        filtered = [m for m in all_with_role if m.id not in seen]
        seen.update(m.id for m in all_with_role)
        members = sort_members(filtered)

        count = len(all_with_role) if role_info.role_id == CENT_ROLE_ID else len(members)
        header = f'{role_info.label} ({count})'
        if role_info.count_only:
            sections.append(header)
            continue
        body = '\n'.join(f'• {format_member(member)}' for member in members) if members else '• нет участников'
        sections.append(f'{header}\n{body}')

    embed = discord.Embed(title=f'👥 Состав семьи {guild.name}', description='\n\n'.join(sections), color=0xF59E0B)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_image(url=MAIN_IMAGE_URL)
    embed.set_footer(text='Автообновление каждые 5 минут')
    embed.timestamp = discord.utils.utcnow()
    return embed, RefreshView()

async def create_or_get_recruit_invite(member: discord.Member) -> dict:
    async with bot.recruit_lock:
        state = read_recruit_state()
        recruiter_id = str(member.id)
        record = state['recruits'].get(recruiter_id)
        if record and record.get('invite_url'):
            return record

        channel = await get_text_channel(INVITE_CHANNEL_ID)
        invite = await channel.create_invite(max_age=0, max_uses=0, unique=True, reason=f'Personal recruit invite for {member} ({member.id})')
        record = {
            'member_id': member.id,
            'invite_code': invite.code,
            'invite_url': invite.url,
            'accepted_count': invite.uses or 0,
            'created_at': discord.utils.utcnow().isoformat(),
        }
        state['recruits'][recruiter_id] = record
        write_recruit_state(state)
        await update_invite_cache(member.guild)
        return record

async def build_recruit_payload(guild: discord.Guild) -> tuple[discord.Embed, discord.ui.View]:
    all_members = await fetch_guild_members(guild)
    higher_role_ids = {r.role_id for r in ROLE_ORDER if r.role_id != CENT_ROLE_ID}
    recruit_members = filter_members_by_role(all_members, RECRUIT_ROLE_ID)
    recruits = sort_members([
        m for m in recruit_members
        if not any(r.id in higher_role_ids for r in m.roles)
    ])
    count = len(recruits)

    header = f'Рекруты ({count})'
    body = '\n'.join(f'• {format_member(member)}' for member in recruits) if recruits else '• нет участников'
    description = f'{header}\n{body}'

    if len(description) > 3900:
        description = description[:3900] + '\n\nСписок слишком длинный, часть рекрутов скрыта.'

    embed = discord.Embed(title=f'👥 Состав-отдела Рекрутов', description=description, color=0x00E3FF)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_image(url=MAIN_IMAGE_URL)
    embed.set_footer(text='Автообновление каждые 5 минут')
    embed.timestamp = discord.utils.utcnow()
    return embed, RecruitRefreshView()

def build_report_button_payload() -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title='📝 Отписать приглашённого',
        description='Нажми кнопку ниже и заполни форму: имя фамилия и номер паспорта.',
        color=0x38BDF8,
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text='Форма доступна только рекрутам')
    return embed, RecruitReportButtonView()

async def refresh_report_button_message() -> None:
    channel = await get_text_channel(RECRUIT_REPORT_CHANNEL_ID)
    embed, view = build_report_button_payload()
    state = read_json(REPORT_BUTTON_STATE_FILE)
    message = None
    if state.get('message_id'):
        try:
            message = await channel.fetch_message(int(state['message_id']))
        except Exception:
            message = None
    if message is None:
        try:
            async for msg in channel.history(limit=50, oldest_first=False):
                if msg.author == bot.user and msg.embeds and msg.embeds[0].title == embed.title:
                    message = msg
                    break
        except Exception:
            pass
    if message is None:
        message = await channel.send(embed=embed, view=view)
    else:
        await message.edit(embed=embed, view=view)
    write_json(REPORT_BUTTON_STATE_FILE, {
        'message_id': message.id,
        'channel_id': channel.id,
        'updated_at': discord.utils.utcnow().isoformat(),
    })

async def refresh_report_button_message_safely() -> None:
    try:
        await refresh_report_button_message()
    except Exception as exc:
        print(f'Report button refresh failed: {exc}')


def build_birthday_payload(guild: discord.Guild) -> tuple[discord.Embed, discord.ui.View]:
    state = read_birthday_state()
    entries = []
    for user_id_str, entry in state['entries'].items():
        try:
            user_id = int(user_id_str)
        except ValueError:
            continue
        entries.append((user_id, entry))

    entries.sort(key=lambda item: birthday_sort_key(item, guild))
    lines = []
    for user_id, entry in entries:
        member = guild.get_member(user_id)
        lines.append(f'• {format_birthday_line(member, user_id, entry)}')

    description = '\n'.join(lines) if lines else 'Пока никто не добавил дату рождения.'
    if len(description) > 3900:
        description = description[:3900] + '\n\nСписок слишком длинный, часть записей скрыта.'

    embed = discord.Embed(title='🎂 Список дней рождения', description=description, color=0xF97316)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text='Нажми кнопку, чтобы добавить или обновить свою дату')
    embed.timestamp = discord.utils.utcnow()
    return embed, BirthdayButtonView()

async def refresh_birthday_board() -> None:
    if not BIRTHDAY_BOARD_CHANNEL_ID:
        return
    channel = await get_text_channel(BIRTHDAY_BOARD_CHANNEL_ID)
    embed, view = build_birthday_payload(channel.guild)
    state = read_birthday_state()
    message = None
    if state.get('message_id'):
        try:
            message = await channel.fetch_message(int(state['message_id']))
        except Exception:
            message = None
    if message is None:
        try:
            async for msg in channel.history(limit=50, oldest_first=False):
                if msg.author == bot.user and msg.embeds and msg.embeds[0].title == embed.title:
                    message = msg
                    break
        except Exception:
            pass
    if message is None:
        message = await channel.send(embed=embed, view=view)
    else:
        await message.edit(embed=embed, view=view)
    state['message_id'] = message.id
    state['channel_id'] = channel.id
    state['updated_at'] = discord.utils.utcnow().isoformat()
    write_birthday_state(state)

async def refresh_birthday_board_safely() -> None:
    try:
        await refresh_birthday_board()
    except Exception as exc:
        print(f'Birthday board refresh failed: {exc}')


GREETED_TODAY: set[int] = set()

async def auto_birthday_greeting() -> None:
    """Каждый час проверяет — чей сегодня день рождения, и поздравляет."""
    if not BIRTHDAY_GREETING_CHANNEL_ID:
        return
    while True:
        await asyncio.sleep(60 * 60)
        try:
            today = discord.utils.utcnow()
            today_day = today.day
            today_month = today.month

            state = read_birthday_state()
            entries = state.get('entries', {})

            channel = bot.get_channel(BIRTHDAY_GREETING_CHANNEL_ID)
            if not channel:
                channel = await bot.fetch_channel(BIRTHDAY_GREETING_CHANNEL_ID)
            if not isinstance(channel, discord.TextChannel):
                continue

            for user_id_str, entry in entries.items():
                user_id = int(user_id_str)
                if entry.get('day') == today_day and entry.get('month') == today_month:
                    if user_id in GREETED_TODAY:
                        continue

                    member = channel.guild.get_member(user_id)
                    if not member:
                        continue

                    year = entry.get('year')
                    age_text = ''
                    if year:
                        age = calculate_age(year, today_month, today_day)
                        if age is not None:
                            age_text = f'\n🎉 С днём рождения! Тебе **{age}** {age_suffix(age)}!'

                    embed = discord.Embed(
                        title='🎂 С Днём Рождения!',
                        description=(
                            f'{member.mention}, поздравляем тебя с днём рождения! 🎉\n\n'
                            f'Желаем тебе счастья, здоровья и удачи! 🥳🎊'
                            f'{age_text}'
                        ),
                        color=0xF97316,
                        timestamp=discord.utils.utcnow(),
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text='С любовью, CENT Family 💛')

                    try:
                        await channel.send(content=member.mention, embed=embed)
                        GREETED_TODAY.add(user_id)
                        print(f'[BIRTHDAY] Greeted {member.display_name} in #{channel.name}')
                    except Exception as exc:
                        print(f'[BIRTHDAY] Failed to greet {member}: {exc}')

            # Сброс приветствий в полночь
            if today.hour == 0 and len(GREETED_TODAY) > 0:
                GREETED_TODAY.clear()

        except Exception as exc:
            print(f'[BIRTHDAY] Auto-greeting error: {exc}')


async def refresh_board() -> None:
    async with bot.refresh_lock:
        channel = await get_text_channel(TARGET_CHANNEL_ID)
        embed, view = await build_payload(channel.guild)
        state = read_state()
        message = None
        if state.get('message_id'):
            try:
                message = await channel.fetch_message(int(state['message_id']))
            except Exception:
                message = None
        if message is None:
            try:
                async for msg in channel.history(limit=50, oldest_first=False):
                    if msg.author == bot.user and msg.embeds and msg.embeds[0].title == embed.title:
                        message = msg
                        break
            except Exception:
                pass
        if message is None:
            message = await channel.send(embed=embed, view=view)
        else:
            await message.edit(embed=embed, view=view)
        write_state({'message_id': message.id, 'channel_id': channel.id, 'updated_at': discord.utils.utcnow().isoformat()})

async def refresh_recruit_board() -> None:
    async with bot.recruit_lock:
        channel = await get_text_channel(RECRUIT_BOARD_CHANNEL_ID)
        embed, view = await build_recruit_payload(channel.guild)
        state = read_recruit_state()
        message = None
        # Try to find message by stored ID
        if state.get('board_message_id'):
            try:
                message = await channel.fetch_message(int(state['board_message_id']))
            except Exception:
                message = None
        # If not found, search channel for bot's last embed message with this title
        if message is None:
            try:
                async for msg in channel.history(limit=50, oldest_first=False):
                    if msg.author == bot.user and msg.embeds and msg.embeds[0].title == embed.title:
                        message = msg
                        break
            except Exception:
                pass
        if message is None:
            message = await channel.send(embed=embed, view=view)
        else:
            await message.edit(embed=embed, view=view)
        state['board_message_id'] = message.id
        state['board_channel_id'] = channel.id
        state['updated_at'] = discord.utils.utcnow().isoformat()
        write_recruit_state(state)

async def refresh_board_safely() -> None:
    try:
        await refresh_board()
    except Exception as exc:
        print(f'Family board refresh failed: {exc}')

async def refresh_recruit_board_safely() -> None:
    try:
        await refresh_recruit_board()
    except Exception as exc:
        print(f'Recruit board refresh failed: {exc}')


async def refresh_blacklist_message() -> None:
    channel = await get_text_channel(BLACKLIST_CHANNEL_ID)
    embed = discord.Embed(
        title='🚫 Чёрный список CENT Family',
        description='Нажми кнопку ниже, чтобы добавить участника в чёрный список.',
        color=0xEF4444,
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text='Форма доступна всем участникам')
    view = BlacklistView()

    state = read_json(BLACKLIST_STATE_FILE)
    message = None
    if state.get('message_id'):
        try:
            message = await channel.fetch_message(int(state['message_id']))
        except Exception:
            message = None
    if message is None:
        try:
            async for msg in channel.history(limit=50, oldest_first=False):
                if msg.author == bot.user and msg.embeds and msg.embeds[0].title == embed.title:
                    message = msg
                    break
        except Exception:
            pass
    if message is None:
        message = await channel.send(embed=embed, view=view)
    else:
        await message.edit(embed=embed, view=view)
    write_json(BLACKLIST_STATE_FILE, {
        'message_id': message.id,
        'channel_id': channel.id,
        'updated_at': discord.utils.utcnow().isoformat(),
    })


async def refresh_blacklist_safely() -> None:
    try:
        await refresh_blacklist_message()
    except Exception as exc:
        print(f'Blacklist refresh failed: {exc}')



async def refresh_application_board() -> None:
    if not APP_CREATE_CHANNEL_ID: return
    channel = await get_text_channel(APP_CREATE_CHANNEL_ID)
    state = read_app_state()

    embed = discord.Embed(
        title='Вступление в семью CENT',
        description='Выберите тип заявки:',
        color=0xE67E22,
    )
    view = ApplicationCreateView()

    file = None
    if CENT_IMAGE_FILE.is_file():
        file = discord.File(CENT_IMAGE_FILE, filename='cent.png')
        embed.set_image(url='attachment://cent.png')
    elif BOT_IMAGE_URL:
        embed.set_image(url=BOT_IMAGE_URL)

    msg_id = state.get('message_id')
    message = None
    if msg_id:
        try:
            message = await channel.fetch_message(int(msg_id))
        except Exception:
            pass

    if message is None:
        try:
            async for msg in channel.history(limit=50, oldest_first=False):
                if msg.author == bot.user and msg.embeds and msg.embeds[0].title == embed.title:
                    message = msg
                    break
        except Exception:
            pass

    if message is None:
        if file:
            message = await channel.send(embed=embed, file=file, view=view)
        else:
            message = await channel.send(embed=embed, view=view)
    else:
        if file:
            message = await message.edit(embed=embed, attachments=[file], view=view)
        else:
            message = await message.edit(embed=embed, view=view)

    state['message_id'] = message.id
    write_app_state(state)

async def refresh_application_board_safely() -> None:
    try:
        await refresh_application_board()
    except Exception as exc:
        print(f'App board refresh error: {exc}')


async def refresh_recruit_app_banner() -> None:
    if not RECRUIT_APP_BANNER_CHANNEL_ID:
        return
    channel = await get_text_channel(RECRUIT_APP_BANNER_CHANNEL_ID)
    state = read_recruit_app_state()

    embed = discord.Embed(
        title='🪖 Заявка в рекруты',
        description='Хочешь стать рекрутом семьи?\nНажми кнопку **Подать заявку** и заполни форму.\n\n'
                    'Твоя заявка будет рассмотрена администрацией.',
        color=0x22C55E,
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text='Требуется роль выше Рекрута для принятия/отклонения')
    embed.timestamp = discord.utils.utcnow()

    view = RecruitAppBannerView()
    message = None
    if state.get('banner_message_id'):
        try:
            message = await channel.fetch_message(int(state['banner_message_id']))
        except Exception:
            message = None
    if message is None:
        try:
            async for msg in channel.history(limit=50, oldest_first=False):
                if msg.author == bot.user and msg.embeds and msg.embeds[0].title == embed.title:
                    message = msg
                    break
        except Exception:
            pass
    if message is None:
        message = await channel.send(embed=embed, view=view)
    else:
        await message.edit(embed=embed, view=view)
    state['banner_message_id'] = message.id
    write_recruit_app_state(state)


async def refresh_recruit_app_banner_safely() -> None:
    try:
        await refresh_recruit_app_banner()
    except Exception as exc:
        print(f'Recruit app banner refresh error: {exc}')


ADMIN_PANEL_STATE_FILE = Path(__file__).with_name('admin-panel-state.json')

def read_admin_panel_state() -> dict:
    state = read_json(ADMIN_PANEL_STATE_FILE)
    state.setdefault('message_id', None)
    return state

def write_admin_panel_state(data: dict) -> None:
    write_json(ADMIN_PANEL_STATE_FILE, data)


async def refresh_admin_panel() -> None:
    if not ADMIN_PANEL_CHANNEL_ID:
        return
    channel = await get_text_channel(ADMIN_PANEL_CHANNEL_ID)

    embed = discord.Embed(
        title='⚙️ Панель управления',
        description=(
            '**На собрание** — переместит всех участников с ролью '
            f'<@&{MEETING_ROLE_ID}> в голосовой канал <#{MEETING_VOICE_CHANNEL_ID}>.\n\n'
            '**1 час до Собрания** — отправит ЛС-уведомление всем участникам с ролью '
            f'<@&{MEETING_ROLE_ID}>.\n\n'
            '**Объявление** — отправит красивый embed в любой канал.\n\n'
            'Кнопки доступны только администрации (Manage Server).'
        ),
        color=0xEF4444,
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.timestamp = discord.utils.utcnow()

    view = AdminPanelView()
    state = read_admin_panel_state()
    message = None

    if state.get('message_id'):
        try:
            message = await channel.fetch_message(int(state['message_id']))
        except discord.NotFound:
            print(f'[ADMIN] Panel message {state["message_id"]} not found — creating new')
            state['message_id'] = None
            write_admin_panel_state(state)
        except discord.HTTPException as exc:
            print(f'[ADMIN] Failed to fetch panel message: {exc}')

    if message is None:
        try:
            async for msg in channel.history(limit=50, oldest_first=False):
                if msg.author == bot.user and msg.embeds and msg.embeds[0].title == embed.title:
                    message = msg
                    break
        except Exception:
            pass

    if message is None:
        message = await channel.send(embed=embed, view=view)
    else:
        await message.edit(embed=embed, view=view)

    state['message_id'] = message.id
    state['channel_id'] = channel.id
    state['updated_at'] = discord.utils.utcnow().isoformat()
    write_admin_panel_state(state)


async def refresh_admin_panel_safely() -> None:
    try:
        await refresh_admin_panel()
    except Exception as exc:
        print(f'Admin panel refresh error: {exc}')


async def track_member_invite(member: discord.Member) -> None:
    try:
        current_invites = await fetch_invites(member.guild)
    except Exception as exc:
        print(f'Could not check invite use for {member}: {exc}')
        return

    previous = bot.invite_cache.get(member.guild.id, {})
    used_code = None
    for code, invite in current_invites.items():
        old_uses = previous.get(code, 0)
        new_uses = invite.uses or 0
        if new_uses > old_uses:
            used_code = code
            break

    bot.invite_cache[member.guild.id] = {code: invite.uses or 0 for code, invite in current_invites.items()}
    if not used_code:
        asyncio.create_task(send_log(
            '👋 Новый участник',
            fields=[
                ('Участник', _log_user_field(member), True),
                ('Источник', '**не определён**', True),
            ],
            color=0xA855F7, user=member,
        ))
        return

    recruiter_name = None
    async with bot.recruit_lock:
        state = read_recruit_state()
        for recruiter_id, record in state['recruits'].items():
            if record.get('invite_code') == used_code:
                record['accepted_count'] = max(int(record.get('accepted_count', 0)) + 1, current_invites[used_code].uses or 0)
                state['accepted_members'][str(member.id)] = {'recruiter_id': recruiter_id, 'joined_at': discord.utils.utcnow().isoformat()}
                write_recruit_state(state)
                recruiter_member = member.guild.get_member(int(recruiter_id))
                recruiter_name = recruiter_member.mention if recruiter_member else f'<@{recruiter_id}>'
                break

    if recruiter_name:
        asyncio.create_task(send_log(
            '👋 Новый участник (по ссылке рекрута)',
            fields=[
                ('Участник', _log_user_field(member), True),
                ('Пригласил', recruiter_name, True),
                ('Код ссылки', f'`{used_code}`', False),
            ],
            color=0x22C55E, user=member,
        ))
    else:
        asyncio.create_task(send_log(
            '👋 Новый участник',
            fields=[
                ('Участник', _log_user_field(member), True),
                ('Ссылка', f'`{used_code}` (без рекрута)', True),
            ],
            color=0xA855F7, user=member,
        ))

    await refresh_recruit_board_safely()

@bot.event
async def on_ready() -> None:
    print(f'Logged in as {bot.user.id}')
    for guild in bot.guilds:
        print(f'Guild: {guild.name} ({guild.id}) - {guild.member_count} members')
        try:
            await update_invite_cache(guild)
        except Exception as exc:
            print(f'Invite cache failed for {guild}: {exc}')
    try:
        if not auto_refresh.is_running():
            auto_refresh.start()
    except Exception as exc:
        print(f'auto_refresh start failed: {exc}')
    asyncio.create_task(refresh_board_safely())
    asyncio.create_task(refresh_recruit_board_safely())
    asyncio.create_task(refresh_report_button_message_safely())
    asyncio.create_task(refresh_birthday_board_safely())
    asyncio.create_task(auto_birthday_greeting())
    asyncio.create_task(refresh_application_board_safely())
    asyncio.create_task(refresh_recruit_app_banner_safely())
    asyncio.create_task(refresh_admin_panel_safely())
    asyncio.create_task(refresh_blacklist_safely())
    await asyncio.sleep(2)
    print('All on_ready tasks launched')
    try:
        await send_log(
            '🟢 Бот запущен',
            f'**{bot.user}** успешно подключился\n'
            f'Серверов: **{len(bot.guilds)}**\n'
            f'Пинг: **{round(bot.latency * 1000)}** мс',
            color=0x10B981,
        )
    except Exception as exc:
        print(f'send_log on startup failed: {exc}')

@bot.event
async def on_member_join(member: discord.Member) -> None:
    await track_member_invite(member)
    asyncio.create_task(send_welcome_message(member))
    asyncio.create_task(check_raid(member))

    # Лог входа
    account_age = (discord.utils.utcnow() - member.created_at).days
    fields = [
        ('Участник', _log_user_field(member), True),
        ('Аккаунт создан', f'{account_age} дн. назад', True),
        ('Участников', str(member.guild.member_count), True),
    ]

    asyncio.create_task(send_log(
        '📥 Участник вошёл',
        fields=fields,
        color=0x00FF00, user=member,
    ))





@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot or message.guild is None:
        return

    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    """Give the verification role after a user reacts to the configured message."""
    if payload.guild_id is None or bot.user is None or payload.user_id == bot.user.id:
        return

    state = read_verification_state()
    if (
        payload.guild_id != state.get('guild_id')
        or payload.channel_id != state.get('channel_id')
        or payload.message_id != state.get('message_id')
        or str(payload.emoji) != VERIFICATION_EMOJI
    ):
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    role = guild.get_role(VERIFICATION_ROLE_ID)
    if role is None:
        print('[VERIFY] Verification role was not found. Check VERIFICATION_ROLE_ID.')
        return

    try:
        member = payload.member or guild.get_member(payload.user_id)
        if member is None:
            member = await guild.fetch_member(payload.user_id)
        if member.bot or role in member.roles:
            return
        if guild.me is None or role >= guild.me.top_role:
            print('[VERIFY] Bot role must be above the verification role.')
            return
        await member.add_roles(role, reason='Completed verification by reaction')
    except discord.Forbidden:
        print('[VERIFY] Missing Manage Roles permission.')
    except discord.HTTPException as exc:
        print(f'[VERIFY] Failed to add role: {exc}')


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
    """Remove the verification role when its reaction is removed."""
    if payload.guild_id is None or bot.user is None or payload.user_id == bot.user.id:
        return

    state = read_verification_state()
    if (
        payload.guild_id != state.get('guild_id')
        or payload.channel_id != state.get('channel_id')
        or payload.message_id != state.get('message_id')
        or str(payload.emoji) != VERIFICATION_EMOJI
    ):
        return

    print(f'[VERIFY] Reaction removed by user {payload.user_id}.')

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    role = guild.get_role(VERIFICATION_ROLE_ID)
    if role is None:
        print('[VERIFY] Verification role was not found. Check VERIFICATION_ROLE_ID.')
        return

    try:
        member = guild.get_member(payload.user_id)
        if member is None:
            member = await guild.fetch_member(payload.user_id)
        if member.bot or role not in member.roles:
            return
        await member.remove_roles(role, reason='Removed verification reaction')
        print(f'[VERIFY] Removed role from user {member.id}.')
    except discord.Forbidden:
        print('[VERIFY] Missing Manage Roles permission.')
    except discord.HTTPException as exc:
        print(f'[VERIFY] Failed to remove role: {exc}')


async def send_welcome_message(member: discord.Member) -> None:
    """Send a member join notification for senior staff with member details and CENT image."""
    print(f'[WELCOME] Triggered for {member} ({member.id})')
    if not WELCOME_CHANNEL_ID:
        print(f'[WELCOME] No WELCOME_CHANNEL_ID set')
        return
    try:
        channel = bot.get_channel(WELCOME_CHANNEL_ID)
        print(f'[WELCOME] Channel from cache: {channel}')
        if channel is None:
            channel = await bot.fetch_channel(WELCOME_CHANNEL_ID)
            print(f'[WELCOME] Channel from API: {channel}')
        if not isinstance(channel, discord.TextChannel):
            print(f'[WELCOME] Channel is not TextChannel: {type(channel)}')
            return

        embed = discord.Embed(
            title='📥 Новый участник зашёл на сервер',
            description=(
                f'1. **Тег:** {member.mention}\n'
                f'2. **Ник:** `{member.name}`\n'
                f'3. **ID:** `{member.id}`'
            ),
            color=0x3B82F6,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        embed.set_footer(text='CENT — Уведомление для Старшего Состава 👑')

        if CENT_IMAGE_FILE.is_file():
            file = discord.File(CENT_IMAGE_FILE, filename='cent.png')
            embed.set_image(url='attachment://cent.png')
            await channel.send(embed=embed, file=file)
        elif WELCOME_IMAGE_URL:
            embed.set_image(url=WELCOME_IMAGE_URL)
            await channel.send(embed=embed)
        else:
            await channel.send(embed=embed)

        print(f'[WELCOME] Message sent successfully')
    except Exception as exc:
        print(f'[WELCOME ERROR] {type(exc).__name__}: {exc}')

@bot.event
async def on_member_remove(member: discord.Member) -> None:
    roles = [r.mention for r in member.roles if r.name != '@everyone']
    role_list = ', '.join(roles[:10]) if roles else 'Нет ролей'

    asyncio.create_task(send_log(
        '📤 Участник вышел',
        fields=[
            ('Участник', _log_user_field(member), True),
            ('Роли', role_list, False),
            ('Участников', str(member.guild.member_count), True),
        ],
        color=0xFF6600, user=member,
    ))


# --------------- Voice state logging ---------------

@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
) -> None:
    if member.bot:
        return

    if before.channel is None and after.channel is not None:
        # Зашёл в войс
        asyncio.create_task(send_log(
            '🔊 Подключился к голосовому',
            fields=[
                ('Участник', _log_user_field(member), True),
                ('Канал', _log_channel_field(after.channel), True),
            ],
            color=0x22C55E, user=member,
        ))
    elif before.channel is not None and after.channel is None:
        # Вышел из войса
        asyncio.create_task(send_log(
            '🔇 Отключился от голосового',
            fields=[
                ('Участник', _log_user_field(member), True),
                ('Канал', _log_channel_field(before.channel), True),
            ],
            color=0xEF4444, user=member,
        ))
    elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
        # Перешёл / перекинули в другой войс
        asyncio.create_task(send_log(
            '🔀 Перемещён в голосовом',
            fields=[
                ('Участник', _log_user_field(member), True),
                ('Откуда', _log_channel_field(before.channel), True),
                ('Куда', _log_channel_field(after.channel), True),
            ],
            color=0xF59E0B, user=member,
        ))


# --------------- Message edit / delete logging ---------------

def _truncate(text: str, limit: int = 1000) -> str:
    """Truncate text for embed fields."""
    if not text:
        return '*пусто*'
    if len(text) <= limit:
        return text
    return text[:limit] + '…'

def _message_link(message: discord.Message) -> str:
    if message.guild:
        return f'https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}'
    return ''

@bot.event
async def on_message_delete(message: discord.Message) -> None:
    if message.author.bot or message.guild is None:
        return

    content = _truncate(message.content) if message.content else '*нет текста (возможно вложение)*'
    link = _message_link(message)

    fields = [
        ('Участник', _log_user_field(message.author), True),
        ('Канал', _log_channel_field(message.channel), True),
        ('Содержимое', content, False),
    ]
    if link:
        fields.append(('Сообщение', f'[перейти]({link})', False))

    asyncio.create_task(send_log(
        '🗑️ Сообщение удалено',
        fields=fields,
        color=0xEF4444, user=message.author,
    ))

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message) -> None:
    if after.author.bot or after.guild is None:
        return
    if before.content == after.content:
        return  # embed update, pin, etc — не текстовое изменение

    link = _message_link(after)
    fields = [
        ('Участник', _log_user_field(after.author), True),
        ('Канал', _log_channel_field(after.channel), True),
        ('До', _truncate(before.content), False),
        ('После', _truncate(after.content), False),
    ]
    if link:
        fields.append(('Сообщение', f'[перейти]({link})', False))

    asyncio.create_task(send_log(
        '✏️ Сообщение изменено',
        fields=fields,
        color=0xF59E0B, user=after.author,
    ))


# --------------- Role change logging ---------------

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member) -> None:
    old_roles = set(before.roles)
    new_roles = set(after.roles)

    added = new_roles - old_roles
    removed = old_roles - new_roles

    if not added and not removed:
        return

    # Ищем кто выдал/забрал роль через raw API
    moderator = None
    await asyncio.sleep(2)
    try:
        guild_id = after.guild.id
        member_id = after.id
        action_type = discord.AuditLogAction.member_role_update.value
        url = f'https://discord.com/api/v10/guilds/{guild_id}/audit-logs?limit=20&action_type={action_type}'
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bot {BOT_TOKEN}'}
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for entry in data.get('audit_log_entries', []):
                        if int(entry.get('target_id', 0)) == member_id:
                            user_id = entry.get('user_id')
                            if user_id:
                                moderator = after.guild.get_member(int(user_id))
                                if moderator is None:
                                    try:
                                        moderator = await after.guild.fetch_member(int(user_id))
                                    except Exception:
                                        pass
                            break
    except Exception:
        pass

    fields = [('Участник', _log_user_field(after), True)]
    if moderator:
        fields.append(('👤 Модератор', _log_user_field(moderator), True))
    if added:
        role_names = ', '.join(r.mention for r in added if r.name != '@everyone')
        if role_names:
            fields.append(('➕ Выданы', role_names, True))
    if removed:
        role_names = ', '.join(r.mention for r in removed if r.name != '@everyone')
        if role_names:
            fields.append(('➖ Забраны', role_names, True))

    asyncio.create_task(send_log(
        '🏷️ Изменение ролей',
        fields=fields,
        color=0x8B5CF6, user=after,
    ))


# --------------- Ban / Unban / Kick logging ---------------

@bot.event
async def on_member_ban(guild: discord.Guild, user: discord.User) -> None:
    await asyncio.sleep(2)
    moderator = None
    reason = ''
    try:
        url = f'https://discord.com/api/v10/guilds/{guild.id}/audit-logs?limit=10&action_type={discord.AuditLogAction.ban.value}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'Authorization': f'Bot {BOT_TOKEN}'}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for entry in data.get('audit_log_entries', []):
                        if int(entry.get('target_id', 0)) == user.id:
                            user_id = entry.get('user_id')
                            if user_id:
                                moderator = guild.get_member(int(user_id))
                                reason = entry.get('reason', '') or ''
                            break
    except Exception:
        pass

    fields = [('Участник', _log_user_field(user), True)]
    if moderator:
        fields.append(('👤 Модератор', _log_user_field(moderator), True))
    if reason:
        fields.append(('📝 Причина', reason, False))

    asyncio.create_task(send_log(
        '🔨 Бан',
        fields=fields,
        color=0xFF0000, user=user,
    ))


@bot.event
async def on_member_unban(guild: discord.Guild, user: discord.User) -> None:
    await asyncio.sleep(2)
    moderator = None
    try:
        url = f'https://discord.com/api/v10/guilds/{guild.id}/audit-logs?limit=10&action_type={discord.AuditLogAction.unban.value}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'Authorization': f'Bot {BOT_TOKEN}'}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for entry in data.get('audit_log_entries', []):
                        if int(entry.get('target_id', 0)) == user.id:
                            user_id = entry.get('user_id')
                            if user_id:
                                moderator = guild.get_member(int(user_id))
                            break
    except Exception:
        pass

    fields = [('Участник', _log_user_field(user), True)]
    if moderator:
        fields.append(('👤 Модератор', _log_user_field(moderator), True))

    asyncio.create_task(send_log(
        '✅ Разбан',
        fields=fields,
        color=0x00FF00, user=user,
    ))


# --------------- Member join / leave logging ---------------

# --------------- Channel logging ---------------

@bot.event
async def on_guild_channel_create(channel: discord.abc.GuildChannel) -> None:
    channel_type = 'Текстовый' if isinstance(channel, discord.TextChannel) else 'Голосовой' if isinstance(channel, discord.VoiceChannel) else 'Другой'
    asyncio.create_task(send_log(
        '📁 Канал создан',
        fields=[
            ('Канал', f'{channel.mention} (`{channel.id}`)', True),
            ('Тип', channel_type, True),
        ],
        color=0x00FF00,
    ))


@bot.event
async def on_guild_channel_delete(channel: discord.abc.GuildChannel) -> None:
    channel_type = 'Текстовый' if isinstance(channel, discord.TextChannel) else 'Голосовой' if isinstance(channel, discord.VoiceChannel) else 'Другой'
    asyncio.create_task(send_log(
        '🗑️ Канал удалён',
        fields=[
            ('Канал', f'#{channel.name} (`{channel.id}`)', True),
            ('Тип', channel_type, True),
        ],
        color=0xFF0000,
    ))


@bot.event
async def on_guild_channel_update(before: discord.abc.GuildChannel, after: discord.abc.GuildChannel) -> None:
    changes = []
    if before.name != after.name:
        changes.append(f'Название: `{before.name}` → `{after.name}`')
    if hasattr(before, 'bitrate') and hasattr(after, 'bitrate') and before.bitrate != after.bitrate:
        changes.append(f'Битрейт: {before.bitrate} → {after.bitrate}')
    if hasattr(before, 'user_limit') and hasattr(after, 'user_limit') and before.user_limit != after.user_limit:
        changes.append(f'Лимит: {before.user_limit} → {after.user_limit}')
    if before.category_id != after.category_id:
        changes.append('Категория изменена')

    if changes:
        asyncio.create_task(send_log(
            '📝 Канал изменён',
            fields=[
                ('Канал', f'{after.mention}', True),
                ('Изменения', '\n'.join(changes), False),
            ],
            color=0xF59E0B,
        ))


# --------------- Invite logging ---------------

@bot.event
async def on_invite_create(invite: discord.Invite) -> None:
    inviter = invite.inviter
    fields = [
        ('Инвайт', f'`{invite.code}`', True),
        ('Канал', f'{invite.channel.mention}' if invite.channel else 'Неизвестно', True),
    ]
    if inviter:
        fields.append(('👤 Создал', _log_user_field(inviter), True))
    if invite.max_uses:
        fields.append(('Лимит использований', str(invite.max_uses), True))
    if invite.max_age:
        fields.append(('Время жизни', f'{invite.max_age // 3600}ч', True))

    asyncio.create_task(send_log(
        '🔗 Инвайт создан',
        fields=fields,
        color=0x00FF00,
    ))


@bot.event
async def on_invite_delete(invite: discord.Invite) -> None:
    asyncio.create_task(send_log(
        '🔗 Инвайт удалён',
        fields=[
            ('Инвайт', f'`{invite.code}`', True),
            ('Канал', f'{invite.channel.mention}' if invite.channel else 'Неизвестно', True),
            ('Использований', str(invite.uses or 0), True),
        ],
        color=0xFF0000,
    ))


@bot.tree.command(name='set_bot_image', description='Обновить изображения бота')
@app_commands.default_permissions(manage_guild=True)
async def set_bot_image(interaction: discord.Interaction) -> None:
    """Upload the bundled CENT image to Discord and use it in all bot embeds."""
    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message('Нужны права «Управление сервером».', ephemeral=True)
        return
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message('Команду нужно использовать в текстовом канале.', ephemeral=True)
        return
    if not CENT_IMAGE_FILE.is_file():
        await interaction.response.send_message('Файл изображения не найден в проекте.', ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True, thinking=True)
    image_message = await interaction.channel.send(file=discord.File(CENT_IMAGE_FILE, filename='cent.png'))
    image_url = image_message.attachments[0].url
    IMAGE_STATE_FILE.write_text(json.dumps({'url': image_url}, ensure_ascii=False), encoding='utf-8')

    global BOT_IMAGE_URL, THUMBNAIL_URL, MAIN_IMAGE_URL, WELCOME_IMAGE_URL
    BOT_IMAGE_URL = image_url
    THUMBNAIL_URL = image_url
    MAIN_IMAGE_URL = image_url
    WELCOME_IMAGE_URL = image_url

    asyncio.create_task(refresh_board_safely())
    asyncio.create_task(refresh_recruit_board_safely())
    asyncio.create_task(refresh_report_button_message_safely())
    asyncio.create_task(refresh_birthday_board_safely())
    asyncio.create_task(refresh_application_board_safely())
    asyncio.create_task(refresh_recruit_app_banner_safely())
    asyncio.create_task(refresh_admin_panel_safely())
    await interaction.followup.send('Изображение бота обновлено во всех панелях.', ephemeral=True)


@tasks.loop(seconds=AUTO_REFRESH_SECONDS)
async def auto_refresh() -> None:
    await refresh_board_safely()
    await refresh_recruit_board_safely()
    await refresh_report_button_message_safely()
    await refresh_birthday_board_safely()
    await refresh_application_board_safely()
    await refresh_recruit_app_banner_safely()
    await refresh_admin_panel_safely()


@bot.tree.command(name='verification_message', description='Отправить сообщение для верификации')
@app_commands.default_permissions(manage_guild=True)
async def verification_message(interaction: discord.Interaction) -> None:
    """Publish a reaction-role verification message in the current text channel."""
    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message('Нужны права «Управление сервером».', ephemeral=True)
        return
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message('Команду нужно использовать в текстовом канале.', ephemeral=True)
        return
    if not VERIFICATION_ROLE_ID:
        await interaction.response.send_message('Укажите VERIFICATION_ROLE_ID в .env и перезапустите бота.', ephemeral=True)
        return

    role = interaction.guild.get_role(VERIFICATION_ROLE_ID) if interaction.guild else None
    if role is None:
        await interaction.response.send_message('Роль из VERIFICATION_ROLE_ID не найдена на этом сервере.', ephemeral=True)
        return
    if interaction.guild is None or interaction.guild.me is None or role >= interaction.guild.me.top_role:
        await interaction.response.send_message('Роль бота должна быть выше роли «Верифицирован».', ephemeral=True)
        return

    embed = discord.Embed(
        title='Верификация',
        description=f'Чтобы получить доступ к серверу, нажмите на реакцию {VERIFICATION_EMOJI} ниже.',
        color=0x5865F2,
    )
    message = await interaction.channel.send(embed=embed)
    await message.add_reaction(VERIFICATION_EMOJI)
    write_verification_state({
        'guild_id': interaction.guild_id,
        'channel_id': interaction.channel_id,
        'message_id': message.id,
    })
    await interaction.response.send_message('Сообщение верификации опубликовано.', ephemeral=True)

@bot.tree.command(name='family', description='Обновить таблицу состава семьи')
async def family(interaction: discord.Interaction) -> None:
    await interaction.response.send_message('Принял, обновляю баннер в канале.', ephemeral=True)
    asyncio.create_task(send_log('📋 Команда /family', f'{interaction.user.mention} обновил состав семьи', color=0xF59E0B, user=interaction.user))
    asyncio.create_task(refresh_board_safely())

@bot.tree.command(name='recruit', description='Показать твою личную ссылку рекрута')
async def recruit(interaction: discord.Interaction) -> None:
    if not isinstance(interaction.user, discord.Member) or not has_recruit_role(interaction.user):
        await interaction.response.send_message('Эта команда доступна только рекрутам.', ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True, thinking=True)
    record = await create_or_get_recruit_invite(interaction.user)
    await refresh_recruit_board_safely()
    await interaction.followup.send(f'Твоя личная ссылка: {record["invite_url"]}\nПринял людей: {record.get("accepted_count", 0)}', ephemeral=True)
    asyncio.create_task(send_log(
        '🔗 Команда /recruit',
        f'{interaction.user.mention} запросил свою ссылку\n{record["invite_url"]}\nПринял людей: **{record.get("accepted_count", 0)}**',
        color=0x22C55E, user=interaction.user,
    ))

@bot.tree.command(name='report_invite', description='Отписать, кого ты пригласил')
async def report_invite(interaction: discord.Interaction) -> None:
    if not isinstance(interaction.user, discord.Member) or not has_recruit_role(interaction.user):
        await interaction.response.send_message('Эта команда доступна только рекрутам.', ephemeral=True)
        return
    asyncio.create_task(send_log('📝 Команда /report_invite', f'{interaction.user.mention} открыл форму отчёта', color=0x38BDF8, user=interaction.user))
    await interaction.response.send_modal(RecruitReportModal())

@bot.tree.command(name='birthday', description='Добавить или изменить свой день рождения')
async def birthday(interaction: discord.Interaction) -> None:
    asyncio.create_task(send_log('🎂 Команда /birthday', f'{interaction.user.mention} открыл форму дня рождения', color=0xF97316, user=interaction.user))
    await interaction.response.send_modal(BirthdayModal())

@bot.tree.command(name='recruits', description='Обновить плашку рекрутов')
@app_commands.default_permissions(manage_guild=True)
async def recruits(interaction: discord.Interaction) -> None:
    await interaction.response.send_message('Обновляю плашку рекрутов.', ephemeral=True)
    asyncio.create_task(send_log('📋 Команда /recruits', f'{interaction.user.mention} обновил плашку рекрутов', color=0x22C55E, user=interaction.user))
    asyncio.create_task(refresh_recruit_board_safely())

@bot.tree.command(name='admin_panel', description='Обновить панель управления')
@app_commands.default_permissions(manage_guild=True)
async def admin_panel(interaction: discord.Interaction) -> None:
    await interaction.response.send_message('Обновляю панель управления.', ephemeral=True)
    asyncio.create_task(send_log('⚙️ Команда /admin_panel', f'{interaction.user.mention} обновил панель управления', color=0xEF4444, user=interaction.user))
    asyncio.create_task(refresh_admin_panel_safely())

@bot.tree.command(name='clear', description='Удалить сообщения из канала')
@app_commands.describe(amount='Количество сообщений для удаления (1-100)')
@app_commands.default_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int) -> None:
    if amount < 1 or amount > 100:
        await interaction.response.send_message('Можно удалить от 1 до 100 сообщений.', ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    deleted = 0
    try:
        messages = [msg async for msg in interaction.channel.history(limit=amount + 1)]
        # Удаляем само сообщение команды тоже
        await interaction.channel.delete_messages(messages)
        deleted = len(messages)
    except discord.Forbidden:
        await interaction.followup.send('Нет права **Управление сообщениями**.', ephemeral=True)
        return
    except discord.HTTPException as exc:
        await interaction.followup.send(f'Ошибка: {exc}', ephemeral=True)
        return

    await interaction.followup.send(f'🗑️ Удалено **{deleted}** сообщений.', ephemeral=True)
    asyncio.create_task(send_log(
        '🗑️ Очистка канала',
        fields=[
            ('Модератор', _log_user_field(interaction.user), True),
            ('Канал', _log_channel_field(interaction.channel), True),
            ('Удалено', f'**{deleted}** сообщений', True),
        ],
        color=0xF59E0B, user=interaction.user,
    ))


# --------------- Nuke (clone & delete) ---------------

class NukeConfirmView(discord.ui.View):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(timeout=30)
        self.channel = channel

    @discord.ui.button(label='Да, нuke', style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message('Нет прав.', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            new_channel = await self.channel.clone(reason=f'Nuke by {interaction.user}')
            await self.channel.delete(reason=f'Nuke by {interaction.user}')

            embed = discord.Embed(
                title='💥 Канал очищен',
                description=f'{new_channel.mention} — все сообщения удалены.',
                color=0xFF0000,
            )
            await new_channel.send(embed=embed)

            asyncio.create_task(send_log(
                '💥 Nuke',
                fields=[
                    ('Модератор', _log_user_field(interaction.user), True),
                    ('Канал', f'{new_channel.mention} (`{new_channel.id}`)', True),
                ],
                color=0xFF0000, user=interaction.user,
            ))
        except discord.Forbidden:
            await interaction.followup.send('Нет права **Управление каналами**.', ephemeral=True)

        self.stop()

    @discord.ui.button(label='Отмена', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('❌ Отменено.', ephemeral=True)
        self.stop()


@bot.tree.command(name='nuke', description='Полная очистка канала (clone + delete)')
@app_commands.default_permissions(manage_channels=True)
async def nuke(interaction: discord.Interaction) -> None:
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message('Только для текстовых каналов.', ephemeral=True)
        return

    view = NukeConfirmView(interaction.channel)
    await interaction.response.send_message(
        '⚠️ **Внимание!** Все сообщения в канале будут удалены.\nКанал будет пересоздан.\n\nВы уверены?',
        view=view,
        ephemeral=True,
    )


class AnnouncementModal(discord.ui.Modal, title='📢 Объявление'):
    title_input = discord.ui.TextInput(label='Заголовок', placeholder='Важное объявление', max_length=100)
    message_input = discord.ui.TextInput(label='Текст', style=discord.TextStyle.paragraph, placeholder='Напиши сообщение...')
    channel_id_input = discord.ui.TextInput(label='ID канала', placeholder='1521295122204201163')

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message('Нет прав.', ephemeral=True)
            return

        try:
            channel_id = int(self.channel_id_input.value.strip())
        except ValueError:
            await interaction.response.send_message('ID канала — число.', ephemeral=True)
            return

        channel = interaction.guild.get_channel(channel_id)
        if channel is None:
            try:
                channel = await interaction.guild.fetch_channel(channel_id)
            except Exception:
                await interaction.response.send_message('Канал не найден.', ephemeral=True)
                return

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message('Это не текстовый канал.', ephemeral=True)
            return

        embed = discord.Embed(
            title=f'📢 {self.title_input}',
            description=str(self.message_input),
            color=0xF59E0B,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=f'Объявление от {interaction.user.display_name}')

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(f'Нет прав писать в {channel.mention}.', ephemeral=True)
            return

        await interaction.response.send_message(f'✅ Объявление отправлено в {channel.mention}', ephemeral=True)
        asyncio.create_task(send_log(
            '📢 Объявление',
            fields=[
                ('Модератор', _log_user_field(interaction.user), True),
                ('Канал', _log_channel_field(channel), True),
                ('Заголовок', self.title_input.value, False),
            ],
            color=0xF59E0B, user=interaction.user,
        ))




# --------------- AI (NVIDIA API) ---------------

@bot.tree.command(name='ai', description='Задать вопрос AI')
@app_commands.describe(question='Ваш вопрос')
async def ai_cmd(interaction: discord.Interaction, question: str) -> None:
    if not NVIDIA_API_KEY:
        await interaction.response.send_message('AI не настроен (нет API ключа).', ephemeral=True)
        return

    await interaction.response.defer(thinking=True)

    headers = {
        'Authorization': f'Bearer {NVIDIA_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': NVIDIA_MODEL,
        'messages': [{'role': 'user', 'content': question}],
        'max_tokens': 1024,
        'temperature': 0.7,
        'top_p': 0.9,
        'stream': False,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(NVIDIA_API_URL, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    await interaction.followup.send(f'Ошибка API ({resp.status}): {text[:500]}', ephemeral=True)
                    return
                data = await resp.json()

        answer = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        if not answer:
            await interaction.followup.send('AI не вернул ответ.', ephemeral=True)
            return

        if len(answer) > 3900:
            answer = answer[:3900] + '\n\n... (ответ обрезан)'

        embed = discord.Embed(
            title='🤖 Вопрос AI',
            description=f'**Вопрос:** {question[:500]}\n\n**Ответ:**\n{answer}',
            color=0x8B5CF6,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=f'{interaction.user.display_name}', icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
        embed.set_thumbnail(url=THUMBNAIL_URL)

        await interaction.followup.send(embed=embed)

        asyncio.create_task(send_log(
            '🤖 AI-запрос',
            fields=[
                ('Участник', _log_user_field(interaction.user), True),
                ('Вопрос', _truncate(question, 200), False),
                ('Длина ответа', f'{len(answer)} символов', True),
            ],
            color=0x8B5CF6, user=interaction.user,
        ))

    except asyncio.TimeoutError:
        await interaction.followup.send('AI не ответил (таймаут 30 сек).', ephemeral=True)
    except Exception as exc:
        await interaction.followup.send(f'Ошибка: {exc}', ephemeral=True)
        print(f'[AI ERROR] {exc}')


# --------------- Анти-рейд ---------------

raid_cache: dict[str, list[float]] = {}
RAID_THRESHOLD = 5       # сколько входов
RAID_WINDOW = 30          # за столько секунд
RAID_ACTION = 'alert'     # alert / lockdown / kick

async def check_raid(member: discord.Member) -> None:
    """Проверяет не является ли вход частью рейда."""
    guild = member.guild
    invite_code = None

    # Проверяем какой инвайт был использован
    try:
        current_invites = await guild.invites()
    except Exception:
        return

    previous = bot.invite_cache.get(guild.id, {})
    for inv in current_invites:
        old_uses = previous.get(inv.code, 0)
        new_uses = inv.uses or 0
        if new_uses > old_uses:
            invite_code = inv.code
            break

    # Если инвайт не найден — возможно рандомный вход
    key = invite_code or 'unknown'

    now = discord.utils.utcnow().timestamp()
    timestamps = raid_cache.get(key, [])
    timestamps = [t for t in timestamps if now - t <= RAID_WINDOW]
    timestamps.append(now)
    raid_cache[key] = timestamps

    if len(timestamps) >= RAID_THRESHOLD:
        raid_cache[key] = []

        # Уведомление в лог
        asyncio.create_task(send_log(
            '🚨 ВОЗМОЖНЫЙ РЕЙД!',
            fields=[
                ('Инвайт', f'`{invite_code}`' if invite_code else '**неизвестен**', True),
                ('Входов за секунд', f'**{RAID_THRESHOLD}+** за **{RAID_WINDOW}** сек', True),
                ('Последний участник', _log_user_field(member), True),
            ],
            color=0xFF0000, user=member,
        ))

        # Пинг админов
        admin_channel = guild.get_channel(LOG_CHANNEL_ID)
        if admin_channel and isinstance(admin_channel, discord.TextChannel):
            try:
                admins = [m for m in guild.members if m.guild_permissions.manage_guild and not m.bot]
                admin_mentions = ' '.join(a.mention for a in admins[:5])
                await admin_channel.send(
                    f'🚨 **ВОЗМОЖНЫЙ РЕЙД!** {RAID_THRESHOLD}+ входов за {RAID_WINDOW} сек через инвайт `{invite_code}`\n{admin_mentions}',
                    allowed_mentions=discord.AllowedMentions(users=True),
                )
            except Exception:
                pass


@bot.tree.command(name='test', description='Проверка бота')
async def test_cmd(interaction: discord.Interaction) -> None:
    await interaction.response.send_message('Привет', ephemeral=True)


# --------------- Бот запускается ---------------

import time as _time

while True:
    try:
        bot.run(BOT_TOKEN)
        break
    except Exception:
        _time.sleep(30)

