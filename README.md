# Gyoshin-The-Raid-Planner

Disclaimer: Gyoshin was project managed by Martijin Bos, not myself. I would like to thank Martijin for inviting me to their project and giving me a chance to gain some experience on a more complex real life project. My additions to the bot are: General help in design, !Create command, !Join command, !Cancel command, !Rally command, Developer testing commands and helper functions, debugging, analysing current beta feedback. I would also like to thank them for teaching me about the database side of the project. All code on my programmed commands were all completed by myself, with Martijin pushing me to use resources and other commands for guidance when stuck but not outright giving me answers, and also giving guidance on how to refactor code to look more polished and handle errors better once code was functional. 

Gyoshin is a Discord Bot, initially created to help my Final Fantasy XIV server have a simple and functional way of planning raid parties. Using Python and additional libraries/APIs such as Discord, datetime, re and sqlite3, Gyoshin allows users to create, and manage parties on a discord server. By saving the party to a database with references to the server channel ID, it allows several servers to use at once without picking up all the raids. 

Users can join raids, by choosing specific roles, withdraw from raids, cancel raids if they are the organiser, and rally the users within one hour of the set datetime of the event.

## Developer RoadMap:

Complete Beta testing with members of FFXIV discord (3000 people in channel), analyse feedback and develop roadmap further and debug my commands where required. 

Allow users to sign up to parties using emjoi reactions. 

Expand available roles to include limited Jobs (Blue Mage).

General refactor of code to improve responsiveness.

### not all files are on github, such as packages, just main programmed files for reference

