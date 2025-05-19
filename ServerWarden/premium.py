import discord
from discord.ext import commands
import datetime
import json
import asyncio
import random
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class PremiumFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
        self.db = self.mongo_client.serverwarden

    @commands.command(name='çekiliş_turbo')
    async def turbo_giveaway(self, ctx, time: str, winners: int, *, prize: str):
        """Gelişmiş çekiliş başlatır"""
        if not await self.is_premium(ctx.guild.id):
            await ctx.send("Bu komut sadece premium sunucularda kullanılabilir!")
            return

        try:
            time_seconds = self.parse_time(time)
            if not time_seconds:
                await ctx.send("Geçersiz zaman formatı! Örnek: 1h, 30m, 1d")
                return

            embed = discord.Embed(
                title="🎉 Turbo Çekiliş",
                description=f"**Ödül:** {prize}\n\n"
                           f"**Kazanan Sayısı:** {winners}\n"
                           f"**Bitiş:** {time}\n\n"
                           f"Katılmak için 🎉 emojisine tıklayın!",
                color=discord.Color.gold()
            )
            message = await ctx.send(embed=embed)
            await message.add_reaction("🎉")

            await asyncio.sleep(time_seconds)
            message = await message.channel.fetch_message(message.id)
            users = [user async for user in message.reactions[0].users()]
            users.remove(self.bot.user)

            if not users:
                await ctx.send("Kimse katılmadı! 😢")
                return

            if len(users) < winners:
                winners = len(users)

            winners_list = random.sample(users, winners)
            winners_text = "\n".join([winner.mention for winner in winners_list])
            
            embed = discord.Embed(
                title="🎉 Çekiliş Sonuçları",
                description=f"**Ödül:** {prize}\n\n"
                           f"**Kazananlar:**\n{winners_text}",
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {str(e)}")

    @commands.command(name='sunucu_bilgi')
    async def server_info(self, ctx):
        """Sunucu istatistiklerini gösterir"""
        if not await self.is_premium(ctx.guild.id):
            await ctx.send("Bu komut sadece premium sunucularda kullanılabilir!")
            return

        guild = ctx.guild
        total_members = len(guild.members)
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        total_channels = len(guild.channels)
        total_roles = len(guild.roles)
        total_emojis = len(guild.emojis)
        total_boosts = guild.premium_subscription_count

        embed = discord.Embed(
            title=f"📊 {guild.name} Sunucu İstatistikleri",
            color=discord.Color.blue()
        )
        embed.add_field(name="👥 Toplam Üye", value=total_members, inline=True)
        embed.add_field(name="🟢 Çevrimiçi Üye", value=online_members, inline=True)
        embed.add_field(name="📝 Toplam Kanal", value=total_channels, inline=True)
        embed.add_field(name="🎭 Toplam Rol", value=total_roles, inline=True)
        embed.add_field(name="😀 Toplam Emoji", value=total_emojis, inline=True)
        embed.add_field(name="✨ Boost Sayısı", value=total_boosts, inline=True)
        embed.add_field(name="📅 Sunucu Kuruluş Tarihi", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="👑 Sunucu Sahibi", value=guild.owner.mention, inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await ctx.send(embed=embed)

    @commands.command(name='rol_ata')
    @commands.has_permissions(manage_roles=True)
    async def auto_role(self, ctx, role: discord.Role):
        """Yeni üyelere otomatik rol atar"""
        if not await self.is_premium(ctx.guild.id):
            await ctx.send("Bu komut sadece premium sunucularda kullanılabilir!")
            return

        try:
            await self.db.auto_roles.update_one(
                {'guild_id': ctx.guild.id},
                {'$set': {'role_id': role.id}},
                upsert=True
            )
            await ctx.send(f"✅ Yeni üyelere otomatik olarak {role.mention} rolü atanacak!")
        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {str(e)}")

    @commands.command(name='komut_özelleştir')
    @commands.has_permissions(administrator=True)
    async def customize_command(self, ctx, command_name: str, *, new_response: str):
        """Komut yanıtlarını özelleştirir"""
        if not await self.is_premium(ctx.guild.id):
            await ctx.send("Bu komut sadece premium sunucularda kullanılabilir!")
            return

        try:
            await self.db.custom_commands.update_one(
                {
                    'guild_id': ctx.guild.id,
                    'command_name': command_name
                },
                {
                    '$set': {
                        'response': new_response,
                        'created_by': ctx.author.id,
                        'created_at': datetime.datetime.now()
                    }
                },
                upsert=True
            )
            await ctx.send(f"✅ `!{command_name}` komutu özelleştirildi!")
        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {str(e)}")

    @commands.command(name='yedekle')
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx):
        """Sunucu ayarlarını yedekler"""
        if not await self.is_premium(ctx.guild.id):
            await ctx.send("Bu komut sadece premium sunucularda kullanılabilir!")
            return

        try:
            # Sunucu ayarlarını topla
            backup_data = {
                'guild_id': ctx.guild.id,
                'timestamp': datetime.datetime.now(),
                'channels': [],
                'roles': [],
                'settings': {}
            }

            # Kanal ayarlarını topla
            for channel in ctx.guild.channels:
                channel_data = {
                    'name': channel.name,
                    'type': str(channel.type),
                    'position': channel.position,
                    'overwrites': []
                }
                for role, overwrite in channel.overwrites.items():
                    channel_data['overwrites'].append({
                        'role_id': role.id,
                        'allow': overwrite.pair()[0].value,
                        'deny': overwrite.pair()[1].value
                    })
                backup_data['channels'].append(channel_data)

            # Rol ayarlarını topla
            for role in ctx.guild.roles:
                if role.name != '@everyone':
                    role_data = {
                        'name': role.name,
                        'color': role.color.value,
                        'hoist': role.hoist,
                        'position': role.position,
                        'permissions': role.permissions.value
                    }
                    backup_data['roles'].append(role_data)

            # Yedeği kaydet
            await self.db.backups.insert_one(backup_data)
            await ctx.send("✅ Sunucu ayarları başarıyla yedeklendi!")
        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {str(e)}")

    @commands.command(name='profil')
    async def profile(self, ctx, member: discord.Member = None):
        """Kullanıcı profilini gösterir"""
        if not await self.is_premium(ctx.guild.id):
            await ctx.send("Bu komut sadece premium sunucularda kullanılabilir!")
            return

        member = member or ctx.author
        
        # Kullanıcı istatistiklerini topla
        messages = await self.db.messages.count_documents({'user_id': member.id, 'guild_id': ctx.guild.id})
        warnings = await self.db.warnings.count_documents({'user_id': member.id, 'guild_id': ctx.guild.id})
        
        embed = discord.Embed(
            title=f"👤 {member.name}'in Profili",
            color=member.color
        )
        embed.add_field(name="📝 Toplam Mesaj", value=messages, inline=True)
        embed.add_field(name="⚠️ Toplam Uyarı", value=warnings, inline=True)
        embed.add_field(name="📅 Hesap Oluşturma", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="📅 Sunucuya Katılma", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
            
        await ctx.send(embed=embed)

    async def is_premium(self, guild_id):
        """Sunucunun premium olup olmadığını kontrol eder"""
        premium_server = await self.db.premium_servers.find_one({'guild_id': guild_id})
        return bool(premium_server)

    def parse_time(self, time_str):
        """Zaman string'ini saniyeye çevirir"""
        try:
            unit = time_str[-1].lower()
            value = int(time_str[:-1])
            
            if unit == 's':
                return value
            elif unit == 'm':
                return value * 60
            elif unit == 'h':
                return value * 3600
            elif unit == 'd':
                return value * 86400
            else:
                return None
        except:
            return None

async def setup(bot):
    await bot.add_cog(PremiumFeatures(bot)) 