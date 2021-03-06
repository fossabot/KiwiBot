from objects.modulebase import ModuleBase
from objects.permissions import PermissionManageGuild


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} [prefix]'
    short_doc = 'Change bot guild prefix'
    long_doc = (
        'Subcommands:\n'
        '\t{prefix}{aliases} [delete|remove|clear] - remove guild prefix'
    )

    name = 'prefix'
    category = 'Moderation'
    aliases = (name, )
    guild_only = True

    async def on_call(self, ctx, args, **flags):
        if len(args) == 1:
            prefix = await self.bot.redis.get(f'guild_prefix:{ctx.guild.id}')

            if not prefix:
                return 'Custom prefix not set. Default is: **' + self.bot._default_prefix + '**'
            else:
                return f'Prefix for this guild is: **{prefix}**'

        manage_guild_perm = PermissionManageGuild()
        if not manage_guild_perm.check(ctx.channel, ctx.author):
            raise manage_guild_perm

        if args[1:].lower() in ('remove', 'delete', 'clear'):
            await self.bot.redis.delete(f'guild_prefix:{ctx.guild.id}')
            del self.bot._guild_prefixes[ctx.guild.id]
            return 'Guild prefix removed'

        prefix = args[1:][:200]  # 200 characters limit
        await self.bot.redis.set(f'guild_prefix:{ctx.guild.id}', prefix)
        self.bot._guild_prefixes[ctx.guild.id] = prefix.lower()

        return f'Guild prefix set to: **{prefix}**'