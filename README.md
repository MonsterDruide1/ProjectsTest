# OdysseyDecomp Progress Tracking

This repo is used as an issue tracker and claiming system for [OdysseyDecomp](https://github.com/MonsterDruide1/OdysseyDecomp). Visit the [issues](https://github.com/MonsterDruide1/ProjectsTest/issues) and [project board](https://github.com/users/MonsterDruide1/projects/1).

## Workflow

1. Pick a class you want to decompile, or ask for someone to suggest something on our [Discord](https://discord.gg/u2dfaQpDh5).
2. Search for the corresponding issue to check its current progress and difficulty. Keep in mind that GitHub's search cannot find words from the middle of a word, so make sure you include the start of the filename. Make sure it's not assigned to anyone else so far. Check the comments so far to see if anyone already did some work on it.
3. If you're happy with taking it, comment `/claim` to assign yourself to the issue.
4. Decompile the file you've picked according to the [Contribution Guide](https://github.com/MonsterDruide1/OdysseyDecomp/blob/master/Contributing.md).
5. Create a PR on `OdysseyDecomp` to add your code into the repo. Reference the issue from this repo in the description.
6. Once it's merged, the issue will be closed automatically!

If you're stuck with something on the file:
- Ask for help on our [Discord](https://discord.gg/u2dfaQpDh5) server.
- If it cannot be solved quick enough, add the `help wanted` label to your issue by commenting `/help`
- If you want to stop working on it for a while and eventually plan to come back, add the `/stale` label
- If you give up on the file, use `/unclaim` to remove your assignment. Add a comment with all information that could be helpful for the next person taking on this file, possibly link to your unfinished branch (make sure you don't delete it later though!) or attach some code snippets to explain the situation or provide a head start.

## List of commands

Command    | Alias     | Effect
-----------|-----------|--------
/claim     | /assign   | Assign the issue to yourself
/unclaim   | /unassign | Remove your assignment from the issue
/help      |           | Add ![help wanted](https://img.shields.io/github/labels/MonsterDruide1/ProjectsTest/help%20wanted?link=https%3A%2F%2Fgithub.com%2FMonsterDruide1%2FProjectsTest%2Flabels%2Fhelp%2520wanted) label
/unhelp    | /thanks   | Remove ![help wanted](https://img.shields.io/github/labels/MonsterDruide1/ProjectsTest/help%20wanted?link=https%3A%2F%2Fgithub.com%2FMonsterDruide1%2FProjectsTest%2Flabels%2Fhelp%2520wanted) label
/stale     |           | Add ![stale](https://img.shields.io/github/labels/MonsterDruide1/ProjectsTest/stale?link=https%3A%2F%2Fgithub.com%2FMonsterDruide1%2FProjectsTest%2Flabels%2Fstale) labelcom%2FMonsterDruide1%2FProjectsTest%2Flabels%2Fstale) label
/unhelp    |           | Remove ![stale](https://img.shields.io/github/labels/MonsterDruide1/ProjectsTest/stale?link=https%3A%2F%2Fgithub.com%2FMonsterDruide1%2FProjectsTest%2Flabels%2Fstale) label
/request   |           | Add https://github.com/MonsterDruide1/ProjectsTest/labels/requested label
/unrequest |           | Remove https://github.com/MonsterDruide1/ProjectsTest/labels/requested label

## Future Ideas
- trigger full sync when new commit on OdysseyDecomp:master is detected
    - https://www.reddit.com/r/github/comments/1dikiqw/is_it_possible_to_trigger_actions_in_another_repo/
- add command to allow linking WIP branch that shows up in issue body, not only in comment below
    - as GitHub application, authenticate as user, then create new branch based on existing one, delete original, then "create linked branch" to the old name, finally delete temporary branch
- labels for "parts" of the game (at least separating al from rs)
