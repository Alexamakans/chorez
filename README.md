# plan for commands, maybe?

```plain
tt task show <filter>
tt task add [--title TITLE] [--desc DESC] [--label LABEL ...] [--field KEY=VALUE ...]
tt task edit <id> [--title TITLE] [--desc DESC] [--label +LABEL|-LABEL ...] [--field KEY=VALUE ...] [--field ~KEY]
tt task rm <id ...> | --filter EXPR

tt time start [<task>] [-s START | --start START] [--note NOTE]
tt time stop [-e END | --end END] [--note NOTE]
tt time switch <task> [--note NOTE]
tt time resume [<task>] [--note NOTE]
tt time log [<task>] -s START | --start START -e END | --end END [--note NOTE]
tt time edit <entry-id> [-s START | --start START] [-e END | --end END] [--note NOTE]
tt time list [-s START | --start START] [-e END | --end END] [--filter EXPR]
tt time status
```
