# plan for commands, maybe?

```plain
tt task show
    [--filter EXPR]
    [--groupby KEY ...]
    [--format {pretty, with_times, json, yaml}]
tt task add <--name NAME> [--desc DESC] [--tags LABEL ...]
tt task edit <id> <--name NAME> [--desc DESC] [--tags +TAG|-TAG ...]
tt task rm <id ...> | --filter EXPR

tt time show
    [-s START | --start START]
    [-e END | --end END]
    [--filter EXPR]
    [--groupby KEY ...]
    [--format {pretty, with_task, json, yaml}]

tt time start [<task>] [-s START | --start START] [--note NOTE]
tt time stop [-e END | --end END] [--note NOTE]
tt time switch <task> [--note NOTE]
tt time resume [<task>] [--note NOTE]
tt time log [<task>] -s START | --start START -e END | --end END [--note NOTE]
tt time edit <entry-id> [-s START | --start START] [-e END | --end END] [--note NOTE]
tt time list [-s START | --start START] [-e END | --end END] [--filter EXPR]
tt time status
```
