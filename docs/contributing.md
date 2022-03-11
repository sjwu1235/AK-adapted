# information-retrieval :: Contributing

## Naming conventions

### GIT Branch Names

Combine the Jira ticket id and a shorted version of the ticket title and underscore it all:

`<JIRA_TICKET_ID>_<SHORTENED-JIRA-TICKET-NAME>`

So if the Jira ticket is:

`FB-714: MOB: refactor updateUserUsernameEpic to catch errors thrown by util`

then the branch should be named:

`FB-714_catch-util-errors-in-updateUserUsernameEpic`

shortest possible version that still describes the ticket.

### GIT Story Branch Names

If the Jira ticket is:

`FB-700: As a user I should see my things listed on the home page`

then the branch should be named:

`FB-700_user-can-see-things-on-home`

shortest possible version that still describes the ticket.

### GIT Commit Messages

We are using [conventional commit messages](https://www.conventionalcommits.org/en/v1.0.0-beta.4/).

please read through the guide at the above link and make sure that you are adhering to the standard outlined above.

[commitlint](https://commitlint.js.org/#/) is used to enforce this standard via a husky hook, so if you do not structure your commit message using the format mentioned above, it will fail.

### Branches, PRs & Merging

If a task belongs to a story that deserves a story branch then:

1. Create a story branch
2. Push the story branch and add protection rules to it on Github
3. Branch your task branch from the story branch
4. Create a Pull Request onto the story branch
5. Request a Peer Review
6. Once approved, squash merge into the story branch
7. Once all the sub task branches are merged into the story branch, create a Pull Request onto develop
8. Request a Peer Review
9. Once approved, squash merge into develop

If a task does not belong to a story branch:

1. Branch your task branch from develop
2. Create a Pull Request onto the develop
3. Request a Peer Review
4. Once approved, squash merge into develop
