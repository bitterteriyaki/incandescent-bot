# Changelog

## 0.14.1 (2023-07-31)

### Fix

- **ext/fun**: fix error when the bot tries to get a member which left the server

## 0.14.0 (2023-07-25)

### Feat

- **ext/levels**: Remove the user from the database when they leaves the guild
- **ext/economy**: Initial economy system

## 0.13.0 (2023-07-21)

### Feat

- **ext/jishaku**: Add all the features from Jishaku

### Fix

- **ext/events**: Get the general channel from this default guild instead look over all guilds

## 0.12.0 (2023-07-09)

### Feat

- **ext/events**: Handle `on_member_join` event and send welcome message

### Fix

- **utils/database**: Set the tables columns not nullable by default
- **ext/levels**: Insert the users when set experience to multiple users

## 0.11.2 (2023-07-08)

### Fix

- **ext/levels**: Insert the users when add experience to multiple users

## 0.11.1 (2023-07-08)

### Fix

- **core**: Change bot activity and status

## 0.11.0 (2023-07-08)

### Feat

- **ext/fun**: Create initial fun cog

## 0.10.0 (2023-07-07)

### Feat

- **ext/levels**: Release the initial commands to manipulate experience

## 0.9.0 (2023-07-07)

### Feat

- **core**: Add a Discord presence for the bot
- **ext/support**: Add support to group commands
- **ext/support**: add initial support cog
- **ext/jishaku**: initial custom Jishaku cog

## 0.8.0 (2023-07-06)

### Feat

- **ext/events**: create initial events extension

## 0.7.0 (2023-07-04)

### Feat

- remove logs folder from the project

## 0.6.0 (2023-07-04)

### Feat

- add rotating logs to bot

## 0.5.3 (2023-07-04)

### Fix

- **ci**: do not remover docker container after running it

## 0.5.2 (2023-07-04)

### Fix

- **ci**: add quotes to environments

## 0.5.1 (2023-07-04)

### Fix

- **ci**: fix ci environments variables

## 0.5.0 (2023-07-04)

### Fix

- **ci**: fix deployment ci

## 0.4.0 (2023-07-04)

- **ci**: finish deployment ci

## 0.3.0 (2023-07-04)

- **ci**: add deploy ci

## 0.2.0 (2023-07-04)

### Fix

- **utils/extensions**: fix extensions variable typing

## 0.1.0 (2023-07-03)

### Feat

- add role when reaching level N
- **levels**: initial levels system development
- initial bot development
