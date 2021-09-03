# Gyoshin-The-Raid-Planner ALPHA

Disclaimer: Gyoshin was project managed by Martijin Bos, not myself. I would like to thank Martijin for inviting me to their project and giving me a chance to gain some experience on a more complex real life project. My additions to the bot so far are: General help in design, !Create command, !Join command, !Cancel command, !Rally command, Developer testing commands and helper functions, debugging, analysing current beta feedback. I would also like to thank them for teaching me about the database side of the project. Initial versions of commands i created up to BETA release were mostly programmed myself (with a few UI edits by Martijin), with Martijin pushing me to use resources and other commands for guidance when stuck but not outright giving me answers, and also giving guidance on how to refactor code to look more polished and handle errors better once code was functional. I will be assisting further by debugging bugs found in beta, and continuing to add more features. 

Gyoshin is a Discord Bot, initially created to help my Final Fantasy XIV server have a simple and functional way of planning raid parties. Using Python and additional libraries/APIs such as Discord, datetime, re and sqlite3, Gyoshin allows users to create, and manage parties on a discord server. By saving the party to a database with references to the server channel ID, it allows several servers to use at once without picking up all the raids. 

Users can join raids, by choosing specific roles, withdraw from raids, cancel raids if they are the organiser, and rally the users within one hour of the set datetime of the event.

### Gyoshin has increased in scope (such as using reactions, and moving error messages and moving raid creation to DMs once !create is called, and code has been refactored largely, I have left this repository up to show my initial programmed commands, below find a link to the current Gyoshin repository once complete and not privae

- Link will be here once Gyoshin is out of beta

## Current Commands

The following commands are available (all times must be provided in UTC time for the bot to function properly):

!Create, used to create a run example use without template: 
!Create TestRaid !DateTime 01-08-2021 19:00 !NrOfPlayers 24 !NrOfTanks 3 !NrOfDps 15 !NrOfHealers 6 !Role Tank
Example use with template: 
!Create TestRaid !DateTime 01-08-2021 19:00 !Template Raid !Role Tank 

!Join, used to sign yourself up for a raid example use: !Join TestRaid !DateTime 01-08-2021 19:00 !Role Tank 

!Withdraw, used to remove yourself from a run example use: !Withdraw TestRaid !DateTime 01-08-2021 19:00

!Cancel, used to cancel a run example use: !Cancel TestRaid !DateTime 01-08-2021 19:00 (only the organizer of the run is allowed to cancel)

!Info, used to retrieve info for a specific run example use: !Info TestRaid !DateTime 01-08-2021 19:00

!Runs, used to retrieve all runs planned on a specific date example use: !Runs 01-08-2021

!Reschedule, used to reschedule the run to another date example use: !Reschedule TestRaid !DateTime 04-08-2021 19:00 !NewDateTime 10-08-2021 19:00 (only the organizer of the run is allowed to reschedule)

!ChangeRole, used to change the role you signed up as for the run example use: !ChangeRole TestRaid !DateTime 01-08-2021 19:00 !Role Tank

!Templates, lists all available templates that can be used to create a run with example use: !Templates

!Commands, lists all supported commands example use: !Commands

!Roles, lists all available roles example use: !Roles

!Rally, used to tag all signed up members to a run example use: !Rally TestRaid !DateTime 04-08-2021 19:00 (this command only works from 1 hour before the start time of the run until the start time)

Dismiss, used to dismiss a member from the run example use: !Dismiss TestRaid DateTime 04-08-2021 19:00 !User UserName (only the organizer of the run is allowed to dismiss members)

!AddDefaultTemplates, used to add some default templates for FFXIV example use: !AddDefaultTemplates

!AddTemplate, used to create a custom template example use: !AddTemplate TestTemplate !NrOfPlayers 8 !NrOfTanks 2 !NrOfDps 4 !NrOfHealers 2

!UpdateTemplate, used to update an existing template example use: !UpdateTemplate TestTemplate !NrOfPlayers 8 !NrOfTanks 2 !NrOfDps 4 !NrOfHealers 2 (only the creator of the template is allowed to update)

!DeleteTemplate, used to delete a template example use: !DeleteTemplate TestTemplate (only the creator of the template is allowed to delete)

## Developer RoadMap:

Complete beta testing with members of FFXIV discord, analyse feedback and develop roadmap further and debug my commands where required. 

Allow creation of parties with just !Create and use best agreed format

Allow users to sign up to parties using emjoi reactions. 

Expand available roles to include limited Jobs (Blue Mage).

General refactor of code to improve responsiveness.

### not all files are on github, such as packages, just main programmed files for reference

