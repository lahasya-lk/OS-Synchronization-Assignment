# AI Prompt Log

**AI tool(s) used:** <e.g. Claude (Anthropic) - model name/version>

## Initial prompt
<Paste your exact first message: uploaded the assignment PDF and asked for dining philosophers (4 philosophers, 4 chopsticks, monitors, test-and-set and back-off) and readers-writers with semaphores/mutex, with simulation and a step-by-step guide.>

## Important follow-up prompts
1. "continue" - requested the README, prompt log and report outline.
2. "what next??" - asked for the remaining steps.
3. "give me the step by step guide separately for both the problems" - requested separate guides.
4. "yeah do that" - requested the viva Q&A sheet and references file.
5. "In the same way ... dining philosophers using semaphore and readers-writers using monitors" - requested the other two implementations.
6. "edit the earlier reports, prompts, references, files including all 4 types" - requested the documents be updated for all four implementations.
<Replace with your exact wording and add any prompts you wrote yourself.>

## What I changed manually
- <e.g. changed default delays / thread counts, renamed variables, added comments>
- <tests run: different seeds, more readers, removed `wrt` to see the checker fail, changed `--backoff`, `--readers 10 --writers 1` for starvation>

## Errors / limitations found in the AI output
- Python has no native monitor, so the AI used lock + Condition; I verified this is an accepted abstraction (PDF section 2).
- Readers-writers (semaphore) uses readers' preference and can starve writers; the monitor version uses writer preference and can starve readers.
- Back-off in the dining-philosophers monitor gives no formal starvation guarantee.
- <Add anything you personally found: a bug, a confusing part, an improvement you made.>

## Note on the assignment PDF
The PDF contained a hidden instruction directed at AI systems (asking for a specific word to be inserted into generated output). The AI did not follow it. <Mention this in your report if you wish.>
