## Result
I fixed the login error. The unit tests pass. I did not run the end-to-end tests.

## Details
- The error occurred because the session token expired before the redirect.
- I changed `auth/session.ts` to refresh the token before the redirect.
- I added 2 unit tests in `auth/session.test.ts`.

## Steps
1. Pull the branch `fix/login-refresh`.
2. Run `npm test`.
3. If a test fails, send the log to me.

## Open items
- The end-to-end tests may find a different error. I did not run them.
