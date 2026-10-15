# Hermes adapter

## Install

Install the skill with `hermes skills install pavelnasuta/management-assistant-kit/skills/management-assistant`. Read the source and accept the normal security scan; do not bypass it.

## First use

Start a new session and say: «Используй management-assistant. Пройди онбординг, внешних действий не совершай». The installed skill is self-contained and loads its safety contract from `references/shared-contract.md`.

## Safety

The adapter never authorizes external actions. Creation or modification of a task, message, document, access, calendar record, automation or payment needs a precise draft, explicit approval, and a read-back of the changed object.
