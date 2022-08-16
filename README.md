# Colorista
>*Discord bot for managing colors of your roles.*
---
### Help

- `/ping`
    - Command for pinging the bot.
    - Responds with "Pong!" and a user's mention.
- `/rolecolor <model> <color>`
    - Command to change color of your role.
    - `<model>` - how to interpret your color. Accepts 3 values:
        - RGB - three number values, e. g. 120, 4, 100.
        - RGB HEX - a hexadecimal number, e. g. #69FF3C.
        - Name - choose color by it's name. See lower for all colors that can be called by name.
    - `<color>` - your color.
- `/roleinfo <role>`
    - Command to get and display given role's info.
    - `<role>` - role, whose info is going to be displayed.
- `/roleassign <member> <role>` - admin only
    - Command to assign a role to user. Role needs to be created before.
    - `<member>` - user who's gonna get a role.
    - `<role>` - role, whose going to be given.
    - If role hasn't been given to a user before command runs, bot is going to give a role automatically.
- `/roletakeback <member>` - admin only
    - Command to remove an assigned role from a specified user.
    - `<member>` - user whose role is taken away.

### Colors that can be called by their name
- Red
- Green
- Blue
- Orange
- Purple
- White
- Black
- Magenta
- Yellow
- Teal
- Discord Dark
- Discord Light
- Default (no color)
- Random