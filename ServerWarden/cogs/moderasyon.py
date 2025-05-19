import discord
from discord.ext import commands
import datetime
from database import Database

db = Database()

class Moderasyon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='temizle')
    @commands.has_permissions(manage_messages=True)
    async def temizle(self, ctx, miktar: int):
        """Belirtilen sayıda mesajı siler."""
        deleted = await ctx.channel.purge(limit=miktar+1)
        await ctx.send(f'🧹 {len(deleted)-1} mesaj silindi!', delete_after=3)

    @commands.command(name='rolver')
    @commands.has_permissions(manage_roles=True)
    async def rolver(self, ctx, member: discord.Member, role: discord.Role):
        """Kullanıcıya rol verir."""
        await member.add_roles(role)
        await ctx.send(f'{member.mention} kullanıcısına {role.mention} rolü verildi!')

    @commands.command(name='rolal')
    @commands.has_permissions(manage_roles=True)
    async def rolal(self, ctx, member: discord.Member, role: discord.Role):
        """Kullanıcıdan rol alır."""
        await member.remove_roles(role)
        await ctx.send(f'{member.mention} kullanıcısından {role.mention} rolü alındı!')

    @commands.command(name='slowmode')
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, saniye: int):
        """Kanalda yavaş mod ayarlar."""
        await ctx.channel.edit(slowmode_delay=saniye)
        await ctx.send(f'⏳ Yavaş mod {saniye} saniye olarak ayarlandı!')

    @commands.command(name='unmute')
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        """Kullanıcının mutesini kaldırır."""
        await member.timeout(None)
        await ctx.send(f'{member.mention} kullanıcısının mutesi kaldırıldı!')

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        """Kullanıcının banını kaldırır."""
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f'{user.mention} kullanıcısının banı kaldırıldı!')

    @commands.command(name='uyarısil')
    @commands.has_permissions(manage_messages=True)
    async def uyarisil(self, ctx, member: discord.Member, uyarino: int):
        """Belirli bir uyarıyı siler."""
        warnings = await db.get_warnings(member.id, ctx.guild.id)
        if 0 < uyarino <= len(warnings):
            warning_id = warnings[uyarino-1]['id']
            await db.delete_warning(warning_id)
            await ctx.send(f'{member.mention} kullanıcısının #{uyarino} numaralı uyarısı silindi!')
        else:
            await ctx.send('Geçersiz uyarı numarası!')

    @commands.command(name='uyarıtemizle')
    @commands.has_permissions(manage_messages=True)
    async def uyaritemizle(self, ctx, member: discord.Member):
        """Kullanıcının tüm uyarılarını siler."""
        await db.clear_warnings(member.id, ctx.guild.id)
        await ctx.send(f'{member.mention} kullanıcısının tüm uyarıları silindi!')

    @commands.command(name='yasaklikelimeekle')
    @commands.has_permissions(manage_messages=True)
    async def yasaklikelimeekle(self, ctx, *, kelime):
        """Yasaklı kelime ekler."""
        await db.add_banned_word(ctx.guild.id, kelime)
        await ctx.send(f'Yasaklı kelime eklendi: {kelime}')

    @commands.command(name='yasaklikelimesil')
    @commands.has_permissions(manage_messages=True)
    async def yasaklikelimesil(self, ctx, *, kelime):
        """Yasaklı kelimeyi siler."""
        await db.delete_banned_word(ctx.guild.id, kelime)
        await ctx.send(f'Yasaklı kelime silindi: {kelime}')

    @commands.command(name='logkanal')
    @commands.has_permissions(manage_channels=True)
    async def logkanal(self, ctx, kanal: discord.TextChannel):
        """Log kanalını ayarlar."""
        await db.set_log_channel(ctx.guild.id, kanal.id)
        await ctx.send(f'Log kanalı {kanal.mention} olarak ayarlandı!')

async def setup(bot):
    await bot.add_cog(Moderasyon(bot)) 